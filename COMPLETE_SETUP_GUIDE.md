# Complete Trash Detection System Setup Guide

## Overview

This guide will help you recreate a complete trash detection system that:

- Detects trash using YOLO computer vision
- Controls dual stepper motors via Arduino Uno R4
- Runs on Raspberry Pi with headless operation
- Provides both automatic and manual motor control

## Hardware Requirements

### Raspberry Pi Setup

- Raspberry Pi 4 (recommended) or Pi 3B+
- MicroSD card (32GB+)
- Power supply (5V, 3A+)
- Webcam (USB or Pi Camera)
- Ethernet cable or WiFi connection

### Arduino Setup

- Arduino Uno R4 (WiFi or Minima)
- 2x 28BYJ-48 stepper motors
- 2x ULN2003 stepper motor drivers
- 5V power supply (2A+ for motors)
- Jumper wires
- Breadboard

### Motor Wiring

```
Arduino Uno R4 Pinout:
- Left Motor (A): IN1→8, IN2→9, IN3→10, IN4→11
- Right Motor (B): IN1→4, IN2→5, IN3→6, IN4→7
- Power: 5V supply to motors (separate from Arduino)
- Ground: Connect all grounds together
```

## Software Setup

### 1. Raspberry Pi Initial Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git arduino-cli

# Install Arduino CLI
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
source ~/.bashrc

# Install Arduino board packages
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli core install arduino:renesas_uno
```

### 2. Clone and Setup Project

```bash
# Clone repository
git clone <your-repo-url> streetsweep
cd streetsweep/imaging

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install opencv-python numpy ultralytics torch torchvision pyserial pillow matplotlib requests
```

### 3. Arduino Sketch Setup

```bash
# Create Arduino sketch directory
mkdir -p ~/streetsweep/controls/dual_stepper_wasd

# Copy the WASD sketch
cp dual_stepper_wasd.ino ~/streetsweep/controls/dual_stepper_wasd/dual_stepper_wasd.ino
```

## Arduino Sketch (dual_stepper_wasd.ino)

```cpp
/*
 * Dual 28BYJ-48 (ULN2003) "rear wheels" with WASD drive on Arduino Uno R4
 * Power motors from a regulated 5V (>=2A) supply. Tie ALL grounds together.
 *
 * Pins:
 * Motor Left (A): IN1..IN4 → 8, 9, 10, 11
 * Motor Right (B): IN1..IN4 → 4, 5, 6, 7
 *
 * Controls (Serial Monitor @ 9600 baud):
 * W = forward S = reverse
 * A = pivot left D = pivot right
 * X or ' ' (space) = stop
 * Q = slower E = faster
 * 1..5 = speed presets (lowest→highest)
 */

// ---------- Config ----------
const int stepsPerRev = 2048;     // 28BYJ-48 (half-steps)
const int MIN_SPS = 100;          // min steps/sec
const int MAX_SPS = 1600;         // max steps/sec
int baseSPS = 800;                // default steps/sec (speed preset)

// ---------- Pin maps ----------
const int leftPins[4]  = {8, 9, 10, 11}; // Left wheel (Motor A)
const int rightPins[4] = {4, 5, 6, 7};   // Right wheel (Motor B)

