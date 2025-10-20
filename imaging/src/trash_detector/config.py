#!/usr/bin/env python3
"""
Configuration and constants for the trash detection system.
"""

from typing import List

# Trash classes that are commonly considered litter
TRASH_CLASSES: List[str] = [
    'bottle',      # Plastic/glass bottles - very common litter
    'cup',         # Disposable cups - common litter
    'bowl',        # Disposable bowls - common litter
    'banana',      # Food waste - common litter
    'apple',       # Food waste - common litter
    'sandwich',    # Food waste - common litter
    'orange',      # Food waste - common litter
    'broccoli',    # Food waste - common litter
    'carrot',      # Food waste - common litter
    'hot dog',     # Food waste - common litter
    'pizza',       # Food waste - common litter
    'donut',       # Food waste - common litter
    'cake',        # Food waste - common litter
    'book',        # Paper waste - common litter
    'frisbee',     # Toys/sports equipment - common litter
    'sports ball', # Sports equipment - common litter
    'tennis racket', # Sports equipment - common litter
    'skateboard',  # Sports equipment - common litter
    'surfboard',   # Sports equipment - common litter
    'wine glass',  # Glass containers - common litter
    'fork',        # Utensils - common litter
    'knife',       # Utensils - common litter
    'spoon',       # Utensils - common litter
    'tie',         # Clothing items - common litter
    'handbag',     # Personal items - common litter
    'suitcase',    # Personal items - common litter
    'umbrella',    # Personal items - common litter
    'backpack',    # Personal items - common litter
    'chair',       # Furniture - common litter (abandoned)
    'couch',       # Furniture - common litter (abandoned)
    'potted plant', # Plants - common litter (abandoned)
    'bed',         # Furniture - common litter (abandoned)
    'dining table', # Furniture - common litter (abandoned)
    'toilet',      # Large items - common litter (abandoned)
]

# Default model path
DEFAULT_MODEL_PATH = 'yolov8n.pt'

# Default confidence threshold
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Default camera index (1 for computer webcam, 0 for phone camera)
DEFAULT_CAMERA_INDEX = 0  # Changed to phone camera

# Detection filtering parameters
DETECTION_FILTERS = {
    'bottle': {'min_area': 0.0005, 'max_area': 0.2, 'min_confidence': 0.3},
    'cup': {'min_area': 0.001, 'max_area': 0.15, 'min_confidence': 0.3},
    'bowl': {'min_area': 0.001, 'max_area': 0.15, 'min_confidence': 0.3},
    'wine glass': {'min_area': 0.001, 'max_area': 0.15, 'min_confidence': 0.3},
    'banana': {'min_area': 0.0005, 'max_area': 0.1, 'min_confidence': 0.4},
    'apple': {'min_area': 0.0005, 'max_area': 0.1, 'min_confidence': 0.4},
    'orange': {'min_area': 0.0005, 'max_area': 0.1, 'min_confidence': 0.4},
    'broccoli': {'min_area': 0.0005, 'max_area': 0.1, 'min_confidence': 0.4},
    'carrot': {'min_area': 0.0005, 'max_area': 0.1, 'min_confidence': 0.4},
    'sandwich': {'min_area': 0.001, 'max_area': 0.1, 'min_confidence': 0.4},
    'hot dog': {'min_area': 0.001, 'max_area': 0.1, 'min_confidence': 0.4},
    'pizza': {'min_area': 0.001, 'max_area': 0.1, 'min_confidence': 0.4},
    'donut': {'min_area': 0.001, 'max_area': 0.1, 'min_confidence': 0.4},
    'cake': {'min_area': 0.001, 'max_area': 0.1, 'min_confidence': 0.4},
    'book': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.5},
    'frisbee': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.4},
    'sports ball': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.4},
    'tennis racket': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.4},
    'skateboard': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.4},
    'surfboard': {'min_area': 0.002, 'max_area': 0.2, 'min_confidence': 0.4},
    'fork': {'min_area': 0.0005, 'max_area': 0.05, 'min_confidence': 0.4},
    'knife': {'min_area': 0.0005, 'max_area': 0.05, 'min_confidence': 0.4},
    'spoon': {'min_area': 0.0005, 'max_area': 0.05, 'min_confidence': 0.4},
    'tie': {'min_area': 0.002, 'max_area': 0.15, 'min_confidence': 0.5},
    'handbag': {'min_area': 0.002, 'max_area': 0.15, 'min_confidence': 0.5},
    'suitcase': {'min_area': 0.002, 'max_area': 0.15, 'min_confidence': 0.5},
    'umbrella': {'min_area': 0.002, 'max_area': 0.15, 'min_confidence': 0.5},
    'backpack': {'min_area': 0.002, 'max_area': 0.15, 'min_confidence': 0.5},
    'chair': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'couch': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'potted plant': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'bed': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'dining table': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'toilet': {'min_area': 0.01, 'max_area': 0.5, 'min_confidence': 0.6},
    'default': {'min_area': 0.0005, 'max_area': 0.2, 'min_confidence': 0.3}
}

# Rotation angles for multi-angle detection
ROTATION_ANGLES = [90, 180, 270]

# IoU threshold for duplicate detection removal
IOU_THRESHOLD = 0.5

# Confidence penalty for rotated detections
ROTATION_PENALTY = 0.9
