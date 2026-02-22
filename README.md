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
* 

https://github.com/user-attachments/assets/039defde-11b0-4b1e-b118-b7c2709918b9



Phase 3: Manual Manipulation (Teleoperation)
* Building a simple UI/UX in Unity (Sliders or Draggable Handles).
* Sending joint commands back to ROS2 to move the virtual/physical robot manually.

Phase 4: Sensor Fusion & Environment (Perception)
* Visualizing LaserScan (Lidar) or PointCloud data within the Unity scene.
* Integrating collision detection using Unity's physics engine.

Phase 5: High-Level Path Planning (Intelligence)
* Sending "Target Pose" commands from Unity to ROS2 MoveIt2.
* Visualizing the planned trajectory before execution (Safety Check).

Phase 6: The Recipe Engine (Automation)
* Developing the JSON-based "Production Sequence" logic.
* Executing multi-step tasks (e.g., Pick-and-Place loops).

Phase 7: Cognitive Interface (NLP & AI)
* Integrating LLM/NLP for voice/text command interpretation.
* Global monitoring and "Dark Factory" remote management dashboard.
