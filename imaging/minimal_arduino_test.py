#!/usr/bin/env python3
"""
Minimal Arduino Test for Raspberry Pi
Tests Arduino connection without requiring heavy dependencies
"""

import serial
import time
import sys
import os

def test_arduino_connection(port='/dev/ttyUSB0', baud_rate=9600):
    """Test Arduino connection"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("✓ Arduino connected successfully!")
        
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
        print("✓ Arduino test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Arduino test failed: {e}")
        return False

def check_available_ports():
    """Check available serial ports"""
    print("Checking available serial ports...")
    
    # Common Arduino ports
    possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    
    available_ports = []
    for port in possible_ports:
        if os.path.exists(port):
            available_ports.append(port)
            print(f"✓ Found: {port}")
    
    if not available_ports:
        print("✗ No Arduino ports found")
        print("Make sure Arduino is connected and powered on")
        return []
    
    return available_ports

def main():
    """Main function"""
    print("=== Minimal Arduino Test for Raspberry Pi ===")
    print()
    
    # Check available ports
    ports = check_available_ports()
    
    if not ports:
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected and powered on")
        print("2. Try: ls /dev/ttyUSB* /dev/ttyACM*")
        print("3. Make sure Arduino code is uploaded")
        sys.exit(1)
    
    # Test each available port
    success = False
    for port in ports:
        print(f"\nTesting port: {port}")
        if test_arduino_connection(port):
            success = True
            break
    
    if success:
        print("\n✓ Arduino is working correctly!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install opencv-python numpy ultralytics")
        print("2. Run full test: python pi_trash_detection.py --test-arduino")
    else:
        print("\n✗ Arduino test failed on all ports")
        print("\nTroubleshooting:")
        print("1. Check Arduino is connected and powered")
        print("2. Verify Arduino code is uploaded")
        print("3. Check USB cable")
        print("4. Try different USB port")
        sys.exit(1)

if __name__ == "__main__":
    main()
