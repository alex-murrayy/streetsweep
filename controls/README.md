# Arduino Motor Control for ELEGoo UNO R3

This directory contains Arduino code for controlling DC motors using an ELEGoo UNO R3 board. The code supports both basic and advanced motor control features.

## Files

- `motor_control.ino` - Basic motor control with serial commands
- `advanced_motor_control.ino` - Advanced motor control with acceleration, safety features, and LED indicators
- `README.md` - This documentation file

## Hardware Requirements

### Basic Setup

- ELEGoo UNO R3 board
- L298N Motor Driver Module
- DC Motor (6-12V)
- External power supply (6-12V for motor)
- Jumper wires
- Breadboard (optional)

### Advanced Setup (includes basic setup plus)

- 3x LEDs (for direction indicators)
- 3x 220Ω resistors (for LEDs)

## Wiring Diagram

### L298N Motor Driver Connections

```
ELEGoo UNO R3    L298N Motor Driver
─────────────────────────────────────
Digital Pin 2    → IN1
Digital Pin 3    → IN2
Digital Pin 9    → ENA (PWM)
5V               → VCC
GND              → GND
                 → VM (External 6-12V supply)
                 → OUT1, OUT2 (Motor terminals)
```

### Optional LED Indicators (Advanced Version)

```
ELEGoo UNO R3    LED Circuit
─────────────────────────────────────
Digital Pin 4    → LED1 (Forward) + 220Ω resistor → GND
Digital Pin 5    → LED2 (Backward) + 220Ω resistor → GND
Digital Pin 6    → LED3 (Stop) + 220Ω resistor → GND
```

## Software Setup

1. **Install Arduino IDE** (if not already installed)

   - Download from: https://www.arduino.cc/en/software

2. **Connect the ELEGoo UNO R3**

   - Connect via USB cable
   - Select the correct board: Tools → Board → Arduino Uno
   - Select the correct port: Tools → Port → (your COM port)

3. **Upload the Code**
   - Open the desired `.ino` file
   - Click the Upload button (→) or press Ctrl+U

## Usage

### Basic Motor Control

After uploading `motor_control.ino`, open the Serial Monitor (Tools → Serial Monitor) and use these commands:

| Command | Function                        |
| ------- | ------------------------------- |
| `f`     | Move forward                    |
| `b`     | Move backward                   |
| `s`     | Stop motor                      |
| `+`     | Increase speed                  |
| `-`     | Decrease speed                  |
| `0-9`   | Set speed level (0=stop, 9=max) |

### Advanced Motor Control

After uploading `advanced_motor_control.ino`, use these commands:

| Command | Function                                |
| ------- | --------------------------------------- |
| `f`     | Move forward                            |
| `b`     | Move backward                           |
| `s`     | Stop motor                              |
| `+`     | Increase speed                          |
| `-`     | Decrease speed                          |
| `0-9`   | Set speed level (0=stop, 9=max)         |
| `e`     | Emergency stop (press again to release) |
| `r`     | Reset to defaults                       |
| `i`     | Show status information                 |
| `a`     | Toggle auto-acceleration                |

## Features

### Basic Version

- ✅ PWM speed control (0-255)
- ✅ Direction control (forward/backward/stop)
- ✅ Serial command interface
- ✅ Speed adjustment with +/- commands
- ✅ Speed level setting (0-9)

### Advanced Version

- ✅ All basic features
- ✅ Smooth acceleration/deceleration
- ✅ LED direction indicators
- ✅ Emergency stop functionality
- ✅ Safety timeout (auto-stop after 30 seconds of inactivity)
- ✅ Settings persistence (saved to EEPROM)
- ✅ Status monitoring
- ✅ Reset to defaults

## Safety Features

1. **Emergency Stop**: Press 'e' to immediately stop the motor
2. **Safety Timeout**: Motor automatically stops after 30 seconds of no commands
3. **Speed Limits**: Minimum and maximum speed constraints
4. **Direction Validation**: Prevents invalid motor states

## Troubleshooting

### Motor Not Moving

1. Check power connections (external supply to VM)
2. Verify motor connections to OUT1 and OUT2
3. Ensure proper ground connections
4. Check if motor voltage matches supply voltage

### Serial Commands Not Working

1. Verify baud rate is set to 9600
2. Check USB connection
3. Ensure correct COM port is selected
4. Try closing and reopening Serial Monitor

### Motor Moving in Wrong Direction

1. Swap the motor connections on OUT1 and OUT2
2. Or modify the code to swap IN1 and IN2 logic

### LED Indicators Not Working (Advanced Version)

1. Check LED polarity (long leg = positive)
2. Verify resistor connections
3. Ensure proper ground connections

## Customization

### Changing Pin Assignments

Modify these constants at the top of the code:

```cpp
const int IN1_PIN = 2;    // Change to desired pin
const int IN2_PIN = 3;    // Change to desired pin
const int ENA_PIN = 9;    // Change to desired pin (must be PWM capable)
```

### Adjusting Speed and Acceleration

```cpp
int maxSpeed = 255;           // Maximum PWM value
int minSpeed = 50;            // Minimum speed to overcome friction
const int ACCELERATION_STEP = 5;      // Speed change per step
const int ACCELERATION_DELAY = 50;    // Delay between steps (ms)
```

### Safety Timeout

```cpp
const unsigned long SAFETY_TIMEOUT = 30000;  // 30 seconds (change as needed)
```

## Power Requirements

- **Arduino UNO**: 5V (from USB or external supply)
- **L298N Module**: 5V (from Arduino)
- **Motor**: 6-12V (external supply required)
- **LEDs**: 5V (from Arduino, with current limiting resistors)

## License

This code is provided as-is for educational and development purposes. Use at your own risk.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Verify all connections match the wiring diagram
3. Ensure proper power supply ratings
4. Test with a simple LED first to verify Arduino functionality
