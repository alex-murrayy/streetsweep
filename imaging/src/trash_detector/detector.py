#!/usr/bin/env python3
"""
Main TrashDetector class for the trash detection system.
"""

import cv2
import numpy as np
import time
import logging
from typing import List, Dict, Optional

from .models.yolo_model import YOLOModel
from .models.advanced_detector import AdvancedTrashDetector
from .utils.image_utils import draw_detections, list_available_cameras

logger = logging.getLogger(__name__)


class TrashDetector:
    """
    A computer vision-based trash detection system that can identify and classify
    various types of litter from video feeds.
    """
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5, use_advanced: bool = False):
        """
        Initialize the trash detector.
        
        Args:
            model_path: Path to pre-trained model (optional)
            confidence_threshold: Minimum confidence for detections
            use_advanced: Use advanced multi-model detector for better accuracy
        """
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.use_advanced = use_advanced
        
        # Initialize detector
        if use_advanced:
            self.model = AdvancedTrashDetector(confidence_threshold=confidence_threshold)
        else:
            self.model = YOLOModel(model_path=model_path, confidence_threshold=confidence_threshold)
    
    def detect_trash(self, frame: np.ndarray) -> List[Dict]:
        """
        Main detection method using YOLO.
        """
        return self.model.detect_trash(frame)
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the frame.
        """
        return draw_detections(frame, detections)
    
    def list_available_cameras(self) -> List[Dict]:
        """List all available cameras on the system."""
        return list_available_cameras()
    
    def process_video(self, video_source: str = 0, output_path: Optional[str] = None):
        """
        Process video feed for trash detection.
        
        Args:
            video_source: Video file path or camera index (0 for webcam)
            output_path: Optional path to save output video
        """
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
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Detect trash in current frame
                detections = self.detect_trash(frame)
                
                # Draw detections on frame
                frame_with_detections = self.draw_detections(frame.copy(), detections)
                
                # Add frame info
                info_text = f"Frame: {frame_count} | Detections: {len(detections)} | FPS: {fps}"
                cv2.putText(frame_with_detections, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Trash Detection', frame_with_detections)
                
                # Save frame if writer is available
                if writer:
                    writer.write(frame_with_detections)
                
                # Log detection results
                if detections:
                    logger.info(f"Frame {frame_count}: Found {len(detections)} trash items")
                    for det in detections:
                        logger.info(f"  - {det['class']}: {det['confidence']:.2f} at {det['center']}")
                
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
