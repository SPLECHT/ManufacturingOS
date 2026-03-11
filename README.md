![logo](https://github.com/user-attachments/assets/b5119506-0d8a-48d8-a028-8f20b3f48ea2)
# ManufacturingOS
Proprietary Industrial Operating System for Autonomous Production

ManufacturingOS is a high-level, hardware-agnostic "Manufacturing Kernel" designed to manage the entire lifecycle of a production line. By bridging Unity's real-time 3D engine with the ROS2 robotics framework, MOS creates a seamless interface between the digital and physical worlds.

🛡️ Project Status: Proprietary
The source code of ManufacturingOS is private and intellectual property. This repository serves as a Roadmap, Technical Documentation, and Portfolio for recruitment and collaboration purposes.

💼 Recruitment & Business Inquiries
This project demonstrates advanced skills in Mechatronics Engineering, System Integration, and Robotics Software Development.

If you have any questions please contact via goktugnuhoglu41@gmail.com

📈 ManufacturingOS Development Log

Phase 1: Connectivity (Foundation) ---- DONE ----
* Unity & ROS2 bi-directional bridge setup.
* Latency testing and "Ping-Pong" verification between Unity Engine on Windows and ROS2 on Ubuntu running in VirtualBox.
 <img width="1919" height="1079" alt="ManufactoringOS Phase1" src="https://github.com/user-attachments/assets/c3530caa-1e69-4175-8659-cf6adebaf7cb" />


Phase 2: Visual Twin (Telemetry) ---- DONE ----
* Subscribing to /joint_states from ROS2's robot_state_publisher.
* Real-time synchronization of the 3D robot model in Unity with the ROS2 core.

https://github.com/user-attachments/assets/039defde-11b0-4b1e-b118-b7c2709918b9


Phase 3: Manual Manipulation (Teleoperation) ---- DONE ----
* Building a simple UI/UX in Unity (Sliders or Draggable Handles).
* Sending joint commands back to ROS2 to move the virtual/physical robot manually.


https://github.com/user-attachments/assets/0e6245b9-6fcd-4487-a529-2770e9b61b73

 
Phase 4: AGV Integration & Fleet Visualization & LiDAR Integration ---- DONE ----
* Integrating an Autonomous Guided Vehicle (AGV) into the existing multi-robot Gazebo simulation.
* Visualizing ROS2 LaserScan (LiDAR)


https://github.com/user-attachments/assets/b0f19dbc-61ab-47c1-bc02-454502077d5d

Revision Overview:
In order to achieve true industrial-grade real-time performance and eliminate the inherent latency of network middleware, the core communication architecture of ManufacturingOS has been completely overhauled. The project has transitioned from using the traditional ROS-TCP-Endpoint bridge to a Native FastDDS integration via Ros2ForUnity.

Key Technical Improvements:

* Middleware Elimination: By removing the TCP bridge bottleneck, Unity now operates as a first-class, native ROS 2 node on the distributed network. This allows for direct peer-to-peer communication with hardware controllers and Gazebo simulations.
* Ultra-Low Latency: Data transmission for high-frequency topics (such as /joint_states, /odom, and /scan) is now handled directly by the DDS (Data Distribution Service) layer, achieving near-zero latency telemetry streaming.
* Thread-Safe Data Synchronization: Completely rewrote the subscriber and publisher architectures in C#. Implemented robust lock mechanisms to safely pass high-frequency background DDS thread data into Unity's main rendering and physics thread without race conditions.
* True "Plug-and-Play" Digital Twin: The platform no longer requires hardcoded IP addresses or separate bridge instances. Utilizing DDS Network Discovery, the Unity HMI dashboard automatically detects and connects to robotic fleets within the same ROS_DOMAIN_ID.

This architectural shift transforms ManufacturingOS from a conceptual simulation bridge into a robust, deployment-ready Industrial IoT and Teleoperation platform.
