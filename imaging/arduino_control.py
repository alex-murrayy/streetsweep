#!/usr/bin/env python3
"""
Arduino Sketch Detector
Identifies what sketch is currently running on the Arduino
"""

import serial
import time
import sys
import glob
import os

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
        print("No Arduino ports found!")
        print("Make sure your Arduino is connected via USB.")
        return None
    
    print(f"Found Arduino ports: {ports}")
    
    # Try each port to see which one responds
    for port in ports:
        try:
            print(f"Testing {port}...")
            ser = serial.Serial(port=port, baudrate=9600, timeout=1)
            time.sleep(1)  # Give Arduino time to initialize
            
            # Send a test command
            ser.write(b'h\n')  # Help command
            time.sleep(0.5)
            
            # Check if we get a response
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"✓ Arduino responding on {port}: {response}")
                    ser.close()
                    return port
            
            ser.close()
            
        except Exception as e:
            print(f"✗ {port}: {e}")
            continue
    
    # If no port responded, return the first available one
    if ports:
        print(f"Using first available port: {ports[0]}")
        return ports[0]
    
    return None

def detect_arduino_sketch(port=None, baud_rate=9600):
    """Detect what sketch is running on Arduino"""
    # Auto-detect port if not specified
    if port is None:
        print("Auto-detecting Arduino port...")
        port = auto_detect_arduino_port()
        if port is None:
            print("Could not find Arduino port!")
            return None
    
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("✓ Arduino connected!")
        print("\nDetecting current sketch...")
        
        # Test different command sets to identify the sketch
        sketches = {
            'WASD Dual Stepper': {
                'commands': ['h', 'w', 'a', 's', 'd', 'x'],
                'expected_responses': ['WASD Drive', 'FORWARD', 'PIVOT LEFT', 'REVERSE', 'PIVOT RIGHT', 'STOP']
            },
            'Single Stepper Control': {
                'commands': ['i', 'f', 'b', 's', '1', '2', '3'],
                'expected_responses': ['Stepper Motor Status', 'Rotating', 'STOPPED']
            },
            'Dual Motor Control': {
                'commands': ['w', 'a', 's', 'd', 'x'],
                'expected_responses': ['FORWARD', 'LEFT', 'REVERSE', 'RIGHT', 'STOP']
            }
        }
        
        detected_sketch = None
        responses = {}
        
        for sketch_name, test_data in sketches.items():
            print(f"\nTesting {sketch_name}...")
            sketch_responses = []
            
            for cmd in test_data['commands']:
                ser.write(f"{cmd}\n".encode())
                time.sleep(0.3)
                
                # Read response
                while ser.in_waiting > 0:
                    response = ser.readline().decode().strip()
                    if response:
                        sketch_responses.append(response)
                        print(f"  {cmd}: {response}")
            
            responses[sketch_name] = sketch_responses
            
            # Check if responses match expected patterns
            if any(expected in ' '.join(sketch_responses) for expected in test_data['expected_responses']):
                detected_sketch = sketch_name
                print(f"  ✓ Likely match: {sketch_name}")
            else:
                print(f"  ✗ No match: {sketch_name}")
        
        ser.close()
        
        # Summary
        print(f"\n{'='*50}")
        print("ARDUINO SKETCH DETECTION RESULTS")
        print(f"{'='*50}")
        
        if detected_sketch:
            print(f"✓ Detected Sketch: {detected_sketch}")
        else:
            print("✗ Could not identify sketch")
            print("Raw responses received:")
            for sketch, responses in responses.items():
                print(f"  {sketch}: {responses}")
        
        return detected_sketch
        
    except Exception as e:
        print(f"✗ Detection failed: {e}")
        return None

