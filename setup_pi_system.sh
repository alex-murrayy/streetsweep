#!/bin/bash

# Raspberry Pi Setup Script for Trash Detection with Arduino Control
# Sets up mjpg-streamer, Python environment, and system services

echo "=== Raspberry Pi Trash Detection Setup ==="

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-opencv libopencv-dev
sudo apt install -y v4l-utils usbutils
sudo apt install -y git curl wget

# Install mjpg-streamer from GitHub
echo "Installing mjpg-streamer..."
cd /tmp
if [ ! -d "mjpg-streamer" ]; then
    git clone https://github.com/jacksonliam/mjpg-streamer.git
fi

cd mjpg-streamer/mjpg-streamer-experimental
make CMAKE_BUILD_TYPE=Release
sudo make install

# Install additional packages for camera support
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev
sudo apt install -y cmake

# Set up camera permissions
echo "Setting up camera permissions..."
sudo usermod -a -G video pi
sudo usermod -a -G dialout pi

# Create project directory
echo "Setting up project directory..."
mkdir -p /home/pi/streetsweep
cd /home/pi/streetsweep

# Copy your existing code (assuming it's already there or will be copied)
if [ ! -d "imaging" ]; then
    echo "Please copy your imaging directory to /home/pi/streetsweep/"
    echo "The imaging directory should contain your trash detection code"
fi

# Create virtual environment for Python dependencies
echo "Creating Python virtual environment..."
cd /home/pi/streetsweep/imaging
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install numpy opencv-python ultralytics torch torchvision
pip install pyserial pillow matplotlib requests

# Install additional dependencies for advanced detection
pip install scipy scikit-learn

# Create systemd service for mjpg-streamer
echo "Creating mjpg-streamer service..."
sudo tee /etc/systemd/system/mjpg-streamer.service > /dev/null <<EOF
[Unit]
Description=MJPG Streamer for Trash Detection
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 640x480 -f 30" -o "output_http.so -w /usr/local/share/mjpg-streamer/www -p 8080"
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for trash detection
echo "Creating trash detection service..."
sudo tee /etc/systemd/system/trash-detection.service > /dev/null <<EOF
[Unit]
Description=Trash Detection System with Arduino Control
After=network.target mjpg-streamer.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/streetsweep/imaging
ExecStart=/home/pi/streetsweep/imaging/venv/bin/python pi_trash_detection.py --camera 0 --arduino-port /dev/ttyUSB0 --mjpg-streamer
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/streetsweep/imaging/src
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create startup script
echo "Creating startup script..."
tee /home/pi/start_trash_detection.sh > /dev/null <<EOF
#!/bin/bash
cd /home/pi/streetsweep/imaging
source venv/bin/activate
python pi_trash_detection.py --camera 0 --arduino-port /dev/ttyUSB0 --mjpg-streamer --verbose
EOF

chmod +x /home/pi/start_trash_detection.sh

# Create test script
echo "Creating test script..."
tee /home/pi/test_system.sh > /dev/null <<EOF
#!/bin/bash
echo "=== Testing Trash Detection System ==="

echo "1. Testing camera..."
cd /home/pi/streetsweep/imaging
source venv/bin/activate
python pi_trash_detection.py --test-camera

echo "2. Testing Arduino connection..."
python pi_trash_detection.py --test-arduino

echo "3. Testing mjpg-streamer..."
curl -s http://localhost:8080 > /dev/null && echo "mjpg-streamer: OK" || echo "mjpg-streamer: FAILED"

echo "4. Testing video devices..."
ls -la /dev/video*

echo "5. Testing Arduino devices..."
ls -la /dev/ttyUSB* /dev/ttyACM*

echo "=== Test Complete ==="
EOF

chmod +x /home/pi/test_system.sh

# Create camera test script
echo "Creating camera test script..."
tee /home/pi/test_camera.sh > /dev/null <<EOF
#!/bin/bash
echo "=== Camera Test ==="

echo "Available video devices:"
ls -la /dev/video*

echo "Testing camera 0..."
cd /home/pi/streetsweep/imaging
source venv/bin/activate
python pi_trash_detection.py --test-camera --camera 0

echo "Testing mjpg-streamer..."
if curl -s http://localhost:8080 > /dev/null; then
    echo "mjpg-streamer is running"
    echo "Stream URL: http://\$(hostname -I | awk '{print \$1}'):8080"
else
    echo "mjpg-streamer is not running"
    echo "Start it with: sudo systemctl start mjpg-streamer"
fi
EOF

chmod +x /home/pi/test_camera.sh

# Create Arduino test script
echo "Creating Arduino test script..."
tee /home/pi/test_arduino.sh > /dev/null <<EOF
#!/bin/bash
echo "=== Arduino Test ==="

echo "Available Arduino devices:"
ls -la /dev/ttyUSB* /dev/ttyACM*

echo "Testing Arduino connection..."
cd /home/pi/streetsweep/imaging
source venv/bin/activate
python pi_trash_detection.py --test-arduino --arduino-port /dev/ttyUSB0

echo "If Arduino is on different port, try:"
echo "python pi_trash_detection.py --test-arduino --arduino-port /dev/ttyACM0"
EOF

chmod +x /home/pi/test_arduino.sh

# Set up log rotation
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/trash-detection > /dev/null <<EOF
/var/log/trash-detection.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
EOF

# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/trash-detection.log
sudo chown pi:pi /var/log/trash-detection.log

# Enable services
echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable mjpg-streamer.service
sudo systemctl enable trash-detection.service

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Connect your webcam to the Pi"
echo "2. Connect Arduino R4 to USB port"
echo "3. Upload arduino_r4_motor_control.ino to your Arduino"
echo "4. Test the system: ./test_system.sh"
echo "5. Start mjpg-streamer: sudo systemctl start mjpg-streamer"
echo "6. Start trash detection: ./start_trash_detection.sh"
echo ""
echo "Services:"
echo "- mjpg-streamer: http://pi-ip:8080"
echo "- Trash detection: systemctl start trash-detection"
echo ""
echo "To enable auto-start on boot:"
echo "sudo systemctl enable trash-detection"
echo ""
echo "Test scripts:"
echo "- ./test_camera.sh - Test camera functionality"
echo "- ./test_arduino.sh - Test Arduino connection"
echo "- ./test_system.sh - Test entire system"
