![logo](https://github.com/user-attachments/assets/b5119506-0d8a-48d8-a028-8f20b3f48ea2)
# ManufacturingOS
Proprietary Industrial Operating System for Autonomous Production

ManufacturingOS is a high-level, hardware-agnostic "Manufacturing Kernel" designed to manage the entire lifecycle of a production line. By bridging Unity's real-time 3D engine with the ROS2 robotics framework, MOS creates a seamless interface between the digital and physical worlds.

🛡️ Project Status: Proprietary
The source code of ManufacturingOS is private and intellectual property. This repository serves as a Roadmap, Technical Documentation, and Portfolio for recruitment and collaboration purposes.

🚀 Key Features (Capabilities)
* Unified Hardware Interface: Capable of controlling multi-axis robotic arms and AGVs regardless of the manufacturer (Universal abstraction layer).
* High-Fidelity Digital Twin: Real-time synchronization with 10-20ms latency optimized for industrial environments.
* Production Recipe Engine: Advanced JSON-based logic to handle complex manufacturing sequences (e.g., modular ammunition production, assembly lines).
* Embedded NLP Integration: Voice and text-based command interpretation for high-level factory orchestration.

💼 Recruitment & Business Inquiries
This project demonstrates advanced skills in Mechatronics Engineering, System Integration, and Robotics Software Development.

For Technical Demos: Please contact via https://www.linkedin.com/in/g%C3%B6ktu%C4%9F-nuho%C4%9Flu-769678192/

📈 ManufacturingOS Development Log

Phase 1: Connectivity (Foundation) ---- DONE ----
* Unity & ROS2 bi-directional bridge setup.
* Latency testing and "Ping-Pong" verification between Windows/WSL2.
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


Phase 5: Integration of High-Fidelity Digital Twin Interface & Real-Time Monitoring GUI
* In this phase, the project transitions from a backend-heavy simulation to a comprehensive Digital Twin Platform. I am developing a custom-built GUI in Unity to bridge the gap between ROS 2-based autonomous logic and human-centric industrial operations. This interface goes beyond traditional SCADA systems by providing spatial awareness through a 3D environment, real-time telemetry visualization, and a seamless command-and-control bridge via ROS-TCP-Connector.
