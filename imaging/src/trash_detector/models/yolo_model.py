#!/usr/bin/env python3
"""
YOLO model handler for trash detection.
"""

import logging
from typing import List, Dict, Optional
import numpy as np
from ..config import TRASH_CLASSES, DEFAULT_MODEL_PATH, ROTATION_ANGLES, ROTATION_PENALTY
from ..utils.image_utils import rotate_image, adjust_rotated_coords, remove_duplicate_detections
from ..utils.detection_filters import is_likely_trash

logger = logging.getLogger(__name__)


class YOLOModel:
    """YOLO model handler for trash detection."""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """
        Initialize the YOLO model.
        
        Args:
            model_path: Path to model file (defaults to yolov8n.pt)
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model = None
        self.class_names = TRASH_CLASSES
        
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded successfully from {self.model_path}")
            
        except ImportError:
            logger.error("ultralytics not installed. Please install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect_trash(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect trash using YOLO model with rotation and partial view handling.
        """
        if self.model is None:
            logger.warning("No model loaded, returning empty detections")
            return []
        
        try:
            # Run inference on original frame
            results = self.model(frame, verbose=False)
            detections = self._process_detections(results, frame)
            
            # Run inference on rotated frames for better detection
            rotated_detections = self._detect_rotated_objects(frame)
            detections.extend(rotated_detections)
            
            # Remove duplicate detections (same object detected multiple times)
            detections = remove_duplicate_detections(detections)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during YOLO detection: {e}")
            return []
    
    def _process_detections(self, results, frame: np.ndarray) -> List[Dict]:
        """Process YOLO detection results."""
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name from COCO dataset
                    class_name = self.model.names[class_id]
                    
                    # Only include classes that are considered trash
                    if class_name in self.class_names and confidence > self.confidence_threshold:
                        # Additional filtering for better trash detection
                        if is_likely_trash(class_name, confidence, x1, y1, x2, y2, frame):
                            detections.append({
                                'class': class_name,
                                'confidence': float(confidence),
                                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                                'center': (int((x1 + x2) // 2), int((y1 + y2) // 2)),
                                'rotation': 0  # Original orientation
                            })
        
        return detections
    
    def _detect_rotated_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in rotated frames to handle rotation issues."""
        detections = []
        
        for angle in ROTATION_ANGLES:
            try:
                # Rotate the frame
                rotated_frame = rotate_image(frame, angle)
                
                # Run inference on rotated frame
                results = self.model(rotated_frame, verbose=False)
                
                # Process detections and adjust coordinates back to original frame
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            class_id = int(box.cls[0].cpu().numpy())
                            class_name = self.model.names[class_id]
                            
                            if class_name in self.class_names and confidence > self.confidence_threshold:
                                # Adjust coordinates back to original frame
                                adj_x1, adj_y1, adj_x2, adj_y2 = adjust_rotated_coords(
                                    x1, y1, x2, y2, angle, frame.shape[1], frame.shape[0]
                                )
                                
                                if is_likely_trash(class_name, confidence, adj_x1, adj_y1, adj_x2, adj_y2, frame):
                                    detections.append({
                                        'class': class_name,
                                        'confidence': float(confidence * ROTATION_PENALTY),  # Slight penalty for rotated detection
                                        'bbox': (int(adj_x1), int(adj_y1), int(adj_x2), int(adj_y2)),
                                        'center': (int((adj_x1 + adj_x2) // 2), int((adj_y1 + adj_y2) // 2)),
                                        'rotation': angle
                                    })
            except Exception as e:
                logger.warning(f"Error processing rotation {angle}: {e}")
                continue
        
        return detections
