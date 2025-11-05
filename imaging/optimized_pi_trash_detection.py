#!/usr/bin/env python3
"""
Optimized Raspberry Pi Trash Detection with Motor Control
- Reduced AI processing load
- Faster motor response
- Better performance on Pi
"""

import sys
import os
import argparse
import logging
import time
import serial
import threading
import queue
import json
import requests
import glob
import cv2
import numpy as np
from typing import List, Dict, Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trash_detector import TrashDetector, TrashCollector
from src.trash_detector.config import DEFAULT_CAMERA_INDEX

# Import RC car controller
sys.path.append(os.path.dirname(__file__))
from rc_car_controller import auto_detect_arduino_port, send_rc_command

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_arduino_ports():
    """Automatically find Arduino ports on Raspberry Pi"""
    arduino_ports = []
    
    # Common Arduino port patterns on Linux/Raspberry Pi
    port_patterns = [
        '/dev/ttyACM*',  # Most common for Arduino Uno/Nano
        '/dev/ttyUSB*',  # USB-to-serial adapters
        '/dev/ttyAMA*',  # Raspberry Pi UART
    ]
    
    for pattern in port_patterns:
        ports = glob.glob(pattern)
        arduino_ports.extend(ports)
    
    # Filter out ports that are likely not Arduino
    filtered_ports = []
    for port in arduino_ports:
        # Skip if it's a Bluetooth or other non-Arduino device
        if any(skip in port.lower() for skip in ['bluetooth', 'gps', 'modem']):
            continue
        filtered_ports.append(port)
    
    return sorted(filtered_ports)


def auto_detect_arduino_port():
    """Auto-detect the best Arduino port"""
    ports = find_arduino_ports()
    
    if not ports:
        logger.warning("No Arduino ports found!")
        logger.warning("Make sure your Arduino is connected via USB.")
        return None
    
    logger.info(f"Found Arduino ports: {ports}")
    
    # Try each port to see which one responds
    for port in ports:
        try:
            logger.info(f"Testing {port}...")
            ser = serial.Serial(port=port, baudrate=9600, timeout=1)
            time.sleep(1)  # Give Arduino time to initialize
            
            # Send a test command
            ser.write(b'h\n')  # Help command
            time.sleep(0.5)
            
            # Check if we get a response
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    logger.info(f"✓ Arduino responding on {port}: {response}")
                    ser.close()
                    return port
            
            ser.close()
            
        except Exception as e:
            logger.debug(f"✗ {port}: {e}")
            continue
    
    # If no port responded, return the first available one
    if ports:
        logger.info(f"Using first available port: {ports[0]}")
        return ports[0]
    
    return None


