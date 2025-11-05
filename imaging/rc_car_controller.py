#!/usr/bin/env python3
"""
RC Car Controller for Arduino R4
Sends steering and throttle commands in the format: <steer,throttle>
"""

import serial
import time
import sys
import glob
import os


def find_arduino_ports():
    """Automatically find Arduino ports"""
    arduino_ports = []
    
    port_patterns = [
        '/dev/ttyACM*',  # Most common for Arduino Uno/R4
        '/dev/ttyUSB*',  # USB-to-serial adapters
    ]
    
    for pattern in port_patterns:
        ports = glob.glob(pattern)
        arduino_ports.extend(ports)
    
    # Filter out ports that are likely not Arduino
    filtered_ports = []
    for port in arduino_ports:
        if any(skip in port.lower() for skip in ['bluetooth', 'gps', 'modem']):
            continue
        filtered_ports.append(port)
    
    return sorted(filtered_ports)


def auto_detect_arduino_port():
    """Auto-detect the best Arduino port"""
    ports = find_arduino_ports()
    
    if not ports:
        print("No Arduino ports found!")
        return None
    
    print(f"Found Arduino ports: {ports}")
    return ports[0]  # Use first available port


def send_rc_command(port, steer_angle, throttle):
    """
    Send RC car command to Arduino
    
    Args:
        port: Serial port (e.g., '/dev/ttyACM0')
        steer_angle: Steering angle (45-135, 90 = center)
        throttle: Throttle speed (-255 to 255, 0 = stop)
    
    Returns:
        bool: True if command sent successfully
    """
    try:
        # Constrain values to safe ranges
        steer_angle = max(45, min(135, int(steer_angle)))
        throttle = max(-255, min(255, int(throttle)))
        
        # Format command: <steer,throttle>
        command = f"<{steer_angle},{throttle}>\n"
        
        ser = serial.Serial(port=port, baudrate=115200, timeout=0.1)
        ser.write(command.encode())
        ser.close()
        
        return True
        
    except Exception as e:
        print(f"Error sending RC command: {e}")
        return False


def interactive_control(port=None):
    """Interactive RC car control"""
    # Auto-detect port if not specified
    if port is None:
        print("Auto-detecting Arduino port...")
        port = auto_detect_arduino_port()
        if port is None:
            print("Could not find Arduino port!")
            return
    
    print(f"RC Car Interactive Control on {port}")
    print("Commands:")
    print("  w/s = Forward/Reverse")
    print("  a/d = Steer Left/Right")
    print("  x = Stop")
    print("  1-9 = Set throttle (1=slow, 9=fast)")
    print("  q = Quit")
    print()
    
    current_steer = 90  # Center
    current_throttle = 0  # Stop
    throttle_step = 30  # Throttle increment per keypress
    
    try:
        while True:
            command = input(f"Steer: {current_steer}, Throttle: {current_throttle} > ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'w':
                # Forward
                current_throttle = min(255, current_throttle + throttle_step)
            elif command == 's':
                # Reverse
                current_throttle = max(-255, current_throttle - throttle_step)
            elif command == 'a':
                # Steer left
                current_steer = max(45, current_steer - 10)
            elif command == 'd':
                # Steer right
                current_steer = min(135, current_steer + 10)
            elif command == 'x':
                # Stop
                current_throttle = 0
            elif command.isdigit() and 1 <= int(command) <= 9:
                # Set throttle level
                level = int(command)
                current_throttle = int((level / 9.0) * 255)  # Scale 1-9 to 0-255
            elif command == '':
                # Just send current values
                pass
            else:
                print("Invalid command")
                continue
            
            # Send command to Arduino
            send_rc_command(port, current_steer, current_throttle)
            print(f"Sent: <{current_steer},{current_throttle}>")
            time.sleep(0.1)  # Small delay between commands
        
        # Stop on exit
        send_rc_command(port, 90, 0)
        print("Stopped and disconnected.")
        
    except KeyboardInterrupt:
        send_rc_command(port, 90, 0)
        print("\nStopped and disconnected.")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC Car Controller')
    parser.add_argument('--port', type=str, default=None,
                       help='Arduino serial port (auto-detected if not specified)')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive control mode')
    parser.add_argument('--test', action='store_true',
                       help='Test connection')
    
    args = parser.parse_args()
    
    if args.test:
        port = args.port or auto_detect_arduino_port()
        if port:
            print(f"Testing connection to {port}...")
            if send_rc_command(port, 90, 0):
                print("✓ Connection successful!")
            else:
                print("✗ Connection failed!")
        else:
            print("No Arduino port found!")
    
    elif args.interactive:
        interactive_control(args.port)
    
    else:
        print("RC Car Controller")
        print("Usage:")
        print("  python3 rc_car_controller.py --test          # Test connection")
        print("  python3 rc_car_controller.py --interactive  # Interactive mode")


if __name__ == "__main__":
    main()

