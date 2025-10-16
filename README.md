Project CleanSweep 🤖♻️
An open-source software stack for an autonomous robot designed to detect, classify, and collect litter from roadsides. This project integrates computer vision, path planning, and robotic manipulation to create a comprehensive solution for environmental cleanup.

## 🎯 Core Features
Real-time Litter Detection: Utilizes a Convolutional Neural Network (CNN) to identify and classify various types of trash (e.g., bottles, cans, paper) from a live camera feed.

Autonomous Navigation: Employs LiDAR and GPS for localization, mapping, and navigating complex roadside environments safely.

Intelligent Path Planning: Implements algorithms like A* and Dynamic Window Approach (DWA) to generate efficient and collision-free paths to targeted debris.

Robotic Arm Manipulation: Controls a multi-DOF robotic arm to precisely pick up identified litter and place it in an onboard storage container.

Web-based Monitoring Dashboard: A remote dashboard built for real-time video streaming, robot status monitoring, and manual override control.

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
### Running the Simulation
To launch the robot model in a simulated roadside environment using Gazebo and visualize the sensor data in RViz:

Bash

roslaunch cleansweep_description spawn_robot.launch
### Running Object Detection on a Live Camera
To run the perception node independently and view the output:

Bash

roslaunch cleansweep_perception perception.launch
## 🤝 How to Contribute
We welcome contributions! Whether it's improving the detection model, optimizing a path planning algorithm, or fixing a bug, please feel free to help out.

Fork the repository.

Create a new branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

## 📜 License
This project is distributed under the MIT License. See LICENSE for more information.