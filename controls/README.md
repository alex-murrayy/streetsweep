# Arduino Motor Control

This directory contains Arduino sketches for controlling stepper motors in the StreetSweep trash detection robot.

## Available Sketches

### `rc_car_arduino.ino` (RC Car Controller)

RC car controller for Arduino R4 with servo steering and motor driver.

**Features:**
- Servo-based steering (45-135 degrees, 90 = center)
- Motor speed control (-255 to 255, 0 = stop)
- Safety watchdog (auto-stops after 500ms without commands)
- Serial command interface

**Wiring:**
```
Servo: Signal → Pin 9
Motor PWM: → Pin 5
Motor IN1: → Pin 6
Motor IN2: → Pin 7
```

**Command Format:**
- `<steer,throttle>` where:
  - `steer`: 45-135 (90 = center)
  - `throttle`: -255 to 255 (0 = stop, positive = forward, negative = reverse)
- Example: `<90,200>` = center steering, forward at speed 200
- Example: `<90,0>` = stop
- Example: `<45,-100>` = steer left, reverse at speed 100

**Serial Settings:**
- Baud rate: **115200** (important!)
- Line ending: Newline recommended but not required

**Testing:**
```bash
# Using the test script
python3 test_rc_car.py COM3 90 200        # Windows
python3 test_rc_car.py /dev/ttyACM0 90 200  # Linux/Mac
python3 test_rc_car.py COM3 --interactive   # Interactive mode

# Or using Python directly
python3 -c "import serial; s=serial.Serial('COM3', 115200); s.write(b'<90,200>\n')"
```

**Troubleshooting RC Car:**
1. **Nothing happens when sending commands:**
   - Verify baud rate is **115200** (not 9600!)
   - Check serial port name (COM3 on Windows, /dev/ttyACM0 on Linux)
   - Open Serial Monitor in Arduino IDE to see debug messages
   - Commands must be in format `<steer,throttle>` (with angle brackets)
   - Watchdog stops car after 500ms - send commands continuously

2. **Arduino not responding:**
   - Upload the sketch again
   - Check Serial Monitor shows "RC Car Controller Ready"
   - Try sending `<90,0>` to stop/reset
   - Check wiring connections

3. **Commands not parsed correctly:**
   - Must include angle brackets: `<90,200>` not `90,200`
   - No spaces: `<90, 200>` won't work, use `<90,200>`
   - Check Serial Monitor for "Parse error" messages

4. **Arduino receives commands but motors don't move:**
   - **Upload `rc_car_hardware_test.ino` first** to test hardware independently
   - Check power supply:
     - Servo needs 5V power (usually from Arduino or external supply)
     - Motor needs external power supply (NOT from Arduino USB)
     - All grounds must be connected together (Arduino GND, motor driver GND, servo GND, power supply GND)
   - Verify wiring:
     - Servo signal wire → Pin 9
     - Motor driver IN1 → Pin 6
     - Motor driver IN2 → Pin 7
     - Motor driver PWM/ENA → Pin 5
   - Check motor driver module:
     - Some modules need enable pin set HIGH
     - Verify motor driver is getting power (LED should light if present)
     - Test motor directly with battery to verify it works
   - Check Serial Monitor output - it now shows pin states being set
   - Try sending `<90,255>` for maximum speed to test
   - If servo doesn't move: check servo power and signal wire
   - If motor doesn't move: check motor driver power, wiring, and enable pin

### `dual_stepper_wasd.ino` (Recommended)

Dual stepper motor control with WASD drive system for robot movement.

**Features:**

- Dual 28BYJ-48 stepper motors with ULN2003 drivers
- WASD control scheme
- Speed control and presets
- Non-blocking motor control

**Wiring:**

```
Motor Left  (A): IN1..IN4 → Pins 8, 9, 10, 11
Motor Right (B): IN1..IN4 → Pins 4, 5, 6, 7
```

**Commands:**

- `W` - Forward
- `A` - Pivot left
- `D` - Pivot right
- `S` - Reverse
- `X` - Stop
- `Q` - Slower
- `E` - Faster
- `1-5` - Speed presets
- `H` - Help

### `stepper_motor_control.ino`

Single stepper motor control for basic movement.

**Features:**

- Single 28BYJ-48 stepper motor
- Precise positioning
- Speed control
- Position memory

**Wiring:**

```
Motor: IN1..IN4 → Pins 8, 9, 10, 11
```

## Power Requirements

- **5V regulated power supply** (2A or higher)
- **All grounds must be connected together**
- **Motors powered from external supply**

## Upload Instructions

1. Connect Arduino to computer
2. Open Arduino IDE
3. Select correct board and port
4. Upload the desired sketch
5. Open Serial Monitor (9600 baud) to test

## Troubleshooting

### Motors Not Moving

- Check power supply (5V, 2A+)
- Verify all ground connections
- Check motor wiring
- Test with Serial Monitor commands

### Upload Issues

- Ensure correct board selected
- Check USB connection
- Try different USB port
- Reset Arduino before upload

### Communication Issues

- Verify baud rate (9600)
- Check serial port permissions
- Test with Serial Monitor first

## Integration with Pi

The Pi script `pi_trash_detection.py` automatically sends commands to the Arduino based on trash detection results:

- Trash on left → `A` (pivot left)
- Trash in center → `W` (forward)
- Trash on right → `D` (pivot right)
- No trash → `X` (stop)
