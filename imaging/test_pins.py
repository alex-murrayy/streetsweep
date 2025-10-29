#!/usr/bin/env python3
"""
Test individual Arduino pins to verify motor connections
"""

import serial
import time

def test_arduino_pins(port='/dev/ttyACM1'):
    """Test individual Arduino pins to verify motor connections"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=9600, timeout=2)
        time.sleep(2)
        
        print("✓ Arduino connected!")
        print("\nTesting individual pins...")
        print("Watch your motors - you should see small movements or hear clicking")
        
        # Test left motor pins (8, 9, 10, 11)
        print("\n1. Testing LEFT motor pins (8, 9, 10, 11)...")
        for pin in [8, 9, 10, 11]:
            print(f"   Testing pin {pin}...")
            ser.write(f"p{pin}\n".encode())
            time.sleep(0.5)
        
        # Test right motor pins (4, 5, 6, 7)
        print("\n2. Testing RIGHT motor pins (4, 5, 6, 7)...")
        for pin in [4, 5, 6, 7]:
            print(f"   Testing pin {pin}...")
            ser.write(f"p{pin}\n".encode())
            time.sleep(0.5)
        
        ser.close()
        print("\n✓ Pin test completed!")
        print("If you didn't see any motor movement, check:")
        print("  • Motor wiring to ULN2003 boards")
        print("  • ULN2003 board power connections")
        print("  • Motor connections to ULN2003 boards")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    test_arduino_pins()
