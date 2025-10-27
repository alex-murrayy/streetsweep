#!/usr/bin/env python3
"""
Direct Arduino Command Test
Sends individual commands to Arduino to test motor movement
"""

import serial
import time
import sys

def test_arduino_commands(port='/dev/ttyACM0', baud_rate=9600):
    """Test individual Arduino commands"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("✓ Arduino connected!")
        print("\nTesting individual commands...")
        
        # Test each command with delays
        commands = [
            ('w', 'Forward'),
            ('a', 'Pivot Left'),
            ('d', 'Pivot Right'),
            ('s', 'Reverse'),
            ('x', 'Stop')
        ]
        
        for cmd, description in commands:
            print(f"\nSending '{cmd}' - {description}")
            ser.write(f"{cmd}\n".encode())
            
            # Read any response
            time.sleep(0.5)
            while ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"Arduino response: {response}")
            
            # Wait to see motor movement
            print("Watch for motor movement...")
            time.sleep(2)
            
            # Stop before next command
            ser.write(b'x\n')
            time.sleep(1)
        
        ser.close()
        print("\n✓ Command test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def interactive_test(port='/dev/ttyACM0', baud_rate=9600):
    """Interactive command testing"""
    try:
        print(f"Connecting to Arduino on {port}...")
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        time.sleep(2)
        
        print("✓ Arduino connected!")
        print("\nInteractive mode - send commands manually:")
        print("w = forward, a = pivot left, d = pivot right, s = reverse, x = stop")
        print("q = quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command in ['w', 'a', 'd', 's', 'x']:
                print(f"Sending '{command}'...")
                ser.write(f"{command}\n".encode())
                
                # Read response
                time.sleep(0.5)
                while ser.in_waiting > 0:
                    response = ser.readline().decode().strip()
                    if response:
                        print(f"Arduino: {response}")
            else:
                print("Invalid command. Use w/a/d/s/x or q to quit")
        
        ser.close()
        print("Disconnected.")
        
    except Exception as e:
        print(f"✗ Interactive test failed: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Direct Arduino Command Test')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                       help='Arduino serial port')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    print("=== Direct Arduino Command Test ===")
    print(f"Port: {args.port}")
    print()
    
    if args.interactive:
        interactive_test(args.port)
    else:
        test_arduino_commands(args.port)

if __name__ == "__main__":
    main()
