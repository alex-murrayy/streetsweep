#!/usr/bin/env python3
"""
Simple test script to send commands to RC Car Arduino
Usage: python3 test_rc_car.py [port] [steer] [throttle]
Example: python3 test_rc_car.py COM3 90 200
         python3 test_rc_car.py /dev/ttyACM0 90 200
"""

import serial
import sys
import time
import glob

def find_arduino_ports():
    """Find available Arduino ports"""
    ports = []
    
    # Windows
    if sys.platform.startswith('win'):
        for i in range(256):
            try:
                port = f'COM{i}'
                ser = serial.Serial(port, timeout=0.1)
                ser.close()
                ports.append(port)
            except (OSError, serial.SerialException):
                pass
    # Linux/Mac
    else:
        port_patterns = ['/dev/ttyACM*', '/dev/ttyUSB*', '/dev/tty.usbmodem*', '/dev/tty.usbserial*']
        for pattern in port_patterns:
            ports.extend(glob.glob(pattern))
    
    return sorted(ports)

def send_command(port, steer, throttle):
    """Send a single command to Arduino"""
    ser = None
    try:
        # Format: <steer,throttle>
        command = f"<{steer},{throttle}>\n"
        
        print(f"Connecting to {port} at 115200 baud...")
        print("(Arduino will reset when serial port opens - this is normal)")
        
        ser = serial.Serial(port=port, baudrate=115200, timeout=2)
        
        # Wait for Arduino to reset and send ready message
        print("Waiting for Arduino to initialize...")
        time.sleep(2.5)  # Give Arduino time to reset and initialize
        
        # Clear any startup messages
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Arduino startup: {startup.strip()}")
        
        print(f"Sending: {command.strip()}")
        print(f"Raw bytes: {command.encode()}")
        
        # Write command
        bytes_written = ser.write(command.encode())
        ser.flush()  # Ensure data is sent immediately
        print(f"✓ Wrote {bytes_written} bytes")
        
        # Read response with timeout
        print("Waiting for Arduino response...")
        time.sleep(0.2)
        
        response_lines = []
        start_time = time.time()
        while time.time() - start_time < 1.0:  # Wait up to 1 second for response
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response_lines.append(line)
                    print(f"Arduino: {line}")
            time.sleep(0.05)
        
        if not response_lines:
            print("⚠ No response from Arduino")
            print("This could mean:")
            print("  - Arduino didn't receive the command")
            print("  - Arduino is not running the correct sketch")
            print("  - Check Serial Monitor in Arduino IDE to see what Arduino sees")
        else:
            print("✓ Command sent and acknowledged!")
        
        return True
        
    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that Arduino is connected")
        print("  2. Check that no other program is using the port (close Arduino IDE Serial Monitor)")
        print("  3. Verify the port name is correct")
        print("  4. Try unplugging and replugging the Arduino")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed")

def interactive_mode(port):
    """Interactive command sending"""
    print(f"\nInteractive mode on {port}")
    print("Enter commands as: <steer,throttle>")
    print("  steer: 45-135 (90 = center)")
    print("  throttle: -255 to 255 (0 = stop, positive = forward, negative = reverse)")
    print("Examples:")
    print("  <90,200>  - center steering, forward at speed 200")
    print("  <90,0>    - stop")
    print("  <45,100>  - steer left, forward")
    print("  <135,-100> - steer right, reverse")
    print("Type 'quit' to exit\n")
    
    ser = None
    try:
        print("Connecting... (Arduino will reset - this is normal)")
        ser = serial.Serial(port=port, baudrate=115200, timeout=1)
        time.sleep(2.5)  # Wait for Arduino reset
        
        # Clear startup messages
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Arduino: {startup.strip()}")
        
        print("Ready! Enter commands:\n")
        
        while True:
            cmd = input("Command: ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                # Send stop command
                ser.write(b"<90,0>\n")
                ser.flush()
                break
            
            # Validate format
            if not (cmd.startswith('<') and cmd.endswith('>')):
                print("Error: Command must be in format <steer,throttle>")
                continue
            
            # Send command
            ser.write(f"{cmd}\n".encode())
            ser.flush()
            
            # Read response
            time.sleep(0.2)
            response_lines = []
            start_time = time.time()
            while time.time() - start_time < 0.5:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response_lines.append(line)
                        print(f"Arduino: {line}")
                time.sleep(0.05)
        
        ser.close()
        print("Stopped.")
        
    except KeyboardInterrupt:
        if ser and ser.is_open:
            ser.write(b"<90,0>\n")
            ser.close()
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")
        if ser and ser.is_open:
            ser.close()

def main():
    if len(sys.argv) == 1:
        # No arguments - show help and list ports
        print("RC Car Arduino Test Script")
        print("\nUsage:")
        print("  python3 test_rc_car.py [port] [steer] [throttle]")
        print("  python3 test_rc_car.py [port] --interactive")
        print("\nExamples:")
        print("  python3 test_rc_car.py COM3 90 200")
        print("  python3 test_rc_car.py /dev/ttyACM0 90 200")
        print("  python3 test_rc_car.py COM3 --interactive")
        print("\nAvailable ports:")
        ports = find_arduino_ports()
        if ports:
            for port in ports:
                print(f"  {port}")
        else:
            print("  (No ports found)")
        print("\nNote: Baud rate is 115200")
        return
    
    port = sys.argv[1]
    
    if len(sys.argv) == 3 and sys.argv[2] == '--interactive':
        interactive_mode(port)
    elif len(sys.argv) == 4:
        try:
            steer = int(sys.argv[2])
            throttle = int(sys.argv[3])
            send_command(port, steer, throttle)
        except ValueError:
            print("Error: steer and throttle must be integers")
    else:
        print("Error: Invalid arguments")
        print("Usage: python3 test_rc_car.py [port] [steer] [throttle]")
        print("   or: python3 test_rc_car.py [port] --interactive")

if __name__ == "__main__":
    main()

