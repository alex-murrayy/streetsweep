#!/usr/bin/env python3
"""
Simple motor test script to diagnose power/wiring issues
"""

import serial
import time
import sys

def test_motor_connections(port='/dev/ttyACM1'):
    """Test motor connections step by step"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=9600, timeout=2)
        time.sleep(2)
        
        print("✓ Arduino connected!")
        print("\nTesting motor connections...")
        
        # Test 1: Check if Arduino responds
        print("\n1. Testing Arduino communication...")
        ser.write(b'h\n')
        time.sleep(1)
        response = ser.readline().decode().strip()
        if response:
            print(f"✓ Arduino responds: {response}")
        else:
            print("✗ Arduino not responding")
            return False
        
        # Test 2: Try slowest speed preset
        print("\n2. Testing with slowest speed (preset 1)...")
        ser.write(b'1\n')  # Set to 300 steps/sec
        time.sleep(0.5)
        
        # Test 3: Try forward movement
        print("3. Testing forward movement...")
        ser.write(b'w\n')
        time.sleep(2)
        
        # Test 4: Stop
        print("4. Stopping motors...")
        ser.write(b'x\n')
        time.sleep(1)
        
        # Test 5: Try reverse
        print("5. Testing reverse movement...")
        ser.write(b's\n')
        time.sleep(2)
        
        # Test 6: Stop
        print("6. Stopping motors...")
        ser.write(b'x\n')
        time.sleep(1)
        
        ser.close()
        print("\n✓ Test completed!")
        print("\nIf motors didn't move, check:")
        print("  • External 5V/2A power supply connected")
        print("  • All grounds connected together")
        print("  • Motor wiring (8 wires total)")
        print("  • ULN2003 driver boards powered")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Motor Connections')
    parser.add_argument('--port', type=str, default='/dev/ttyACM1',
                       help='Arduino serial port')
    
    args = parser.parse_args()
    
    print("Motor Connection Test")
    print("=" * 30)
    print("This will test your motor setup step by step.")
    print("Make sure your Arduino is connected and powered.")
    print()
    
    test_motor_connections(args.port)

if __name__ == "__main__":
    main()
