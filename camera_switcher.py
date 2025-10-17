#!/usr/bin/env python3
"""
Quick camera switcher for trash detection system.
"""

import sys
import os
import subprocess

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trash_detector import TrashDetector


def list_cameras():
    """List available cameras with descriptions."""
    detector = TrashDetector()
    cameras = detector.list_available_cameras()
    
    print("Available Cameras:")
    print("=" * 50)
    
    if not cameras:
        print("No cameras found!")
        return
    
    for cam in cameras:
        # Try to identify camera type based on resolution
        resolution = cam['resolution']
        if resolution == "1920x1080":
            camera_type = "📱 Phone Camera (likely)"
        elif resolution == "1280x720":
            camera_type = "💻 Computer Webcam (likely)"
        else:
            camera_type = "📹 Unknown Camera"
        
        print(f"Camera {cam['index']}: {resolution} - {camera_type}")


def run_with_camera(camera_index, collection_mode=False, location=None):
    """Run trash detection with specified camera."""
    cmd = ["python", "main.py", "--source", str(camera_index)]
    
    if collection_mode:
        cmd.append("--collection-mode")
        if location:
            cmd.extend(["--location", location])
    
    print(f"Starting trash detection with Camera {camera_index}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running detection: {e}")
    except KeyboardInterrupt:
        print("\nDetection stopped by user")


def main():
    """Main function for camera switcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Camera Switcher for Trash Detection')
    parser.add_argument('--list', action='store_true', help='List available cameras')
    parser.add_argument('--phone', action='store_true', help='Use phone camera (Camera 0)')
    parser.add_argument('--computer', action='store_true', help='Use computer webcam (Camera 1)')
    parser.add_argument('--camera', type=int, help='Use specific camera index')
    parser.add_argument('--collection', action='store_true', help='Enable collection mode')
    parser.add_argument('--location', type=str, help='Location for collection mode')
    
    args = parser.parse_args()
    
    if args.list:
        list_cameras()
        return
    
    camera_index = None
    
    if args.phone:
        camera_index = 0
    elif args.computer:
        camera_index = 1
    elif args.camera is not None:
        camera_index = args.camera
    else:
        # Interactive mode
        list_cameras()
        print()
        try:
            camera_index = int(input("Enter camera index to use: "))
        except (ValueError, KeyboardInterrupt):
            print("Invalid input or cancelled")
            return
    
    run_with_camera(camera_index, args.collection, args.location)


if __name__ == "__main__":
    main()