// 8-step half-step sequence
const uint8_t seq[8][4] = {
  {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
  {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
};

struct Wheel {
  const int* pins;                    // 4-pin array
  int idx = 0;                        // current sequence index 0..7
  int sps = 0;                        // signed steps/sec (direction in sign)
  unsigned long lastStepUs = 0;       // last step timestamp
  unsigned long intervalUs = 0;       // microseconds between steps (abs)
  bool energized = false;             // coils currently driven
};

Wheel left;
Wheel right;

void setupWheels() {
  left.pins  = leftPins;
  left.idx   = 0;
  left.sps   = 0;
  left.lastStepUs = 0;
  left.intervalUs = 0;
  left.energized  = false;

  right.pins  = rightPins;
  right.idx   = 0;
  right.sps   = 0;
  right.lastStepUs = 0;
  right.intervalUs = 0;
  right.energized  = false;
}

// ---------- Helpers ----------
void pinsModeOut(const int p[4]) {
  for (int i=0; i<4; i++) pinMode(p[i], OUTPUT);
}
void coilsOff(const int p[4]) {
  for (int i=0; i<4; i++) digitalWrite(p[i], LOW);
}
inline unsigned long spsToIntervalUs(int spsAbs) {
  if (spsAbs < 1) spsAbs = 1; // avoid div0
  return (unsigned long)(1000000UL / (unsigned long)spsAbs);
}

// Set wheel speed in steps/sec (signed: + = forward, - = backward, 0 = stop)
void setWheelSpeed(Wheel &w, int sps) {
  w.sps = sps;
  int a = abs(sps);
  if (a == 0) {
    coilsOff(w.pins);
    w.energized = false;
    w.intervalUs = 0;
  } else {
    if (a < MIN_SPS) a = MIN_SPS;
    if (a > MAX_SPS) a = MAX_SPS;
    w.intervalUs = spsToIntervalUs(a);
    if (!w.energized) {
      // Energize with current pattern so the first step has valid state
      for (int i=0; i<4; i++) digitalWrite(w.pins[i], seq[w.idx][i]);
      w.energized = true;
      w.lastStepUs = micros();
    }
  }
}

// Service one wheel: step when time interval elapsed
void serviceWheel(Wheel &w) {
  if (w.sps == 0) return;
  unsigned long now = micros();
  if ((unsigned long)(now - w.lastStepUs) < w.intervalUs) return;
  w.lastStepUs = now;

  // Direction: +1 for forward, -1 for backward
  int delta = (w.sps > 0) ? 1 : -1;
  w.idx = (w.idx + delta) & 0x7;  // wrap 0..7 quickly

  // Output new pattern
  for (int i=0; i<4; i++) digitalWrite(w.pins[i], seq[w.idx][i]);
}

// High-level driving modes
void driveStop() {
  setWheelSpeed(left, 0);
  setWheelSpeed(right, 0);
  Serial.println("STOP");
}

void driveForward() {
  setWheelSpeed(left,  +baseSPS);
  setWheelSpeed(right, +baseSPS);
  Serial.print("FORWARD @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void driveReverse() {
  setWheelSpeed(left,  -baseSPS);
  setWheelSpeed(right, -baseSPS);
  Serial.print("REVERSE @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void drivePivotLeft() {   // left wheel backward, right forward
  setWheelSpeed(left,  -baseSPS);
  setWheelSpeed(right, +baseSPS);
  Serial.print("PIVOT LEFT @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void drivePivotRight() {  // left wheel forward, right backward
  setWheelSpeed(left,  +baseSPS);
  setWheelSpeed(right, -baseSPS);
  Serial.print("PIVOT RIGHT @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void printHelp() {
  Serial.println("\n=== WASD Drive ===");
  Serial.println("W forward | S reverse | A pivot left | D pivot right");
  Serial.println("X or Space = stop | Q slower | E faster | 1..5 speed presets");
  Serial.print("Current speed preset (steps/sec): "); Serial.println(baseSPS);
  Serial.println("===================\n");
}

// ---------- Arduino ----------
void setup() {
  setupWheels();
  Serial.begin(9600);
  pinsModeOut(left.pins);
  pinsModeOut(right.pins);
  coilsOff(left.pins);
  coilsOff(right.pins);
  printHelp();
}

void loop() {
  // keyboard input
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {
      case 'w': case 'W': driveForward(); break;
      case 's': case 'S': driveReverse(); break;
      case 'a': case 'A': drivePivotLeft(); break;
      case 'd': case 'D': drivePivotRight(); break;
      case 'x': case 'X': case ' ': driveStop(); break;

      // speed trim
      case 'q': case 'Q':
        baseSPS -= 100;
        if (baseSPS < MIN_SPS) baseSPS = MIN_SPS;
        Serial.print("Speed ↓ -> "); Serial.println(baseSPS);
        // if moving, update to new speed
        if (left.sps  != 0) setWheelSpeed(left,  (left.sps  > 0 ? +baseSPS : -baseSPS));
        if (right.sps != 0) setWheelSpeed(right, (right.sps > 0 ? +baseSPS : -baseSPS));
        break;

      case 'e': case 'E':
        baseSPS += 100;
        if (baseSPS > MAX_SPS) baseSPS = MAX_SPS;
        Serial.print("Speed ↑ -> "); Serial.println(baseSPS);
        if (left.sps  != 0) setWheelSpeed(left,  (left.sps  > 0 ? +baseSPS : -baseSPS));
        if (right.sps != 0) setWheelSpeed(right, (right.sps > 0 ? +baseSPS : -baseSPS));
        break;

      // speed presets
      case '1': baseSPS = 300;  Serial.println("Preset 1 -> 300 sps");  break;
      case '2': baseSPS = 600;  Serial.println("Preset 2 -> 600 sps");  break;
      case '3': baseSPS = 800;  Serial.println("Preset 3 -> 800 sps");  break;
      case '4': baseSPS = 1000; Serial.println("Preset 4 -> 1000 sps"); break;
      case '5': baseSPS = 1200; Serial.println("Preset 5 -> 1200 sps"); break;

      case 'h': case 'H': printHelp(); break;
      default: /* ignore */ break;
    }
  }

  // service both wheels without blocking
  serviceWheel(left);
  serviceWheel(right);
}
```

## Upload Arduino Sketch

```bash
# Compile the sketch
arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi ~/streetsweep/controls/dual_stepper_wasd

# Upload to Arduino (put Arduino in DFU mode first - double-press reset)
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:renesas_uno:unor4wifi ~/streetsweep/controls/dual_stepper_wasd
```

## Usage Instructions

### Manual Control

```bash
# Test Arduino connection
python3 pi_trash_detection.py --test-arduino

# Manual control via interactive mode
python3 arduino_control.py --interactive
```

**Manual Commands:**

- `w` = Forward (both motors)
- `s` = Reverse (both motors)
- `a` = Pivot left
- `d` = Pivot right
- `x` = Stop
- `q` = Slower speed
- `e` = Faster speed
- `1-5` = Speed presets
- `h` = Help

### Automatic Trash Detection

```bash
# Run with GUI (if display available)
python3 pi_trash_detection.py --verbose

# Run headless (no GUI - recommended for Pi)
python3 pi_trash_detection.py --verbose --headless
```

**Automatic Behavior:**

- **Trash detected** → Both motors move forward
- **No trash detected** → Motors stop (after cooldown)
- **High confidence detection** → Forward movement
- **Low confidence detection** → No movement (filtered out)

### Configuration Options

```bash
# Adjust confidence threshold (0.0-1.0)
python3 pi_trash_detection.py --confidence 0.7 --headless

# Use different camera
python3 pi_trash_detection.py --camera 1 --headless

# Use mjpg-streamer
python3 pi_trash_detection.py --mjpg-streamer --headless

# Advanced detection model
python3 pi_trash_detection.py --advanced --headless
```

## Troubleshooting

### Arduino Connection Issues

```bash
# Check Arduino port
ls /dev/ttyACM* /dev/ttyUSB*

# Check Arduino connection
python3 -c "
import serial
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)
ser.write(b'h\n')
time.sleep(0.5)
while ser.in_waiting > 0:
    print(ser.readline().decode().strip())
ser.close()
"
```

### Upload Issues

```bash
# Put Arduino R4 in DFU mode
# Double-press the reset button quickly
# LED should blink rapidly
# Then immediately run upload command

# Check board type
arduino-cli board listall | grep -i r4
```

### Camera Issues

```bash
# Test camera
python3 pi_trash_detection.py --test-camera

# Check available cameras
ls /dev/video*
```

### Performance Issues

```bash
# Monitor system resources
htop

# Check Python dependencies
pip list | grep -E "(opencv|numpy|ultralytics)"
```

## System Architecture

```
Raspberry Pi
├── Camera Input (USB/Pi Camera)
├── YOLO Trash Detection
├── Motor Control Logic
└── Serial Communication → Arduino R4
    ├── Left Stepper Motor (28BYJ-48)
    └── Right Stepper Motor (28BYJ-48)
```

## File Structure

```
streetsweep/
├── imaging/
│   ├── pi_trash_detection.py      # Main system
│   ├── arduino_control.py         # Manual control
│   ├── requirements.txt           # Python dependencies
│   └── src/trash_detector/        # Detection modules
├── controls/
│   └── dual_stepper_wasd.ino      # Arduino sketch
└── README.md                      # Project documentation
```

## Safety Notes

1. **Power Supply**: Use separate 5V supply for motors (2A+)
2. **Ground Connection**: Connect all grounds together
3. **Motor Current**: 28BYJ-48 motors draw ~240mA each
4. **Heat Management**: Motors can get hot during extended use
5. **Emergency Stop**: Always have a way to disconnect power

## Performance Tips

1. **Headless Mode**: Use `--headless` for better performance
2. **Confidence Threshold**: Adjust `--confidence` to reduce false positives
3. **Frame Rate**: System runs at ~30 FPS on Pi 4
4. **Detection Cooldown**: 3-second cooldown prevents excessive motor movements
5. **Consecutive Detections**: Requires 2 consecutive detections before moving

## Next Steps

1. **Calibration**: Adjust motor speeds and detection thresholds
2. **Navigation**: Add obstacle avoidance
3. **Collection**: Implement trash collection mechanism
4. **Mapping**: Add path planning and mapping
5. **Remote Control**: Add web interface for remote monitoring

---

**Happy Building!** 🚀
