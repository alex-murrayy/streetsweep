Project CleanSweep 🤖♻️
An open-source software stack for an autonomous robot designed to detect, classify, and collect litter from roadsides. This project integrates computer vision, path planning, and robotic manipulation to create a comprehensive solution for environmental cleanup.

## 🎯 Core Features

Real-time Litter Detection: Utilizes a Convolutional Neural Network (CNN) to identify and classify various types of trash (e.g., bottles, cans, paper) from a live camera feed.

Autonomous Navigation: Employs LiDAR and GPS for localization, mapping, and navigating complex roadside environments safely.

Intelligent Path Planning: Implements algorithms like A\* and Dynamic Window Approach (DWA) to generate efficient and collision-free paths to targeted debris.

Robotic Arm Manipulation: Controls a multi-DOF robotic arm to precisely pick up identified litter and place it in an onboard storage container.

Web-based Monitoring Dashboard: A remote dashboard built for real-time video streaming, robot status monitoring, and manual override control.

## 📁 Project Structure

```
streetsweep/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── trash_detector.py           # Standalone trash detection script
└── [Future ROS packages]
    ├── cleansweep_perception   # ROS perception node
    ├── cleansweep_planning     # ROS planning node
    ├── cleansweep_control      # ROS control node
    └── cleansweep_description  # Robot URDF models
```

## 🛠️ System Architecture

The software is built on the Robot Operating System (ROS) and is organized into several key nodes that communicate via topics and services.

Perception Node (/perception_node)

Subscribes to: /camera/image_raw, /lidar/scan

Publishes to: /detected_objects, /obstacles

Function: Processes raw sensor data. It runs the computer vision model on incoming video frames to detect and locate litter, and it uses LiDAR data to identify static and dynamic obstacles.

Planning Node (/planning_node)

Subscribes to: /robot_pose, /detected_objects, /obstacles

Publishes to: /cmd_vel (for navigation), /arm_goal (for manipulation)

Function: This is the brain of the operation. It takes the locations of detected litter and obstacles to compute the optimal path for the robot's base and the necessary joint angles for the robotic arm.

Control Node (/control_node)

Subscribes to: /cmd_vel, /arm_goal

Function: The low-level controller that translates velocity commands and arm goals into electrical signals for the motors and servos.

Communications Node (/comm_node)

Function: Manages the connection to the web dashboard via a WebSocket server, relaying telemetry and receiving control commands. This architecture allows for potential future expansion to a multi-robot system, coordinating tasks between agents.

## 🚀 Technologies Used

Platform: Robot Operating System (ROS Noetic)

Languages: Python, C++, Go (Golang)

AI / Computer Vision: TensorFlow, Keras, OpenCV

Simulation: Gazebo, RViz

Web Dashboard:

Backend: Go

Frontend: React, Material-UI

Communication: WebSockets

## ⚙️ Getting Started

### Prerequisites

Ubuntu 20.04

ROS Noetic

Python 3.8+

NVIDIA GPU with CUDA and cuDNN (for hardware-accelerated model inference)

### Installation

Clone the repository into your catkin workspace:

Bash

cd ~/catkin_ws/src
git clone https://github.com/your-username/Project-CleanSweep.git
Install Python dependencies:

Bash

cd Project-CleanSweep
pip install -r requirements.txt
Build the ROS package:

Bash

cd ~/catkin_ws
catkin_make
source devel/setup.bash

## ▶️ Usage

### Trash Detection Script (Standalone)

The project includes a standalone Python script (`trash_detector.py`) for real-time trash detection that can be run independently of the full ROS system. This script serves as both a standalone tool for testing and development, and as a foundation for the ROS perception node.

#### Prerequisites

- Python 3.8 or higher
- Webcam or video file for input
- NVIDIA GPU (optional, for better performance)

#### Installation

**For macOS (including Apple Silicon):**

```bash
# Install core dependencies (excludes ROS packages)
pip install -r requirements.txt
```

**For Linux/Ubuntu (full ROS support):**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install ROS Noetic (if not already installed)
sudo apt update
sudo apt install ros-noetic-desktop-full

