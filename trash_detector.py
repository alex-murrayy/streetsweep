#!/usr/bin/env python3
"""
Trash Detection System for CleanSweep Project
Detects and classifies various types of trash in real-time video feeds.
"""

import cv2
import numpy as np
import argparse
import time
from typing import List, Tuple, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrashDetector:
    """
    A computer vision-based trash detection system that can identify and classify
    various types of litter from video feeds.
    """
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        Initialize the trash detector.
        
        Args:
            model_path: Path to pre-trained model (optional)
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        
        # Initialize YOLO model
        self.model = None
        self.class_names = self._get_trash_classes()
        
        if model_path:
            self._load_custom_model()
        else:
            # Use YOLOv8 from ultralytics for better accuracy
            logger.info("No model path provided, using YOLOv8 for object detection")
            self._load_yolov8()
    
    def _get_trash_classes(self) -> List[str]:
        """Get COCO classes that are commonly considered trash/litter."""
        # Focus on items that are commonly littered
        trash_classes = [
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
        return trash_classes
    
    def _load_yolov8(self):
        """Load YOLOv8 model from ultralytics."""
        try:
            from ultralytics import YOLO
            # Load YOLOv8n (nano) model - lightweight and fast
            self.model = YOLO('yolov8n.pt')
            logger.info("YOLOv8 model loaded successfully")
            
        except ImportError:
            logger.error("ultralytics not installed. Please install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            self.model = None
    
    def _load_custom_model(self):
        """Load custom trained model for trash detection."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"Custom model loaded successfully from {self.model_path}")
            
        except ImportError:
            logger.error("ultralytics not installed. Please install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load custom model: {e}")
            self.model = None
    
    def detect_trash_yolo(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect trash using YOLOv8 model with rotation and partial view handling.
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
            detections = self._remove_duplicate_detections(detections)
            
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
                        if self._is_likely_trash(class_name, confidence, x1, y1, x2, y2, frame):
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
        
        # Rotate frame by 90, 180, and 270 degrees
        rotations = [90, 180, 270]
        
        for angle in rotations:
            try:
                # Rotate the frame
                rotated_frame = self._rotate_image(frame, angle)
                
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
                                adj_x1, adj_y1, adj_x2, adj_y2 = self._adjust_rotated_coords(
                                    x1, y1, x2, y2, angle, frame.shape[1], frame.shape[0]
                                )
                                
                                if self._is_likely_trash(class_name, confidence, adj_x1, adj_y1, adj_x2, adj_y2, frame):
                                    detections.append({
                                        'class': class_name,
                                        'confidence': float(confidence * 0.9),  # Slight penalty for rotated detection
                                        'bbox': (int(adj_x1), int(adj_y1), int(adj_x2), int(adj_y2)),
                                        'center': (int((adj_x1 + adj_x2) // 2), int((adj_y1 + adj_y2) // 2)),
                                        'rotation': angle
                                    })
            except Exception as e:
                logger.warning(f"Error processing rotation {angle}: {e}")
                continue
        
        return detections
    
    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by specified angle."""
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            return image
    
    def _adjust_rotated_coords(self, x1: float, y1: float, x2: float, y2: float, 
                              angle: int, orig_width: int, orig_height: int) -> tuple:
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
    
    def _remove_duplicate_detections(self, detections: List[Dict]) -> List[Dict]:
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
                iou = self._calculate_iou(detection['bbox'], existing['bbox'])
                
                # If IoU is high and same class, consider it a duplicate
                if iou > 0.5 and detection['class'] == existing['class']:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_detections.append(detection)
        
        return filtered_detections
    
    def _calculate_iou(self, bbox1: tuple, bbox2: tuple) -> float:
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
    
    def _is_likely_trash(self, class_name: str, confidence: float, x1: float, y1: float, x2: float, y2: float, frame: np.ndarray) -> bool:
        """
        Additional filtering to determine if a detection is likely trash.
        """
        # Calculate bounding box dimensions
        width = x2 - x1
        height = y2 - y1
        area = width * height
        frame_area = frame.shape[0] * frame.shape[1]
        relative_area = area / frame_area
        
        # More lenient filtering - focus on common litter items
        if class_name == 'bottle':
            # Bottles - very common litter, be more lenient
            return 0.0005 < relative_area < 0.2 and confidence > 0.3
        elif class_name in ['cup', 'bowl', 'wine glass']:
            # Cups and bowls - common litter
            return 0.001 < relative_area < 0.15 and confidence > 0.3
        elif class_name in ['banana', 'apple', 'orange', 'broccoli', 'carrot']:
            # Fruits and vegetables - common food waste
            return 0.0005 < relative_area < 0.1 and confidence > 0.4
        elif class_name in ['sandwich', 'hot dog', 'pizza', 'donut', 'cake']:
            # Food items - common food waste
            return 0.001 < relative_area < 0.1 and confidence > 0.4
        elif class_name == 'book':
            # Books - common paper waste
            return 0.002 < relative_area < 0.2 and confidence > 0.5
        elif class_name in ['frisbee', 'sports ball', 'tennis racket', 'skateboard', 'surfboard']:
            # Sports equipment - common litter
            return 0.002 < relative_area < 0.2 and confidence > 0.4
        elif class_name in ['fork', 'knife', 'spoon']:
            # Utensils - common litter
            return 0.0005 < relative_area < 0.05 and confidence > 0.4
        elif class_name in ['tie', 'handbag', 'suitcase', 'umbrella', 'backpack']:
            # Personal items - common litter
            return 0.002 < relative_area < 0.15 and confidence > 0.5
        elif class_name in ['chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet']:
            # Large items - usually abandoned, not typical small litter
            return 0.01 < relative_area < 0.5 and confidence > 0.6
        else:
            # Default filtering for other classes - be more lenient
            return 0.0005 < relative_area < 0.2 and confidence > 0.3
    
    def detect_trash(self, frame: np.ndarray) -> List[Dict]:
        """
        Main detection method using YOLOv8.
        """
        return self.detect_trash_yolo(frame)
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the frame.
        """
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
    
    def process_video(self, video_source: str = 0, output_path: str = None):
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


def main():
    """Main function to run the trash detection system."""
    parser = argparse.ArgumentParser(description='Trash Detection System')
    parser.add_argument('--source', type=str, default='0', 
                       help='Video source (file path or camera index, default: 0)')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to trained model file')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Confidence threshold for detections (default: 0.5)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video file path (optional)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no camera required)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize detector
    detector = TrashDetector(model_path=args.model, 
                           confidence_threshold=args.confidence)
    
    if args.test:
        # Test mode - create a simple test image and run detection
        logger.info("Running in test mode...")
        import numpy as np
        
        # Create a test image with some colored rectangles (simulating trash)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some colored rectangles to simulate different types of trash
        cv2.rectangle(test_image, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue bottle
        cv2.rectangle(test_image, (300, 150), (400, 250), (0, 0, 255), -1)  # Red can
        cv2.rectangle(test_image, (150, 300), (300, 350), (255, 255, 255), -1)  # White paper
        
        # Run detection on test image
        detections = detector.detect_trash(test_image)
        logger.info(f"Test mode: Found {len(detections)} detections")
        
        # Draw detections on test image
        result_image = detector.draw_detections(test_image.copy(), detections)
        
        # Display result
        cv2.imshow('Test Mode - Trash Detection', result_image)
        logger.info("Test image displayed. Press any key to exit...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return
    
    # Convert source to int if it's a number
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    logger.info("Starting trash detection system...")
    logger.info(f"Video source: {video_source}")
    logger.info(f"Confidence threshold: {args.confidence}")
    
    # Process video
    detector.process_video(video_source=video_source, output_path=args.output)


if __name__ == "__main__":
    main()
