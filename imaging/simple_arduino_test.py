#!/usr/bin/env python3
"""
Simple Arduino Test Script for Raspberry Pi
Tests Arduino connection without requiring OpenCV
"""

import serial
import time
import sys

def test_arduino_connection(port='/dev/ttyUSB0', baud_rate=9600):
    """Test Arduino connection"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("Arduino connected successfully!")
        
        # Send test command
        print("Sending test command...")
        ser.write(b't\n')  # Test command
        
        # Read response
        time.sleep(1)
        response = ser.readline().decode().strip()
        print(f"Arduino response: {response}")
        
        # Send status command
        print("Requesting status...")
        ser.write(b'i\n')
        time.sleep(1)
        
        # Read status
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:
                print(f"Status: {line}")
        
        ser.close()
        print("Arduino test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Arduino test failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Arduino Test')
    parser.add_argument('--port', type=str, default='/dev/ttyUSB0',
                       help='Arduino serial port')
    parser.add_argument('--baud', type=int, default=9600,
                       help='Serial baud rate')
    
    args = parser.parse_args()
    
    print("=== Simple Arduino Test ===")
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print()
    
    # Test Arduino connection
    success = test_arduino_connection(args.port, args.baud)
    
    if not success:
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected: ls /dev/ttyUSB* /dev/ttyACM*")
        print("2. Try different port: python simple_arduino_test.py --port /dev/ttyACM0")
        print("3. Check Arduino code is uploaded")
        print("4. Verify Arduino is powered on")
        sys.exit(1)
    else:
        print("\nArduino is working correctly!")

if __name__ == "__main__":
    main()
