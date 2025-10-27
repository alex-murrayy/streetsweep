# StreetSweep - Autonomous Trash Detection Robot

An intelligent trash detection system that combines computer vision with Arduino motor control for autonomous cleanup operations.

## 🚀 Features

- **AI-Powered Trash Detection**: Uses YOLO models to identify various types of litter
- **Arduino Motor Control**: Dual stepper motor system with WASD controls
- **Raspberry Pi Integration**: Remote operation with video streaming
- **Real-time Processing**: Live camera feed with motor response
- **Modular Design**: Easy to extend and customize

## 📁 Project Structure

```
streetsweep/
├── imaging/                    # AI trash detection system
│   ├── src/trash_detector/    # Core detection modules
│   ├── main.py               # Main detection script
│   ├── pi_trash_detection.py # Raspberry Pi integration
│   └── requirements.txt      # Python dependencies
├── controls/                  # Arduino motor control
│   ├── dual_stepper_wasd.ino # Dual motor WASD control
│   ├── stepper_motor_control.ino # Single motor control
│   └── README.md             # Motor control documentation
├── setup_pi_system.sh        # Pi setup script
├── remote_control.sh         # Remote control script
└── README_PI_SETUP.md        # Pi setup documentation
```

## 🛠️ Quick Start

### 1. Arduino Setup

- Upload `controls/dual_stepper_wasd.ino` to your Arduino
- Connect dual stepper motors with ULN2003 drivers
- Wire according to pin mappings in the sketch

### 2. Raspberry Pi Setup

```bash
# Run setup script
chmod +x setup_pi_system.sh
./setup_pi_system.sh

# Test system
cd imaging
python3 pi_trash_detection.py --test-arduino
```

### 3. Run Detection System

```bash
# Start trash detection with motor control
python3 pi_trash_detection.py --verbose
```

## 🎮 Controls

### Arduino Motor Commands

- `W` - Move forward
- `A` - Pivot left
- `D` - Pivot right
- `S` - Reverse
- `X` - Stop
- `1-5` - Speed presets

### Pi Script Options

```bash
python3 pi_trash_detection.py --help
```

## 🔧 Hardware Requirements

- **Arduino Uno R3/R4** with dual stepper motors
- **Raspberry Pi 4** (recommended)
- **USB Webcam** or Pi Camera
- **ULN2003 Stepper Motor Drivers**
- **28BYJ-48 Stepper Motors**

## 📖 Documentation

- [Pi Setup Guide](README_PI_SETUP.md) - Complete Raspberry Pi setup
- [Motor Control](controls/README.md) - Arduino motor control details
- [Remote Control](remote_control.sh) - Remote operation commands

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. See individual files for specific licensing information.

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Note**: This system is designed for educational and research purposes. Always follow local regulations when operating autonomous vehicles.
