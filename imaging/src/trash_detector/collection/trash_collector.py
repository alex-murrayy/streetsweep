#!/usr/bin/env python3
"""
Trash collection logic and management system.
"""

import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TrashItem:
    """Represents a detected trash item."""
    class_name: str
    confidence: float
    bbox: tuple
    center: tuple
    timestamp: datetime
    location: Optional[str] = None
    collected: bool = False
    collection_timestamp: Optional[datetime] = None


@dataclass
class CollectionSession:
    """Represents a trash collection session."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_items: int = 0
    collected_items: int = 0
    items: List[TrashItem] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


class TrashCollector:
    """Manages trash collection sessions and data."""
    
    def __init__(self, data_dir: str = "collection_data"):
        """
        Initialize the trash collector.
        
        Args:
            data_dir: Directory to store collection data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.current_session: Optional[CollectionSession] = None
        self.collection_history: List[CollectionSession] = []
        
        # Load existing collection history
        self._load_collection_history()
    
    def start_collection_session(self, location: Optional[str] = None) -> str:
        """
        Start a new collection session.
        
        Args:
            location: Optional location description
            
        Returns:
            Session ID
        """
        session_id = f"session_{int(time.time())}"
        self.current_session = CollectionSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        logger.info(f"Started collection session: {session_id}")
        return session_id
    
    def end_collection_session(self) -> Optional[CollectionSession]:
        """
        End the current collection session.
        
        Returns:
            The completed session or None if no active session
        """
        if self.current_session is None:
            logger.warning("No active collection session to end")
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.total_items = len(self.current_session.items)
        self.current_session.collected_items = sum(1 for item in self.current_session.items if item.collected)
        
        # Save session data
        self._save_session(self.current_session)
        
        # Add to history
        self.collection_history.append(self.current_session)
        
        logger.info(f"Ended collection session: {self.current_session.session_id}")
        logger.info(f"Total items detected: {self.current_session.total_items}")
        logger.info(f"Items collected: {self.current_session.collected_items}")
        
        completed_session = self.current_session
        self.current_session = None
        return completed_session
    
    def add_detection(self, detection: Dict, location: Optional[str] = None) -> TrashItem:
        """
        Add a detected trash item to the current session.
        
        Args:
            detection: Detection dictionary from the detector
            location: Optional location description
            
        Returns:
            Created TrashItem
        """
        if self.current_session is None:
            logger.warning("No active collection session. Starting new session.")
            self.start_collection_session()
        
        trash_item = TrashItem(
            class_name=detection['class'],
            confidence=detection['confidence'],
            bbox=detection['bbox'],
            center=detection['center'],
            timestamp=datetime.now(),
            location=location
        )
        
        self.current_session.items.append(trash_item)
        logger.debug(f"Added detection: {trash_item.class_name} at {trash_item.center}")
        
        return trash_item
    
    def mark_item_collected(self, item: TrashItem) -> bool:
        """
        Mark a trash item as collected.
        
        Args:
            item: TrashItem to mark as collected
            
        Returns:
            True if successfully marked, False otherwise
        """
        if self.current_session is None:
            logger.warning("No active collection session")
            return False
        
        if item in self.current_session.items:
            item.collected = True
            item.collection_timestamp = datetime.now()
            logger.info(f"Marked item as collected: {item.class_name}")
            return True
        
        logger.warning("Item not found in current session")
        return False
    
    def get_session_statistics(self, session_id: Optional[str] = None) -> Dict:
        """
        Get statistics for a session or the current session.
        
        Args:
            session_id: Session ID (None for current session)
            
        Returns:
            Statistics dictionary
        """
        if session_id is None:
            session = self.current_session
        else:
            session = next((s for s in self.collection_history if s.session_id == session_id), None)
        
        if session is None:
            return {}
        
        # Count items by class
        class_counts = {}
        collected_by_class = {}
        
        for item in session.items:
            class_counts[item.class_name] = class_counts.get(item.class_name, 0) + 1
            if item.collected:
                collected_by_class[item.class_name] = collected_by_class.get(item.class_name, 0) + 1
        
        return {
            'session_id': session.session_id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'total_items': session.total_items,
            'collected_items': session.collected_items,
            'collection_rate': session.collected_items / session.total_items if session.total_items > 0 else 0,
            'items_by_class': class_counts,
            'collected_by_class': collected_by_class,
            'duration_minutes': (session.end_time - session.start_time).total_seconds() / 60 if session.end_time else None
        }
    
    def get_collection_history(self) -> List[Dict]:
        """
        Get collection history for all sessions.
        
        Returns:
            List of session statistics
        """
        return [self.get_session_statistics(session.session_id) for session in self.collection_history]
    
    def export_session_data(self, session_id: str, format: str = 'json') -> Optional[str]:
        """
        Export session data to a file.
        
        Args:
            session_id: Session ID to export
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to exported file or None if failed
        """
        session = next((s for s in self.collection_history if s.session_id == session_id), None)
        if session is None:
            logger.error(f"Session {session_id} not found")
            return None
        
        if format == 'json':
            file_path = self.data_dir / f"{session_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(session), f, indent=2, default=str)
        elif format == 'csv':
            file_path = self.data_dir / f"{session_id}.csv"
            import csv
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['class_name', 'confidence', 'bbox', 'center', 'timestamp', 'location', 'collected', 'collection_timestamp'])
                for item in session.items:
                    writer.writerow([
                        item.class_name,
                        item.confidence,
                        str(item.bbox),
                        str(item.center),
                        item.timestamp.isoformat(),
                        item.location or '',
                        item.collected,
                        item.collection_timestamp.isoformat() if item.collection_timestamp else ''
                    ])
        else:
            logger.error(f"Unsupported format: {format}")
            return None
        
        logger.info(f"Exported session data to: {file_path}")
        return str(file_path)
    
    def _save_session(self, session: CollectionSession):
        """Save session data to disk."""
        file_path = self.data_dir / f"{session.session_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(session), f, indent=2, default=str)
    
    def _load_collection_history(self):
        """Load existing collection history from disk."""
        for file_path in self.data_dir.glob("session_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Convert timestamps back to datetime objects
                data['start_time'] = datetime.fromisoformat(data['start_time'])
                if data['end_time']:
                    data['end_time'] = datetime.fromisoformat(data['end_time'])
                
                for item_data in data['items']:
                    item_data['timestamp'] = datetime.fromisoformat(item_data['timestamp'])
                    if item_data['collection_timestamp']:
                        item_data['collection_timestamp'] = datetime.fromisoformat(item_data['collection_timestamp'])
                
                session = CollectionSession(**data)
                self.collection_history.append(session)
                
            except Exception as e:
                logger.error(f"Failed to load session from {file_path}: {e}")
        
        logger.info(f"Loaded {len(self.collection_history)} collection sessions from history")
