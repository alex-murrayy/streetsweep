# 5-Pin Stepper Motor Control for ELEGoo UNO R3

This directory contains Arduino code for controlling 5-pin stepper motors using an ELEGoo UNO R3 board with ULN2003 driver modules.

## Files

- `stepper_motor_control.ino` - Basic stepper motor control with serial commands
- `advanced_stepper_control.ino` - Advanced stepper motor control with positioning, memory, and microstepping
- `stepper_motor_README.md` - This documentation file

## Hardware Requirements

### Basic Setup
- ELEGoo UNO R3 board
- ULN2003 Stepper Motor Driver Module
- 28BYJ-48 5V Stepper Motor (or compatible 5-pin stepper)
- Jumper wires
- Breadboard (optional)

### Advanced Setup (includes basic setup plus)
- 3x LEDs (for status indicators)
- 3x 220Ω resistors (for LEDs)

## Wiring Diagram

### ULN2003 Stepper Motor Driver Connections

```
ELEGoo UNO R3    ULN2003 Driver    28BYJ-48 Motor
─────────────────────────────────────────────────
Digital Pin 8    → IN1            → OUT1
Digital Pin 9    → IN2            → OUT2
Digital Pin 10   → IN3            → OUT3
Digital Pin 11   → IN4            → OUT4
5V               → VCC            → Center tap
GND              → GND            → (not connected)
                 → OUT1, OUT2, OUT3, OUT4 → Motor coils
```

### Optional LED Indicators (Advanced Version)

```
ELEGoo UNO R3    LED Circuit
─────────────────────────────────────
Digital Pin 4    → LED1 (Active) + 220Ω resistor → GND
Digital Pin 5    → LED2 (Direction) + 220Ω resistor → GND
Digital Pin 6    → LED3 (Position) + 220Ω resistor → GND
```

## Stepper Motor Specifications

### 28BYJ-48 Motor:
- **Voltage**: 5V
- **Steps per Revolution**: 2048 (with gear reduction)
- **Step Angle**: 0.18° (with gear reduction)
- **Gear Ratio**: 1:64
- **Coil Resistance**: ~300Ω per coil
- **Current**: ~100mA per coil

## Software Setup

1. **Install Arduino IDE** (if not already installed)
2. **Connect the ELEGoo UNO R3**
3. **Upload the Code**
4. **Open Serial Monitor** (9600 baud)

## Usage

### Basic Stepper Motor Control

After uploading `stepper_motor_control.ino`, use these commands:

| Command | Function |
|---------|----------|
| `f` | Rotate forward (1 full revolution) |
| `b` | Rotate backward (1 full revolution) |
| `s` | Stop motor |
| `+` | Increase speed (decrease delay) |
| `-` | Decrease speed (increase delay) |
| `1` | Rotate 1/4 turn forward |
| `2` | Rotate 1/2 turn forward |
| `3` | Rotate 3/4 turn forward |
| `4` | Rotate 1 full turn forward |
| `r` | Rotate 1 full turn backward |
| `c` | Rotate 1/4 turn backward |
| `h` | Rotate 1/2 turn backward |
| `t` | Rotate 3/4 turn backward |
| `i` | Show status |
| `p` | Set custom position |

### Advanced Stepper Motor Control

After uploading `advanced_stepper_control.ino`, use these commands:

| Command | Function |
|---------|----------|
| `f` | Rotate forward (1 revolution) |
| `b` | Rotate backward (1 revolution) |
| `s` | Stop motor |
| `+` | Increase speed |
| `-` | Decrease speed |
| `1-9` | Rotate fraction of turn (1/9 to 9/9) |
| `r` | Rotate 1 full turn backward |
| `i` | Show status |
| `p` | Set custom position |
| `g` | Go to saved position |
| `m` | Save current position |
| `l` | List saved positions |
| `c` | Clear saved positions |
| `h` | Toggle half-step mode |
| `a` | Toggle acceleration |
| `z` | Zero position |

## Features

### Basic Version
- ✅ Full-step and half-step modes
- ✅ Forward/backward rotation
- ✅ Speed control
- ✅ Fractional turns (1/4, 1/2, 3/4, full)
- ✅ Custom position setting
- ✅ Serial command interface

### Advanced Version
- ✅ All basic features
- ✅ Position memory (save/recall positions)
- ✅ Microstepping support
- ✅ LED status indicators
- ✅ Position tracking
- ✅ EEPROM storage
- ✅ Zero position function
- ✅ Acceleration control

## Stepper Motor Advantages

1. **Precise Positioning**: Exact step control
2. **High Torque**: Strong holding torque
3. **No Feedback Required**: Open-loop control
4. **Repeatable**: Consistent positioning
5. **Low Speed Control**: Excellent for slow, precise movements

## Common Applications

- **Robotics**: Arm joints, grippers
- **CNC Machines**: X/Y/Z axis control
- **3D Printers**: Extruder positioning
- **Camera Gimbals**: Pan/tilt control
- **Automated Systems**: Precise positioning

## Troubleshooting

### Motor Not Moving
1. Check power connections (5V to VCC)
2. Verify motor connections to ULN2003
3. Ensure proper ground connections
4. Check if motor is getting warm (indicates power)

### Motor Moving Erratically
1. Check step sequence in code
2. Verify all 4 motor pins are connected
3. Try different step delay values
4. Check for loose connections

### Motor Not Holding Position
1. Stepper motors don't hold position when stopped
2. Consider using a servo motor for position holding
3. Or implement a holding current in the code

### Serial Commands Not Working
1. Verify baud rate is set to 9600
2. Check USB connection
3. Ensure correct COM port is selected

## Customization

### Changing Pin Assignments
```cpp
const int IN1_PIN = 8;    // Change to desired pin
const int IN2_PIN = 9;    // Change to desired pin
const int IN3_PIN = 10;   // Change to desired pin
const int IN4_PIN = 11;   // Change to desired pin
```

### Adjusting Speed
```cpp
int stepDelay = 2;  // Decrease for faster movement
int accelerationDelay = 5;  // Acceleration timing
```

### Changing Steps per Revolution
```cpp
int stepsPerRevolution = 2048;  // 28BYJ-48 default
// For other motors, adjust this value
```

## Power Requirements

- **Arduino UNO**: 5V (from USB or external supply)
- **ULN2003 Module**: 5V (from Arduino)
- **28BYJ-48 Motor**: 5V, ~100mA per coil
- **LEDs**: 5V (from Arduino, with current limiting resistors)

## Step Sequences

### Full-Step Mode (4 steps per cycle):
```
Step 1: 1000
Step 2: 0100
Step 3: 0010
Step 4: 0001
```

### Half-Step Mode (8 steps per cycle):
```
Step 1: 1000
Step 2: 1100
Step 3: 0100
Step 4: 0110
Step 5: 0010
Step 6: 0011
Step 7: 0001
Step 8: 1001
```

## Performance Tips

1. **Use appropriate step delay**: Too fast can cause missed steps
2. **Enable microstepping**: For smoother operation
3. **Implement acceleration**: For better control
4. **Save positions**: For repeatable operations
5. **Monitor current**: Stepper motors can get warm

## License

This code is provided as-is for educational and development purposes. Use at your own risk.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all connections match the wiring diagram
3. Ensure proper power supply ratings
4. Test with simple movements first
5. Check motor specifications for your specific stepper motor
