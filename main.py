#!/usr/bin/env python3
"""
Main entry point for the Trash Detection System.
"""

import sys
import os
import argparse
import logging
import numpy as np
import cv2

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trash_detector import TrashDetector, TrashCollector
from src.trash_detector.config import DEFAULT_CAMERA_INDEX

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main function to run the trash detection system."""
    parser = argparse.ArgumentParser(description='Trash Detection System')
    parser.add_argument('--source', type=str, default=str(DEFAULT_CAMERA_INDEX), 
                       help='Video source (file path or camera index, default: 1 for computer webcam)')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to trained model file')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Confidence threshold for detections (default: 0.5)')
    parser.add_argument('--advanced', action='store_true',
                       help='Use advanced multi-model detector (much better accuracy)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video file path (optional)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no camera required)')
    parser.add_argument('--list-cameras', action='store_true',
                       help='List all available cameras and exit')
    parser.add_argument('--collection-mode', action='store_true',
                       help='Enable collection mode to track detected trash items')
    parser.add_argument('--location', type=str, default=None,
                       help='Location description for collection mode')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize detector
    detector = TrashDetector(model_path=args.model, 
                           confidence_threshold=args.confidence,
                           use_advanced=args.advanced)
    
    # Initialize collector if in collection mode
    collector = None
    if args.collection_mode:
        collector = TrashCollector()
        session_id = collector.start_collection_session(args.location)
        logger.info(f"Collection mode enabled. Session ID: {session_id}")
    
    if args.list_cameras:
        # List available cameras and exit
        logger.info("Listing available cameras...")
        cameras = detector.list_available_cameras()
        if cameras:
            logger.info(f"Found {len(cameras)} available cameras:")
            for cam in cameras:
                logger.info(f"  Camera {cam['index']}: {cam['resolution']} ({cam['backend']})")
        else:
            logger.warning("No cameras found!")
        return
    
    if args.test:
        # Test mode - create a simple test image and run detection
        logger.info("Running in test mode...")
        
        # Create a test image with some colored rectangles (simulating trash)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some colored rectangles to simulate different types of trash
        cv2.rectangle(test_image, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue bottle
        cv2.rectangle(test_image, (300, 150), (400, 250), (0, 0, 255), -1)  # Red can
        cv2.rectangle(test_image, (150, 300), (300, 350), (255, 255, 255), -1)  # White paper
        
        # Run detection on test image
        detections = detector.detect_trash(test_image)
        logger.info(f"Test mode: Found {len(detections)} detections")
        
        # Add detections to collector if in collection mode
        if collector:
            for detection in detections:
                collector.add_detection(detection, "test_location")
        
        # Draw detections on test image
        result_image = detector.draw_detections(test_image.copy(), detections)
        
        # Display result
        cv2.imshow('Test Mode - Trash Detection', result_image)
        logger.info("Test image displayed. Press any key to exit...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # End collection session if active
        if collector:
            session = collector.end_collection_session()
            if session:
                stats = collector.get_session_statistics(session.session_id)
                logger.info(f"Collection session completed: {stats}")
        
        return
    
    # Convert source to int if it's a number
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    logger.info("Starting trash detection system...")
    logger.info(f"Video source: {video_source}")
    logger.info(f"Confidence threshold: {args.confidence}")
    if args.collection_mode:
        logger.info("Collection mode: ENABLED")
    
    try:
        # Process video with collection integration
        if collector:
            process_video_with_collection(detector, collector, video_source, args.output, args.location)
        else:
            detector.process_video(video_source=video_source, output_path=args.output)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    finally:
        # End collection session if active
        if collector:
            session = collector.end_collection_session()
            if session:
                stats = collector.get_session_statistics(session.session_id)
                logger.info(f"Collection session completed: {stats}")


def process_video_with_collection(detector: TrashDetector, collector: TrashCollector, 
                                 video_source, output_path: str = None, location: str = None):
    """
    Process video feed with collection tracking.
    """
    import cv2
    import time
    
    # Open video source
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        logger.error(f"Could not open video source: {video_source}")
        return
    
    # Try different backends for macOS compatibility
    if isinstance(video_source, int):
        logger.info("Trying different camera backends for macOS compatibility...")
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
        for backend in backends:
            cap.release()
            cap = cv2.VideoCapture(video_source, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    logger.info(f"Successfully opened camera with backend: {backend}")
                    break
                else:
                    logger.warning(f"Camera opened with backend {backend} but failed to read frame")
            else:
                logger.warning(f"Failed to open camera with backend: {backend}")
        
        if not cap.isOpened():
            logger.error("Could not open camera with any backend")
            return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video properties: {width}x{height} @ {fps} FPS")
    
    # Setup video writer if output path provided
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    start_time = time.time()
    last_stats_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect trash in current frame
            detections = detector.detect_trash(frame)
            
            # Add detections to collector
            for detection in detections:
                collector.add_detection(detection, location)
            
            # Draw detections on frame
            frame_with_detections = detector.draw_detections(frame.copy(), detections)
            
            # Add frame info
            info_text = f"Frame: {frame_count} | Detections: {len(detections)} | FPS: {fps}"
            cv2.putText(frame_with_detections, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add collection stats
            if collector.current_session:
                stats = collector.get_session_statistics()
                collection_text = f"Session: {stats.get('total_items', 0)} items | Collected: {stats.get('collected_items', 0)}"
                cv2.putText(frame_with_detections, collection_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Trash Detection - Collection Mode', frame_with_detections)
            
            # Save frame if writer is available
            if writer:
                writer.write(frame_with_detections)
            
            # Log detection results
            if detections:
                logger.info(f"Frame {frame_count}: Found {len(detections)} trash items")
                for det in detections:
                    logger.info(f"  - {det['class']}: {det['confidence']:.2f} at {det['center']}")
            
            # Log collection stats every 30 seconds
            current_time = time.time()
            if current_time - last_stats_time > 30:
                if collector.current_session:
                    stats = collector.get_session_statistics()
                    logger.info(f"Collection stats: {stats['total_items']} items detected, {stats['collected_items']} collected")
                last_stats_time = current_time
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Performance statistics
        elapsed_time = time.time() - start_time
        avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        logger.info(f"Processed {frame_count} frames in {elapsed_time:.2f}s (avg FPS: {avg_fps:.2f})")


if __name__ == "__main__":
    main()
