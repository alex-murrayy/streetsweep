#!/usr/bin/env python3
"""
Motor diagnostic script - tests each motor individually
"""

import serial
import time
import sys

def test_individual_motors(port='/dev/ttyACM1'):
    """Test each motor individually to isolate the problem"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=9600, timeout=2)
        time.sleep(2)
        
        print("✓ Arduino connected!")
        print("\nTesting individual motor control...")
        
        # Clear any existing data
        while ser.in_waiting > 0:
            ser.readline()
        
        # Test 1: Check Arduino response
        print("\n1. Testing Arduino communication...")
        ser.write(b'h\n')
        time.sleep(1)
        
        response = ""
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:
                response += line + "\n"
        
        if response:
            print("✓ Arduino response:")
            print(response)
        else:
            print("✗ No response from Arduino")
            return False
        
        # Test 2: Set slowest speed
        print("\n2. Setting slowest speed (preset 1)...")
        ser.write(b'1\n')
        time.sleep(0.5)
        
        # Test 3: Try forward (both motors)
        print("\n3. Testing FORWARD (both motors)...")
        print("   Watch both motors - they should move together")
        ser.write(b'w\n')
        time.sleep(3)
        
        # Test 4: Stop
        print("\n4. Stopping...")
        ser.write(b'x\n')
        time.sleep(1)
        
        # Test 5: Try reverse (both motors)
        print("\n5. Testing REVERSE (both motors)...")
        print("   Watch both motors - they should move together")
        ser.write(b's\n')
        time.sleep(3)
        
        # Test 6: Stop
        print("\n6. Stopping...")
        ser.write(b'x\n')
        time.sleep(1)
        
        # Test 7: Try pivot left (left motor reverse, right motor forward)
        print("\n7. Testing PIVOT LEFT...")
        print("   Left motor should go backward, right motor forward")
        ser.write(b'a\n')
        time.sleep(3)
        
        # Test 8: Stop
        print("\n8. Stopping...")
        ser.write(b'x\n')
        time.sleep(1)
        
        # Test 9: Try pivot right (left motor forward, right motor backward)
        print("\n9. Testing PIVOT RIGHT...")
        print("   Left motor should go forward, right motor backward")
        ser.write(b'd\n')
        time.sleep(3)
        
        # Test 10: Stop
        print("\n10. Stopping...")
        ser.write(b'x\n')
        time.sleep(1)
        
        ser.close()
        print("\n✓ Diagnostic test completed!")
        print("\nIf no motors moved, the issue is likely:")
        print("  • Wrong pin assignments in Arduino code")
        print("  • Loose wiring connections")
        print("  • Faulty ULN2003 driver boards")
        print("  • Motors not properly connected to drivers")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose Motor Issues')
    parser.add_argument('--port', type=str, default='/dev/ttyACM1',
                       help='Arduino serial port')
    
    args = parser.parse_args()
    
    print("Motor Diagnostic Test")
    print("=" * 40)
    print("This will test each motor movement pattern.")
    print("Watch the motors carefully during each test.")
    print("Make sure your Arduino is connected and powered.")
    print()
    
    test_individual_motors(args.port)

if __name__ == "__main__":
    main()