class RCCarController:
    """RC Car controller for Arduino R4 using <steer,throttle> protocol"""
    
    def __init__(self, serial_port: str = None):
        # Auto-detect port if not specified
        if serial_port is None:
            logger.info("Auto-detecting Arduino port...")
            serial_port = auto_detect_arduino_port()
            if serial_port is None:
                logger.warning("Could not auto-detect Arduino port!")
                serial_port = '/dev/ttyACM0'  # Fallback to default
        
        self.serial_port = serial_port
        self.is_connected = False
        self.last_command_time = 0
        self.command_cooldown = 0.1  # 100ms between commands (faster for RC car)
        
        # RC Car parameters
        self.frame_width = 640  # Camera frame width
        self.steer_center = 90  # Center steering angle
        self.steer_min = 45  # Left limit
        self.steer_max = 135  # Right limit
        self.throttle_min = 50  # Minimum throttle to move (avoid dead zone)
        self.throttle_max = 200  # Maximum throttle for safety
        
    def connect(self) -> bool:
        """Connect to Arduino via serial"""
        try:
            # Test connection by sending a stop command
            result = send_rc_command(self.serial_port, self.steer_center, 0)
            if result:
                self.is_connected = True
                logger.info(f"Connected to RC Car Arduino on {self.serial_port}")
                return True
            else:
                logger.error("Failed to connect to Arduino")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        # Send stop command before disconnecting
        if self.is_connected:
            send_rc_command(self.serial_port, self.steer_center, 0)
        self.is_connected = False
        logger.info("Disconnected from Arduino")
    
    def send_rc_command(self, steer_angle: int, throttle: int) -> bool:
        """Send RC car command to Arduino"""
        if not self.is_connected:
            logger.warning("Not connected to Arduino")
            return False
        
        # Check cooldown to prevent excessive commands
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        
        try:
            # Call the imported function directly
            result = send_rc_command(self.serial_port, steer_angle, throttle)
            self.last_command_time = current_time
            logger.debug(f"Sent RC command: <{steer_angle},{throttle}>")
            return result
        except Exception as e:
            logger.error(f"Failed to send RC command: {e}")
            return False
    
    def move_towards_trash(self, detection: Dict):
        """Move towards detected trash with smart steering and throttle"""
        if not detection:
            return
        
        # Get detection position and confidence
        bbox = detection.get('bbox', [0, 0, 100, 100])
        confidence = detection.get('confidence', 0.5)
        
        # Calculate center of detection
        x_center = (bbox[0] + bbox[2]) / 2
        frame_width = self.frame_width
        
        # Calculate steering angle based on trash position
        # Map frame position (0-640) to steering angle (45-135)
        # Center (320) = 90 degrees
        position_ratio = (x_center / frame_width)  # 0.0 to 1.0
        steer_angle = int(self.steer_min + (position_ratio * (self.steer_max - self.steer_min)))
        steer_angle = max(self.steer_min, min(self.steer_max, steer_angle))
        
        # Calculate throttle based on confidence
        # Higher confidence = higher throttle
        # Scale confidence (0.5-1.0) to throttle (min-max)
        confidence_normalized = max(0.0, min(1.0, (confidence - 0.5) * 2.0))  # Scale 0.5-1.0 to 0.0-1.0
        throttle = int(self.throttle_min + (confidence_normalized * (self.throttle_max - self.throttle_min)))
        
        # Send command to Arduino
        self.send_rc_command(steer_angle, throttle)
        
        # Log the action
        direction = "LEFT" if steer_angle < 90 else "RIGHT" if steer_angle > 90 else "CENTER"
        logger.info(f"Moving {direction} (steer={steer_angle}°, throttle={throttle}) "
                   f"towards {detection.get('class', 'trash')} (confidence: {confidence:.2f})")
    
    def stop_motor(self):
        """Stop motor movement"""
        self.send_rc_command(self.steer_center, 0)
        logger.info("Stopping RC car")
    
    def set_speed(self, speed: int):
        """Set throttle speed (1-9 scale, maps to throttle_min-throttle_max)"""
        if 1 <= speed <= 9:
            # Map 1-9 to throttle range
            throttle = int(self.throttle_min + ((speed - 1) / 8.0) * (self.throttle_max - self.throttle_min))
            self.send_rc_command(self.steer_center, throttle)
            logger.info(f"Throttle set to {throttle} (level {speed})")