# Source ROS environment
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install additional ROS packages for this project
sudo apt install ros-noetic-cv-bridge ros-noetic-sensor-msgs ros-noetic-geometry-msgs
```

**For Windows:**

```bash
# Install core dependencies (ROS not supported on Windows)
pip install -r requirements.txt
```

#### Quick Start

1. **Run with Webcam:**

   ```bash
   python trash_detector.py --source 0
   ```

2. **Run with Video File:**

   ```bash
   python trash_detector.py --source path/to/your/video.mp4
   ```

3. **Save Detection Output:**

   ```bash
   python trash_detector.py --source 0 --output detected_trash.mp4
   ```

#### Command Line Options

| Option         | Description                              | Default                        | Example                              |
| -------------- | ---------------------------------------- | ------------------------------ | ------------------------------------ |
| `--source`     | Video source (camera index or file path) | `0` (webcam)                   | `--source 1` or `--source video.mp4` |
| `--model`      | Path to custom trained model             | `None` (uses simple detection) | `--model trash_model.weights`        |
| `--confidence` | Detection confidence threshold (0.0-1.0) | `0.5`                          | `--confidence 0.7`                   |
| `--output`     | Save output video to file                | `None`                         | `--output results.mp4`               |
| `--verbose`    | Enable detailed logging                  | `False`                        | `--verbose`                          |

#### Usage Examples

**Basic webcam detection:**

```bash
python trash_detector.py
```

**High-confidence detection with custom model:**

```bash
python trash_detector.py --source 0 --model custom_trash_model.weights --confidence 0.8
```

**Process video file and save results:**

```bash
python trash_detector.py --source street_footage.mp4 --output trash_detected.mp4 --verbose
```

**Use different camera (if multiple cameras available):**

```bash
python trash_detector.py --source 1
```

#### Detection Features

- **Real-time Processing**: Processes video feed at camera's native FPS
- **Multiple Detection Methods**:
  - Simple color/contour analysis (fallback)
  - YOLO-based detection (with custom models)
- **Trash Classification**: Identifies bottles, cans, paper, plastic, and other common litter
- **Confidence Scoring**: Filters detections based on confidence threshold
- **Visual Output**: Displays bounding boxes, labels, and detection centers
- **Performance Monitoring**: Shows FPS and detection statistics
- **ROS Integration Ready**: Compatible with the full CleanSweep system

#### Controls

- **Press 'q'** to quit the detection window
- **Ctrl+C** to stop processing from command line

#### Output Information

The script provides real-time feedback including:

- Frame count and processing speed (FPS)
- Number of detections per frame
- Detection details (class, confidence, location)
- Performance statistics on exit

#### Troubleshooting

**Dependency Installation Issues:**

_On macOS with Apple Silicon:_

```bash
# If you get tensorflow installation errors, install the macOS-specific version
pip uninstall tensorflow
pip install tensorflow-macos tensorflow-metal
```

_If ROS packages fail to install:_

```bash
# ROS packages are not available via pip on macOS/Windows
# The script will work without them - ROS integration is optional
# Only install ROS packages if you're on Ubuntu and need full ROS functionality
```

**Camera not found:**

```bash
# Try different camera indices
python trash_detector.py --source 1
python trash_detector.py --source 2
```

**Low detection accuracy:**

```bash
# Lower confidence threshold
python trash_detector.py --source 0 --confidence 0.3
```

**Performance issues:**

- Ensure you have the latest OpenCV installed
- Consider using a GPU-accelerated version of TensorFlow
- Reduce video resolution if processing is too slow
- On Apple Silicon, TensorFlow Metal can provide GPU acceleration

### Running the Full ROS Simulation

To launch the robot model in a simulated roadside environment using Gazebo and visualize the sensor data in RViz:

```bash
roslaunch cleansweep_description spawn_robot.launch
```

### Running Object Detection on a Live Camera (ROS)

To run the perception node independently and view the output:

```bash
roslaunch cleansweep_perception perception.launch
```

## 🤝 How to Contribute

We welcome contributions! Whether it's improving the detection model, optimizing a path planning algorithm, or fixing a bug, please feel free to help out.

Fork the repository.

Create a new branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

## 📜 License

This project is distributed under the MIT License. See LICENSE for more information.