def send_arduino_command(port=None, command='h'):
    """Send a single command to Arduino"""
    # Auto-detect port if not specified
    if port is None:
        print("Auto-detecting Arduino port...")
        port = auto_detect_arduino_port()
        if port is None:
            print("Could not find Arduino port!")
            return False
    
    try:
        ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        time.sleep(1)
        
        print(f"Sending command: {command}")
        ser.write(f"{command}\n".encode())
        time.sleep(0.5)
        
        # Read response
        while ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"Arduino: {response}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_control(port=None):
    """Interactive Arduino control with speed control"""
    # Auto-detect port if not specified
    if port is None:
        print("Auto-detecting Arduino port...")
        port = auto_detect_arduino_port()
        if port is None:
            print("Could not find Arduino port!")
            return
    
    try:
        ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        time.sleep(1)
        
        print("Interactive Arduino Control with Speed Control")
        print("Movement Commands: w/a/s/d/x (WASD)")
        print("Speed Commands: 1-9 (speed levels), 0 (stop)")
        print("Other Commands: h (help), q (quit)")
        print("Speed Control: + (increase), - (decrease)")
        
        current_speed = 5  # Default medium speed (1-9 scale)
        
        while True:
            command = input(f"\nEnter command (speed: {current_speed}): ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'h':
                print_help()
            elif command in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                # Set specific speed
                current_speed = int(command)
                ser.write(f"s{current_speed}\n".encode())
                print(f"Speed set to: {current_speed}")
                time.sleep(0.3)
            elif command == '0':
                # Stop motors
                ser.write("x\n".encode())
                print("Motors stopped")
                time.sleep(0.3)
            elif command == '+':
                # Increase speed
                if current_speed < 9:
                    current_speed += 1
                    ser.write(f"s{current_speed}\n".encode())
                    print(f"Speed increased to: {current_speed}")
                else:
                    print("Already at maximum speed (9)")
                time.sleep(0.3)
            elif command == '-':
                # Decrease speed
                if current_speed > 1:
                    current_speed -= 1
                    ser.write(f"s{current_speed}\n".encode())
                    print(f"Speed decreased to: {current_speed}")
                else:
                    print("Already at minimum speed (1)")
                time.sleep(0.3)
            elif command in ['w', 'a', 's', 'd']:
                # Movement commands with current speed
                ser.write(f"{command}{current_speed}\n".encode())
                print(f"Moving {command.upper()} at speed {current_speed}")
                time.sleep(0.3)
            elif command == 'x':
                # Stop command
                ser.write("x\n".encode())
                print("Stop command sent")
                time.sleep(0.3)
            elif command:
                # Send raw command
                ser.write(f"{command}\n".encode())
                print(f"Sent raw command: {command}")
                time.sleep(0.3)
            
            # Read response
            while ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"Arduino: {response}")
        
        ser.close()
        print("Disconnected.")
        
    except Exception as e:
        print(f"Error: {e}")

def print_help():
    """Print detailed help for interactive mode"""
    print("\n" + "="*50)
    print("ARDUINO INTERACTIVE CONTROL HELP")
    print("="*50)
    print("MOVEMENT COMMANDS:")
    print("  w = Forward")
    print("  s = Reverse/Backward")
    print("  a = Pivot Left")
    print("  d = Pivot Right")
    print("  x = Stop")
    print("")
    print("SPEED CONTROL:")
    print("  1-9 = Set specific speed level (1=slowest, 9=fastest)")
    print("  0   = Stop motors")
    print("  +   = Increase speed by 1")
    print("  -   = Decrease speed by 1")
    print("")
    print("OTHER COMMANDS:")
    print("  h = Show this help")
    print("  q = Quit")
    print("")
    print("EXAMPLES:")
    print("  w5 = Move forward at speed 5")
    print("  a3 = Pivot left at speed 3")
    print("  s9 = Move backward at maximum speed")
    print("="*50)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Arduino Remote Control with Auto-Detection')
    parser.add_argument('--port', type=str, default=None,
                       help='Arduino serial port (auto-detected if not specified)')
    parser.add_argument('--detect', action='store_true',
                       help='Detect current Arduino sketch')
    parser.add_argument('--command', type=str,
                       help='Send single command to Arduino')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive control mode')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available Arduino ports')
    
    args = parser.parse_args()
    
    if args.list_ports:
        print("Available Arduino ports:")
        ports = find_arduino_ports()
        if ports:
            for port in ports:
                print(f"  {port}")
        else:
            print("  No Arduino ports found")
    elif args.detect:
        detect_arduino_sketch(args.port)
    elif args.command:
        send_arduino_command(args.port, args.command)
    elif args.interactive:
        interactive_control(args.port)
    else:
        print("Arduino Remote Control with Auto-Detection & Speed Control")
        print("Usage:")
        print("  python3 arduino_control.py --list-ports      # List available ports")
        print("  python3 arduino_control.py --detect          # Detect current sketch")
        print("  python3 arduino_control.py --command w       # Send single command")
        print("  python3 arduino_control.py --interactive    # Interactive mode with speed control")
        print("")
        print("Interactive Mode Features:")
        print("  • Auto-detects Arduino port")
        print("  • Speed control (1-9 levels)")
        print("  • WASD movement controls")
        print("  • Real-time speed adjustment (+/-)")
        print("")
        print("Note: Port auto-detection is enabled by default!")
        print("Use --port /dev/ttyACM1 to specify a specific port if needed.")

if __name__ == "__main__":
    main()
