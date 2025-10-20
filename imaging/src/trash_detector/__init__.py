#!/usr/bin/env python3
"""
Trash Detection System Package

A computer vision-based trash detection system that can identify and classify
various types of litter from video feeds.
"""

from .detector import TrashDetector
from .collection.trash_collector import TrashCollector, TrashItem, CollectionSession
from .config import TRASH_CLASSES, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_CAMERA_INDEX

__version__ = "1.0.0"
__author__ = "CleanSweep Project"

__all__ = [
    'TrashDetector',
    'TrashCollector', 
    'TrashItem',
    'CollectionSession',
    'TRASH_CLASSES',
    'DEFAULT_CONFIDENCE_THRESHOLD',
    'DEFAULT_CAMERA_INDEX'
]
