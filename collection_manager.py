#!/usr/bin/env python3
"""
Collection Manager CLI tool for managing trash collection data.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trash_detector import TrashCollector


def main():
    """Main function for the collection manager CLI."""
    parser = argparse.ArgumentParser(description='Trash Collection Manager')
    parser.add_argument('--data-dir', type=str, default='collection_data',
                       help='Directory containing collection data')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List sessions command
    list_parser = subparsers.add_parser('list', help='List all collection sessions')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                           help='Output format')
    
    # Show session details command
    show_parser = subparsers.add_parser('show', help='Show details of a specific session')
    show_parser.add_argument('session_id', help='Session ID to show')
    show_parser.add_argument('--format', choices=['table', 'json'], default='table',
                           help='Output format')
    
    # Export session command
    export_parser = subparsers.add_parser('export', help='Export session data')
    export_parser.add_argument('session_id', help='Session ID to export')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                             help='Export format')
    export_parser.add_argument('--output', type=str, help='Output file path')
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show collection statistics')
    stats_parser.add_argument('--format', choices=['table', 'json'], default='table',
                            help='Output format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize collector
    collector = TrashCollector(args.data_dir)
    
    if args.command == 'list':
        list_sessions(collector, args.format)
    elif args.command == 'show':
        show_session(collector, args.session_id, args.format)
    elif args.command == 'export':
        export_session(collector, args.session_id, args.format, args.output)
    elif args.command == 'stats':
        show_statistics(collector, args.format)


def list_sessions(collector: TrashCollector, format: str):
    """List all collection sessions."""
    history = collector.get_collection_history()
    
    if format == 'json':
        print(json.dumps(history, indent=2, default=str))
    else:
        if not history:
            print("No collection sessions found.")
            return
        
        print(f"{'Session ID':<20} {'Start Time':<20} {'Duration':<10} {'Items':<8} {'Collected':<10} {'Rate':<8}")
        print("-" * 80)
        
        for session in history:
            duration = f"{session['duration_minutes']:.1f}m" if session['duration_minutes'] else "N/A"
            rate = f"{session['collection_rate']:.1%}" if session['collection_rate'] else "N/A"
            start_time = session['start_time'][:19] if session['start_time'] else "N/A"
            
            print(f"{session['session_id']:<20} {start_time:<20} {duration:<10} "
                  f"{session['total_items']:<8} {session['collected_items']:<10} {rate:<8}")


def show_session(collector: TrashCollector, session_id: str, format: str):
    """Show details of a specific session."""
    stats = collector.get_session_statistics(session_id)
    
    if not stats:
        print(f"Session {session_id} not found.")
        return
    
    if format == 'json':
        print(json.dumps(stats, indent=2, default=str))
    else:
        print(f"Session: {stats['session_id']}")
        print(f"Start Time: {stats['start_time']}")
        print(f"End Time: {stats['end_time'] or 'N/A'}")
        print(f"Duration: {stats['duration_minutes']:.1f} minutes" if stats['duration_minutes'] else "Duration: N/A")
        print(f"Total Items: {stats['total_items']}")
        print(f"Collected Items: {stats['collected_items']}")
        print(f"Collection Rate: {stats['collection_rate']:.1%}")
        print()
        
        print("Items by Class:")
        for class_name, count in stats['items_by_class'].items():
            collected = stats['collected_by_class'].get(class_name, 0)
            print(f"  {class_name}: {count} total, {collected} collected")


def export_session(collector: TrashCollector, session_id: str, format: str, output: str = None):
    """Export session data."""
    file_path = collector.export_session_data(session_id, format)
    
    if file_path:
        if output:
            import shutil
            shutil.move(file_path, output)
            print(f"Session data exported to: {output}")
        else:
            print(f"Session data exported to: {file_path}")
    else:
        print(f"Failed to export session {session_id}")


def show_statistics(collector: TrashCollector, format: str):
    """Show overall collection statistics."""
    history = collector.get_collection_history()
    
    if not history:
        print("No collection data available.")
        return
    
    # Calculate overall statistics
    total_sessions = len(history)
    total_items = sum(session['total_items'] for session in history)
    total_collected = sum(session['collected_items'] for session in history)
    overall_rate = total_collected / total_items if total_items > 0 else 0
    
    # Calculate class statistics
    all_class_counts = {}
    all_collected_counts = {}
    
    for session in history:
        for class_name, count in session['items_by_class'].items():
            all_class_counts[class_name] = all_class_counts.get(class_name, 0) + count
            collected = session['collected_by_class'].get(class_name, 0)
            all_collected_counts[class_name] = all_collected_counts.get(class_name, 0) + collected
    
    stats = {
        'total_sessions': total_sessions,
        'total_items_detected': total_items,
        'total_items_collected': total_collected,
        'overall_collection_rate': overall_rate,
        'items_by_class': all_class_counts,
        'collected_by_class': all_collected_counts
    }
    
    if format == 'json':
        print(json.dumps(stats, indent=2, default=str))
    else:
        print("Collection Statistics")
        print("=" * 50)
        print(f"Total Sessions: {total_sessions}")
        print(f"Total Items Detected: {total_items}")
        print(f"Total Items Collected: {total_collected}")
        print(f"Overall Collection Rate: {overall_rate:.1%}")
        print()
        
        print("Items by Class:")
        for class_name in sorted(all_class_counts.keys()):
            total = all_class_counts[class_name]
            collected = all_collected_counts.get(class_name, 0)
            rate = collected / total if total > 0 else 0
            print(f"  {class_name}: {total} total, {collected} collected ({rate:.1%})")


if __name__ == "__main__":
    main()