class OptimizedPiTrashDetectionSystem:
    """Optimized trash detection system for Raspberry Pi"""
    
    def __init__(self, camera_source: str = "0", arduino_port: str = None, 
                 confidence_threshold: float = 0.6, use_advanced: bool = False,
                 headless: bool = False, frame_skip: int = 3, simulate_motors: bool = False,
                 stop_timeout: float = 3.0):
        self.camera_source = camera_source
        self.confidence_threshold = confidence_threshold
        self.use_advanced = use_advanced
        self.headless = headless
        self.frame_skip = frame_skip  # Process every Nth frame
        self.simulate_motors = simulate_motors
        
        # Initialize detector with optimized settings
        self.detector = TrashDetector(
            confidence_threshold=confidence_threshold,
            use_advanced=use_advanced
        )
        
        # Initialize RC Car controller
        if simulate_motors:
            self.arduino_controller = None
            logger.info("Motor simulation mode enabled - no Arduino needed")
        else:
            self.arduino_controller = RCCarController(serial_port=arduino_port)
        
        # Detection tracking (more responsive)
        self.last_detection_time = 0
        self.detection_cooldown = 1.0  # Reduced from 3.0 seconds
        self.consecutive_detections = 0
        self.min_consecutive_detections = 1  # Reduced from 2
        self.frame_count = 0
        
        # No detection timeout - stop motors if no trash detected for X seconds
        self.no_detection_timeout = stop_timeout
        self.last_stop_time = 0
        self.stop_cooldown = 2.0  # Don't spam stop commands
        
    def start(self):
        """Start the optimized trash detection system"""
        logger.info("Starting Optimized Pi Trash Detection System...")
        
        # Connect to Arduino
        if not self.simulate_motors:
            if not self.arduino_controller.connect():
                logger.error("Failed to connect to Arduino. Continuing without motor control.")
        else:
            logger.info("Running in simulation mode - motor commands will be logged only")
        
        # Start video processing
        self.process_video()
    
    def process_video(self):
        """Process video feed with optimizations"""
        # Determine video source
        video_source = int(self.camera_source) if self.camera_source.isdigit() else self.camera_source
        logger.info(f"Using camera: {video_source}")
        
        # Open video source with optimized settings
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            logger.error(f"Could not open video source: {video_source}")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)  # Reduced FPS for better performance
        
        logger.info("Video source opened successfully")
        if self.headless:
            logger.info("Headless mode: Type commands and press Enter")
            self.print_headless_help()
        else:
            logger.info("Press 'q' to quit, 's' to stop motor, 'h' to home motor")
        
        frame_count = 0
        start_time = time.time()
        last_stats_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame from video source")
                    break
                
                frame_count += 1
                
                # Skip frames for better performance
                if frame_count % self.frame_skip != 0:
                    continue
                
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (320, 240))
                
                # Detect trash in current frame
                detections = self.detector.detect_trash(small_frame)
                
                # Process detections for motor control
                if detections:
                    self.process_detections_for_motor_control(detections)
                else:
                    # No detections - check if we should stop motors
                    self.consecutive_detections = 0
                    self.check_no_detection_timeout()
                
                # Draw detections on original frame
                frame_with_detections = self.detector.draw_detections(frame.copy(), detections)
                
                # Add system info
                info_text = f"Frame: {frame_count} | Detections: {len(detections)} | FPS: {frame_count/(time.time()-start_time):.1f}"
                cv2.putText(frame_with_detections, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add motor status
                if self.simulate_motors:
                    motor_status = "MOTOR: SIMULATION MODE"
                    color = (255, 255, 0)  # Yellow
                elif self.arduino_controller and self.arduino_controller.is_connected:
                    motor_status = "MOTOR: CONNECTED"
                    color = (0, 255, 0)  # Green
                else:
                    motor_status = "MOTOR: DISCONNECTED"
                    color = (0, 0, 255)  # Red
                
                cv2.putText(frame_with_detections, motor_status, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Display frame (only if not in headless mode)
                if not self.headless:
                    cv2.imshow('Optimized Pi Trash Detection', frame_with_detections)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('x'):  # Stop motor
                        self.arduino_controller.stop_motor()
                    elif key == ord('s'):  # Set speed
                        speed = int(input("Enter speed (1-5): "))
                        self.arduino_controller.set_speed(speed)
                else:
                    # In headless mode, check for manual control via stdin
                    import select
                    import sys
                    
                    # Check if there's input available (non-blocking)
                    if select.select([sys.stdin], [], [], 0)[0]:
                        key = sys.stdin.readline().strip().lower()
                        if key == 'q':
                            break
                        elif key == 'x':  # Stop motor
                            self.arduino_controller.stop_motor()
                        elif key.isdigit() and 1 <= int(key) <= 5:
                            self.arduino_controller.set_speed(int(key))
                    
                    # Add a small delay to prevent excessive CPU usage
                    time.sleep(0.067)  # ~15 FPS
                
                # Log performance every 50 frames
                if frame_count % 50 == 0:
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                    logger.info(f"Processing at {fps:.1f} FPS")
                
        except KeyboardInterrupt:
            logger.info("Processing interrupted by user")
        
        finally:
            # Cleanup
            cap.release()
            if not self.headless:
                cv2.destroyAllWindows()
            self.arduino_controller.disconnect()
            
            # Performance statistics
            elapsed_time = time.time() - start_time
            avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            logger.info(f"Processed {frame_count} frames in {elapsed_time:.2f}s (avg FPS: {avg_fps:.2f})")
    
    def process_detections_for_motor_control(self, detections: List[Dict]):
        """Process detections and send motor commands with smart steering"""
        current_time = time.time()
        
        # Check cooldown to prevent excessive motor movements
        if current_time - self.last_detection_time < self.detection_cooldown:
            return
        
        # Find the largest/most confident detection
        best_detection = max(detections, key=lambda d: d.get('confidence', 0))
        
        # Only move if confidence is high enough
        if best_detection.get('confidence', 0) > self.confidence_threshold:
            self.consecutive_detections += 1
            
            # Only move after consecutive detections to avoid false positives
            if self.consecutive_detections >= self.min_consecutive_detections:
                if self.simulate_motors:
                    # Simulation mode - calculate and log the action
                    bbox = best_detection.get('bbox', [0, 0, 100, 100])
                    confidence = best_detection.get('confidence', 0.5)
                    x_center = (bbox[0] + bbox[2]) / 2
                    frame_width = 640
                    
                    # Calculate steering angle (same as real mode)
                    position_ratio = (x_center / frame_width)
                    steer_angle = int(45 + (position_ratio * 90))  # 45-135 range
                    
                    # Calculate throttle based on confidence
                    confidence_normalized = max(0.0, min(1.0, (confidence - 0.5) * 2.0))
                    throttle = int(50 + (confidence_normalized * 150))  # 50-200 range
                    
                    direction = "LEFT" if steer_angle < 90 else "RIGHT" if steer_angle > 90 else "CENTER"
                    logger.info(f"[SIMULATION] Steer {direction} ({steer_angle}°), Throttle {throttle} "
                               f"towards {best_detection.get('class', 'trash')} "
                               f"(confidence: {confidence:.2f})")
                else:
                    # Real mode - send commands to Arduino
                    self.arduino_controller.move_towards_trash(best_detection)
                
                self.last_detection_time = current_time
                self.consecutive_detections = 0  # Reset counter

    def check_no_detection_timeout(self):
        """Check if we should stop motors due to no detections"""
        current_time = time.time()
        
        # Only check if we've had detections before
        if self.last_detection_time > 0:
            time_since_last_detection = current_time - self.last_detection_time
            
            # If no detections for the timeout period, stop motors
            if time_since_last_detection > self.no_detection_timeout:
                # Check cooldown to avoid spamming stop commands
                if current_time - self.last_stop_time > self.stop_cooldown:
                    if self.simulate_motors:
                        logger.info("[SIMULATION] STOP - No trash detected for 3+ seconds")
                    else:
                        self.arduino_controller.stop_motor()
                        logger.info("STOP - No trash detected for 3+ seconds")
                    
                    self.last_stop_time = current_time
                    self.last_detection_time = 0  # Reset to avoid repeated stops

    def print_headless_help(self):
        """Print help for headless mode"""
        logger.info("=== HEADLESS MODE CONTROLS ===")
        logger.info("Type command and press Enter:")
        logger.info("  1-5 = Set speed (1=slowest, 5=fastest)")
        logger.info("  x = Stop motor")
        logger.info("  q = Quit")
        logger.info("===============================")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Optimized Pi Trash Detection with Motor Control')
    parser.add_argument('--camera', type=str, default='0', 
                       help='Camera source: camera index (0,1,2...)')
    parser.add_argument('--arduino-port', type=str, default=None,
                       help='Arduino serial port (auto-detected if not specified)')
    parser.add_argument('--confidence', type=float, default=0.6,
                       help='Confidence threshold for detections (default: 0.6)')
    parser.add_argument('--advanced', action='store_true',
                       help='Use advanced multi-model detector')
    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode (no GUI windows)')
    parser.add_argument('--frame-skip', type=int, default=3,
                       help='Process every Nth frame for better performance (default: 3)')
    parser.add_argument('--simulate-motors', action='store_true',
                       help='Run in simulation mode (no Arduino needed)')
    parser.add_argument('--stop-timeout', type=float, default=3.0,
                       help='Stop motors after X seconds of no detections (default: 3.0)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start system
    system = OptimizedPiTrashDetectionSystem(
        camera_source=args.camera,
        arduino_port=args.arduino_port,
        confidence_threshold=args.confidence,
        use_advanced=args.advanced,
        headless=args.headless,
        frame_skip=args.frame_skip,
        simulate_motors=args.simulate_motors,
        stop_timeout=args.stop_timeout
    )
    
    system.start()


if __name__ == "__main__":
    main()
