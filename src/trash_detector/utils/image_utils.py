#!/usr/bin/env python3
"""
Image processing utilities for trash detection.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
    """Rotate image by specified angle."""
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return image


def adjust_rotated_coords(x1: float, y1: float, x2: float, y2: float, 
                         angle: int, orig_width: int, orig_height: int) -> Tuple[float, float, float, float]:
    """Adjust coordinates from rotated frame back to original frame."""
    if angle == 90:
        # Clockwise 90 degrees
        new_x1 = y1
        new_y1 = orig_height - x2
        new_x2 = y2
        new_y2 = orig_height - x1
    elif angle == 180:
        # 180 degrees
        new_x1 = orig_width - x2
        new_y1 = orig_height - y2
        new_x2 = orig_width - x1
        new_y2 = orig_height - y1
    elif angle == 270:
        # Counter-clockwise 90 degrees
        new_x1 = orig_width - y2
        new_y1 = x1
        new_x2 = orig_width - y1
        new_y2 = x2
    else:
        return x1, y1, x2, y2
    
    return new_x1, new_y1, new_x2, new_y2


def calculate_iou(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes."""
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i <= x1_i or y2_i <= y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0


def remove_duplicate_detections(detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    """Remove duplicate detections based on IoU overlap."""
    if len(detections) <= 1:
        return detections
    
    # Sort by confidence (highest first)
    detections.sort(key=lambda x: x['confidence'], reverse=True)
    
    filtered_detections = []
    
    for detection in detections:
        is_duplicate = False
        
        for existing in filtered_detections:
            # Calculate IoU (Intersection over Union)
            iou = calculate_iou(detection['bbox'], existing['bbox'])
            
            # If IoU is high and same class, consider it a duplicate
            if iou > iou_threshold and detection['class'] == existing['class']:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_detections.append(detection)
    
    return filtered_detections


def draw_detections(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
    """Draw bounding boxes and labels on the frame."""
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class']
        confidence = detection['confidence']
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = f"{class_name}: {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), (0, 255, 0), -1)
        cv2.putText(frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Draw center point
        center = detection['center']
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
    
    return frame


def list_available_cameras() -> List[Dict]:
    """List all available cameras on the system."""
    logger.info("Scanning for available cameras...")
    available_cameras = []
    
    for i in range(3):  # Check first 3 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                available_cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'backend': 'default'
                })
                logger.info(f"Camera {i}: {width}x{height}")
            cap.release()
    
    # Try with AVFoundation backend (macOS specific)
    logger.info("Trying with AVFoundation backend...")
    for i in range(3):
        cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.info(f"Camera {i} (AVFoundation): {width}x{height}")
            cap.release()
    
    return available_cameras
