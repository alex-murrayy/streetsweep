# Raspberry Pi Trash Detection System with Arduino Control

This guide will help you set up a complete trash detection system on a Raspberry Pi that controls Arduino R4 motors based on detected trash, using mjpg-streamer for webcam input.

## System Overview

The system consists of:

- **Raspberry Pi**: Runs your existing trash detection code
- **Webcam**: Captures video feed via mjpg-streamer
- **Arduino R4**: Controls stepper motors based on Pi commands
- **mjpg-streamer**: Provides remote video streaming and camera access

## Hardware Requirements

### Raspberry Pi

- Raspberry Pi 4 (recommended) or Pi 3B+
- MicroSD card (32GB+ recommended)
- Power supply (5V, 3A)
- Ethernet cable or WiFi connection

### Arduino

- Arduino Uno R4 (or R3)
- ULN2003 Stepper Motor Driver
- 28BYJ-48 Stepper Motor (5V, 4-phase)
- Jumper wires
- Breadboard

### Camera

- USB webcam (compatible with Linux)
- Or Raspberry Pi Camera Module

## Software Setup

### 1. Initial Pi Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git python3-pip python3-venv

# Clone your repository
git clone <your-repo-url> /home/pi/streetsweep
cd /home/pi/streetsweep
```

### 2. Run Setup Script

```bash
# Make setup script executable
chmod +x setup_pi_system.sh

# Run setup (this will take several minutes)
./setup_pi_system.sh
```

### 3. Arduino Setup

1. Connect your Arduino R4 to your computer
2. Open Arduino IDE
3. Upload `controls/arduino_r4_motor_control.ino` to your Arduino
4. Connect Arduino to Pi via USB cable

### 4. Hardware Connections

#### Arduino R4 to Stepper Motor (ULN2003 Driver):

```
Arduino Pin 4  -> ULN2003 IN1
Arduino Pin 5  -> ULN2003 IN2
Arduino Pin 6  -> ULN2003 IN3
Arduino Pin 7  -> ULN2003 IN4
Arduino 5V     -> ULN2003 VCC
Arduino GND    -> ULN2003 GND
```

#### Stepper Motor to ULN2003:

```
Motor Orange -> ULN2003 OUT1
Motor Yellow -> ULN2003 OUT2
Motor Pink   -> ULN2003 OUT3
Motor Blue   -> ULN2004 OUT4
Motor Red    -> 5V (center tap)
```

## Usage

### Local Control (on Pi)

```bash
# Test the system
./test_system.sh

# Test individual components
./test_camera.sh
./test_arduino.sh

# Start video stream only
sudo systemctl start mjpg-streamer

# Start trash detection
./start_trash_detection.sh

# View logs
journalctl -u trash-detection -f
```

### Remote Control (from your computer)

1. **Set up SSH keys** (one-time setup):

```bash
# On your computer
ssh-copy-id pi@<pi-ip-address>
```

2. **Set Pi IP address**:

```bash
export PI_HOST=192.168.1.100  # Replace with your Pi's IP
```

3. **Use remote control script**:

```bash
# Make script executable
chmod +x remote_control.sh

# Start video stream
./remote_control.sh start-stream

# Test system
./remote_control.sh test

# Start trash detection
./remote_control.sh start-detection

# Monitor system in real-time
./remote_control.sh monitor

# Open video stream in browser
./remote_control.sh open-stream
```

## Video Streaming

The system provides remote video streaming via mjpg-streamer:

- **Stream URL**: `http://<pi-ip>:8080`
- **Stream Control**: `http://<pi-ip>:8080/?action=stream`
- **Web Interface**: `http://<pi-ip>:8080/?action=snapshot`

## Motor Control Commands

The Pi sends these commands to the Arduino:

- `f` - Move forward (towards center trash)
- `l` - Move left (towards left trash)
- `r` - Move right (towards right trash)
- `s` - Stop motor
- `h` - Home position
- `t` - Test sequence
- `i` - Status information

## Configuration

### Camera Settings

Edit `pi_trash_detection.py` to adjust:

- Camera source (default: 0)
- Resolution (default: 640x480)
- FPS (default: 30)

### Detection Settings

```bash
# Run with custom settings
python pi_trash_detection.py --camera 0 --confidence 0.6 --advanced --mjpg-streamer
```

### Arduino Port

If Arduino is on different port:

```bash
python pi_trash_detection.py --arduino-port /dev/ttyACM0
```

## Troubleshooting

### Camera Issues

```bash
# List available cameras
ls /dev/video*

# Test camera
python pi_trash_detection.py --test-camera

# Check camera permissions
sudo usermod -a -G video pi
```

### Arduino Connection Issues

```bash
# List USB devices
ls /dev/ttyUSB* /dev/ttyACM*

# Test Arduino connection
python pi_trash_detection.py --test-arduino
```

### Service Issues

```bash
# Check service status
sudo systemctl status mjpg-streamer
sudo systemctl status trash-detection

# Restart services
sudo systemctl restart mjpg-streamer trash-detection

# View service logs
journalctl -u mjpg-streamer -f
journalctl -u trash-detection -f
```

### Performance Issues

```bash
# Check system resources
htop
free -h
df -h

# Reduce camera resolution
# Edit pi_trash_detection.py and change:
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

## Auto-Start on Boot

To start the system automatically when Pi boots:

```bash
# Enable services
sudo systemctl enable mjpg-streamer
sudo systemctl enable trash-detection

# Check if enabled
sudo systemctl is-enabled mjpg-streamer
sudo systemctl is-enabled trash-detection
```

## Network Access

### Find Pi IP Address

```bash
# On Pi
hostname -I

# Or scan network from your computer
nmap -sn 192.168.1.0/24 | grep -B2 "Raspberry Pi"
```

### Port Forwarding (if needed)

If accessing from outside local network:

```bash
# Forward port 8080 to Pi
# Configure on your router's admin panel
```

## File Structure

```
/home/pi/streetsweep/
├── imaging/
│   ├── pi_trash_detection.py    # Main Pi script
│   ├── src/                     # Your existing trash detection code
│   └── venv/                    # Python virtual environment
├── controls/
│   └── arduino_r4_motor_control.ino  # Arduino code
├── setup_pi_system.sh          # Setup script
├── remote_control.sh           # Remote control script
└── README_PI_SETUP.md         # This file
```

## Key Features

### Trash Detection Integration

- Uses your existing trash detection code without modification
- Supports both basic and advanced detection modes
- Configurable confidence thresholds

### Motor Control

- Precise stepper motor control via Arduino R4
- Movement based on trash position (left/center/right)
- Safety features: cooldown periods, consecutive detection requirements

### Remote Monitoring

- Real-time video streaming via mjpg-streamer
- Remote control and monitoring via SSH
- System status and health monitoring

### Robust Operation

- Automatic service restart on failure
- Connection timeout handling
- Comprehensive logging and error reporting

## Support

If you encounter issues:

1. Check the logs: `./remote_control.sh logs`
2. Test components: `./remote_control.sh test`
3. Check system status: `./remote_control.sh status`
4. Restart services: `./remote_control.sh restart`
5. Monitor in real-time: `./remote_control.sh monitor`

The system is designed to be robust and will automatically restart services if they fail.
