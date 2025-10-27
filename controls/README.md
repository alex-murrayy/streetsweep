# Arduino Motor Control

This directory contains Arduino sketches for controlling stepper motors in the StreetSweep trash detection robot.

## Available Sketches

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
