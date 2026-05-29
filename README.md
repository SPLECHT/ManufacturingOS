# 🏭 ManufacturingOS: Industrial Digital Twin & Fleet Management System

ManufacturingOS is a highly advanced, bidirectional **Digital Twin and Fleet Management platform** bridging **Unity 3D** and **ROS2 (MoveIt2)**. 

Moving beyond standard simulation, ManufacturingOS acts as a central **"Master Brain"** for industrial environments. It provides zero-latency communication via a Native DDS network, dynamic real-time collision generation, and multi-robot fleet orchestration natively controlled through a custom-built Unity Teach Pendant UI.

![ManufacturingOS Banner](![logo](https://github.com/user-attachments/assets/b5119506-0d8a-48d8-a028-8f20b3f48ea2))

[![Watch the Demo Video](https://img.shields.io/badge/YouTube-Watch_Demo_Video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](#) *((https://youtu.be/y4o7uS0ALpM))*

---

## 🚀 Key Features & Architectural Breakthroughs

### 1. Native ROS2 DDS Integration (Zero-Latency)
Say goodbye to intermediate TCP/Rosbridge bottlenecks. ManufacturingOS utilizes a **Native DDS Bridge**, allowing Unity to publish and subscribe directly to ROS2 topics (`std_msgs`, `geometry_msgs`). Unity acts as a first-class citizen node in the ROS2 ecosystem.

### 2. MOS Kernel Daemon & Multi-Robot Fleet Orchestration
The system features a custom Python daemon (`mos_kernel_daemon.py`) running in the background (WSL2/Ubuntu). 
* **Dynamic Booting:** Unity sends a unified JSON payload (`START_FLEET`) containing the namespaces of the active robots in the scene.
* **Parallel Universes:** The Daemon dynamically spawns isolated MoveIt2 instances, TF trees, and Action Servers for each robot (e.g., `/robot_a`, `/ses`) simultaneously.

### 3. Smart Scene Manager (Real-Time Collision Avoidance)
A dynamic radar system (`SmartSceneManager.cs`) inside Unity scans the environment at 10Hz. 
* Converts Unity `BoxColliders` and Transforms into ROS2 `CollisionObjects`.
* Automatically maps Unity's Left-Handed coordinate system to ROS2's Right-Handed system.
* Publishes dynamic obstacles directly to the MoveIt2 `/planning_scene`, ensuring robots never collide with newly introduced objects.

### 4. Advanced Teach Pendant UI & Waypoint Manager
A fully custom, layout-driven UI built from scratch in Unity for industrial programming.
* **Dictionary-Based Memory:** Manage independent trajectories for multiple robots without data overlapping.
* **TCP Anchor Alignment:** Waypoints calculate trajectories based on the Tool Center Point (TCP) rather than the robot base, essential for high-precision tasks like welding.
* **Local Space Mathematics:** Utilizes `InverseTransformPoint` to calculate relative distances via a specific `URDF_Anchor`, eliminating world-space offset bugs.

### 5. Cartesian Path Planning (Smooth Execution)
Transitioned from standard Point-to-Point (PTP) navigation to **Linear Interpolation (Cartesian Paths)**.
* The ROS2 `MotionAgent` parses JSON trajectories from Unity and utilizes MoveIt's `compute_cartesian_path` service.
* Executes smooth, uninterrupted welding-style paths with tight tolerances (1cm position, 0.2 rad orientation) across multiple waypoints.

---

## ⚙️ How It Works (The Execution Flow)

1. **Wake the Daemon:** Run `mos_daemon.py` in the ROS2 environment. It idles in the background, listening to the `/mos/system_boot` topic.
2. **Design the Factory:** Open Unity, place industrial robots (e.g., Fanuc M-10iA), and assign them unique namespaces via the `RobotReplika` script.
3. **Boot the Fleet:** Hit the **"BOOT"** button in Unity. Unity commands the Daemon to spin up all required MoveIt2 nodes, Controllers, and Motion Agents for the detected namespaces.
4. **Program Trajectories:** Use the Teach Pendant UI to create precise waypoints relative to the robot's TCP.
5. **Execute Simulation:** Press **"Play"**. Unity serializes the trajectory into a JSON payload and publishes it directly to the robot's specific command topic. The Python `MotionAgent` executes the Cartesian path flawlessly.

---

## 🛠️ Tech Stack
* **Game Engine / UI:** Unity 3D (C#)
* **Robotics Framework:** ROS2 (Humble/Foxy)
* **Motion Planning:** MoveIt2 (OMPL, KDL)
* **Communication:** Native DDS Bridge
* **Languages:** C#, Python 3

---

*Developed by a passionate Robotics Software Developer striving to push the boundaries of Industrial Automation and Digital Twins.*
