#!/usr/bin/env python3
"""
Arduino Sketch Detector
Identifies what sketch is currently running on the Arduino
"""

import serial
import time
import sys

def detect_arduino_sketch(port='/dev/ttyACM0', baud_rate=9600):
    """Detect what sketch is running on Arduino"""
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

def send_arduino_command(port='/dev/ttyACM0', command='h'):
    """Send a single command to Arduino"""
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

def interactive_control(port='/dev/ttyACM0'):
    """Interactive Arduino control"""
    try:
        ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        time.sleep(1)
        
        print("Interactive Arduino Control")
        print("Commands: w/a/s/d/x (WASD), h (help), q (quit)")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command:
                ser.write(f"{command}\n".encode())
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

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Arduino Remote Control')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                       help='Arduino serial port')
    parser.add_argument('--detect', action='store_true',
                       help='Detect current Arduino sketch')
    parser.add_argument('--command', type=str,
                       help='Send single command to Arduino')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive control mode')
    
    args = parser.parse_args()
    
    if args.detect:
        detect_arduino_sketch(args.port)
    elif args.command:
        send_arduino_command(args.port, args.command)
    elif args.interactive:
        interactive_control(args.port)
    else:
        print("Arduino Remote Control")
        print("Usage:")
        print("  python3 arduino_control.py --detect          # Detect current sketch")
        print("  python3 arduino_control.py --command w       # Send single command")
        print("  python3 arduino_control.py --interactive    # Interactive mode")

if __name__ == "__main__":
    main()
