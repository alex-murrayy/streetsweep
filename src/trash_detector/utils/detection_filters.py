#!/usr/bin/env python3
"""
Detection filtering utilities for trash detection.
"""

import numpy as np
from typing import Dict
from ..config import DETECTION_FILTERS


def is_likely_trash(class_name: str, confidence: float, x1: float, y1: float, 
                   x2: float, y2: float, frame: np.ndarray) -> bool:
    """
    Additional filtering to determine if a detection is likely trash.
    """
    # Calculate bounding box dimensions
    width = x2 - x1
    height = y2 - y1
    area = width * height
    frame_area = frame.shape[0] * frame.shape[1]
    relative_area = area / frame_area
    
    # Get filter parameters for this class
    filter_params = DETECTION_FILTERS.get(class_name, DETECTION_FILTERS['default'])
    
    min_area = filter_params['min_area']
    max_area = filter_params['max_area']
    min_confidence = filter_params['min_confidence']
    
    return min_area < relative_area < max_area and confidence > min_confidence


def filter_detections_by_size_and_confidence(detections: list, frame: np.ndarray) -> list:
    """
    Filter detections based on size and confidence thresholds.
    """
    filtered = []
    
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class']
        confidence = detection['confidence']
        
        if is_likely_trash(class_name, confidence, x1, y1, x2, y2, frame):
            filtered.append(detection)
    
    return filtered
