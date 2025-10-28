#!/usr/bin/env python3
"""
Raspberry Pi Trash Detection with Arduino Motor Control
Integrates your existing trash detection system with Arduino R4 motor control
Uses mjpg-streamer for webcam input and provides remote video streaming
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
from typing import List, Dict, Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trash_detector import TrashDetector, TrashCollector
from src.trash_detector.config import DEFAULT_CAMERA_INDEX

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


class ArduinoController:
    """Handles communication with Arduino R4 for motor control"""
    
    def __init__(self, serial_port: str = None, baud_rate: int = 9600):
        # Auto-detect port if not specified
        if serial_port is None:
            logger.info("Auto-detecting Arduino port...")
            serial_port = auto_detect_arduino_port()
            if serial_port is None:
                logger.warning("Could not auto-detect Arduino port!")
                serial_port = '/dev/ttyACM0'  # Fallback to default
        
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.is_connected = False
        self.last_command_time = 0
        self.command_cooldown = 1.0  # Minimum time between commands (seconds)
        
    def connect(self) -> bool:
        """Connect to Arduino via serial"""
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=1
            )
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            logger.info(f"Connected to Arduino on {self.serial_port}")
            
            # Send test command to verify connection
            self.send_command('i')  # Status command
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            logger.info("Disconnected from Arduino")
    
    def send_command(self, command: str) -> bool:
        """Send command to Arduino with cooldown protection"""
        if not self.is_connected or not self.serial_connection:
            logger.warning("Not connected to Arduino")
            return False
        
        # Check cooldown to prevent excessive commands
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        
        try:
            self.serial_connection.write(f"{command}\n".encode())
            self.last_command_time = current_time
            logger.debug(f"Sent command to Arduino: {command}")
            return True
        except Exception as e:
            logger.error(f"Failed to send command to Arduino: {e}")
            return False
    
    def move_towards_trash(self, detection: Dict):
        """Move both motors forward when trash is detected"""
        if not detection:
            return
        
        # Always move forward when trash is detected
        self.send_command('w')  # Move forward (WASD scheme)
        logger.info("Moving FORWARD towards trash")
    
    def stop_motor(self):
        """Stop motor movement"""
        self.send_command('x')  # Stop command in WASD scheme
        logger.info("Stopping motor")
    
    def home_motor(self):
        """Move motor to home position"""
        self.send_command('s')  # Reverse to home position
        logger.info("Moving to home position")
    
    def test_motor(self):
        """Run motor test sequence"""
        # Test sequence: forward, pivot left, pivot right, stop
        self.send_command('w')  # Forward
        time.sleep(1)
        self.send_command('a')  # Pivot left
        time.sleep(1)
        self.send_command('d')  # Pivot right
        time.sleep(1)
        self.send_command('x')  # Stop
        logger.info("Running motor test sequence")


class MjpgStreamerInterface:
    """Interface for mjpg-streamer webcam input"""
    
    def __init__(self, stream_url: str = "http://localhost:8080/?action=stream"):
        self.stream_url = stream_url
        self.is_streaming = False
        
    def check_stream_status(self) -> bool:
        """Check if mjpg-streamer is running"""
        try:
            response = requests.get(self.stream_url, timeout=2)
            self.is_streaming = response.status_code == 200
            return self.is_streaming
        except:
            self.is_streaming = False
            return False
    
    def get_stream_url(self) -> str:
        """Get the stream URL for OpenCV"""
        return self.stream_url


class PiTrashDetectionSystem:
    """Main system for running trash detection on Raspberry Pi with motor control"""
    
    def __init__(self, camera_source: str = "0", arduino_port: str = '/dev/ttyUSB0', 
                 confidence_threshold: float = 0.5, use_advanced: bool = False,
                 use_mjpg_streamer: bool = False, headless: bool = False):
        self.camera_source = camera_source
        self.confidence_threshold = confidence_threshold
        self.use_advanced = use_advanced
        self.use_mjpg_streamer = use_mjpg_streamer
        self.headless = headless
        
        # Initialize detector
        self.detector = TrashDetector(
            confidence_threshold=confidence_threshold,
            use_advanced=use_advanced
        )
        
        # Initialize Arduino controller
        self.arduino_controller = ArduinoController(serial_port=arduino_port)
        
        # Initialize mjpg-streamer interface
        self.mjpg_interface = MjpgStreamerInterface()
        
        # Detection tracking
        self.last_detection_time = 0
        self.detection_cooldown = 3.0  # Minimum time between motor movements (seconds)
        self.consecutive_detections = 0
        self.min_consecutive_detections = 2  # Require 2 consecutive detections before moving
        
    def start(self):
        """Start the trash detection system"""
        logger.info("Starting Pi Trash Detection System...")
        
        # Check mjpg-streamer if enabled
        if self.use_mjpg_streamer:
            if not self.mjpg_interface.check_stream_status():
                logger.warning("mjpg-streamer not running. Starting with direct camera...")
                self.use_mjpg_streamer = False
        
        # Connect to Arduino
        if not self.arduino_controller.connect():
            logger.error("Failed to connect to Arduino. Continuing without motor control.")
        
        # Start video processing
        self.process_video()
    
    def process_video(self):
        """Process video feed and control motors based on detections"""
        import cv2
        
        # Determine video source
        if self.use_mjpg_streamer:
            video_source = self.mjpg_interface.get_stream_url()
            logger.info(f"Using mjpg-streamer: {video_source}")
        else:
            video_source = int(self.camera_source) if self.camera_source.isdigit() else self.camera_source
            logger.info(f"Using direct camera: {video_source}")
        
        # Open video source
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            logger.error(f"Could not open video source: {video_source}")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        logger.info("Video source opened successfully")
        if self.headless:
            logger.info("Headless mode: Type commands and press Enter")
            self.print_headless_help()
        else:
            logger.info("Press 'q' to quit, 's' to stop motor, 'h' to home motor, 't' to test motor")
        
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
                
                # Detect trash in current frame
                detections = self.detector.detect_trash(frame)
                
                # Process detections for motor control
                if detections:
                    self.process_detections_for_motor_control(detections)
                else:
                    self.consecutive_detections = 0
                
                # Draw detections on frame
                frame_with_detections = self.detector.draw_detections(frame.copy(), detections)
                
                # Add system info
                info_text = f"Frame: {frame_count} | Detections: {len(detections)}"
                cv2.putText(frame_with_detections, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add motor status
                motor_status = "MOTOR: CONNECTED" if self.arduino_controller.is_connected else "MOTOR: DISCONNECTED"
                cv2.putText(frame_with_detections, motor_status, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if self.arduino_controller.is_connected else (0, 0, 255), 2)
                
                # Add detection confidence info
                if detections:
                    best_detection = max(detections, key=lambda d: d.get('confidence', 0))
                    conf_text = f"Best: {best_detection.get('class', 'trash')} ({best_detection.get('confidence', 0):.2f})"
                    cv2.putText(frame_with_detections, conf_text, (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                
                # Display frame (only if not in headless mode)
                if not self.headless:
                    cv2.imshow('Pi Trash Detection with Motor Control', frame_with_detections)
                    
                    # Handle keyboard input (WASD scheme)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('x'):  # Stop motor
                        self.arduino_controller.stop_motor()
                    elif key == ord('s'):  # Reverse/home
                        self.arduino_controller.home_motor()
                    elif key == ord('t'):  # Test sequence
                        self.arduino_controller.test_motor()
                    elif key == ord('w'):  # Manual forward
                        self.arduino_controller.send_command('w')
                    elif key == ord('a'):  # Manual pivot left
                        self.arduino_controller.send_command('a')
                    elif key == ord('d'):  # Manual pivot right
                        self.arduino_controller.send_command('d')
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
                        elif key == 's':  # Reverse/home
                            self.arduino_controller.home_motor()
                        elif key == 't':  # Test sequence
                            self.arduino_controller.test_motor()
                        elif key == 'w':  # Manual forward
                            self.arduino_controller.send_command('w')
                        elif key == 'a':  # Manual pivot left
                            self.arduino_controller.send_command('a')
                        elif key == 'd':  # Manual pivot right
                            self.arduino_controller.send_command('d')
                        elif key == 'h':  # Help
                            self.print_headless_help()
                    
                    # Add a small delay to prevent excessive CPU usage
                    time.sleep(0.033)  # ~30 FPS
                
                # Log performance every 100 frames
                if frame_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                    logger.info(f"Processing at {fps:.1f} FPS")
                
                # Log stats every 30 seconds
                current_time = time.time()
                if current_time - last_stats_time > 30:
                    logger.info(f"System running: {frame_count} frames processed")
                    last_stats_time = current_time
                
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
        """Process detections and send motor commands"""
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
                self.arduino_controller.move_towards_trash(best_detection)
                self.last_detection_time = current_time
                self.consecutive_detections = 0  # Reset counter
                
                logger.info(f"Moving towards {best_detection.get('class', 'trash')} "
                           f"(confidence: {best_detection.get('confidence', 0):.2f})")

    def print_headless_help(self):
        """Print help for headless mode"""
        logger.info("=== HEADLESS MODE CONTROLS ===")
        logger.info("Type command and press Enter:")
        logger.info("  w = Forward (both motors)")
        logger.info("  s = Reverse (both motors)")
        logger.info("  a = Pivot left")
        logger.info("  d = Pivot right")
        logger.info("  x = Stop")
        logger.info("  t = Test sequence")
        logger.info("  h = Show this help")
        logger.info("  q = Quit")
        logger.info("===============================")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Pi Trash Detection with Arduino Motor Control')
    parser.add_argument('--camera', type=str, default='0', 
                       help='Camera source: camera index (0,1,2...) or mjpg-streamer URL')
    parser.add_argument('--arduino-port', type=str, default=None,
                       help='Arduino serial port (auto-detected if not specified)')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Confidence threshold for detections (default: 0.5)')
    parser.add_argument('--advanced', action='store_true',
                       help='Use advanced multi-model detector')
    parser.add_argument('--mjpg-streamer', action='store_true',
                       help='Use mjpg-streamer instead of direct camera')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--test-camera', action='store_true',
                       help='Test camera connection and exit')
    parser.add_argument('--test-arduino', action='store_true',
                       help='Test Arduino connection and exit')
    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode (no GUI windows)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Test camera if requested
    if args.test_camera:
        import cv2
        if args.mjpg_streamer:
            cap = cv2.VideoCapture("http://localhost:8080/?action=stream")
        else:
            cap = cv2.VideoCapture(int(args.camera))
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                logger.info(f"Camera working - resolution: {frame.shape}")
            else:
                logger.error("Camera opened but failed to read frame")
        else:
            logger.error(f"Could not open camera source: {args.camera}")
        cap.release()
        return
    
    # Test Arduino if requested
    if args.test_arduino:
        controller = ArduinoController(serial_port=args.arduino_port)
        if controller.connect():
            controller.test_motor()
            time.sleep(2)
            controller.stop_motor()
            controller.disconnect()
            logger.info("Arduino test completed")
        else:
            logger.error("Arduino test failed")
        return
    
    # Create and start system
    system = PiTrashDetectionSystem(
        camera_source=args.camera,
        arduino_port=args.arduino_port,
        confidence_threshold=args.confidence,
        use_advanced=args.advanced,
        use_mjpg_streamer=args.mjpg_streamer,
        headless=args.headless
    )
    
    system.start()


if __name__ == "__main__":
    main()
