import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # 1. URDF'i yükle
    robot_desc_path = os.path.join(get_package_share_directory('manufacturing_os_description'), 'urdf', 'robot.urdf.xacro')
    robot_description_config = xacro.process_file(robot_desc_path, mappings={'robot_name': 'manufacturing_robot'})
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 2. Kontrolcü ayar dosyan (Gazebo için kullandığın controllers.yaml)
    controllers_file = os.path.join(get_package_share_directory('manufacturing_os_description'), 'config', 'controllers.yaml')

    # 3. Kontrolcü Yöneticisi (Gazebo'nun içinden çıkan çekirdek düğüm)
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, controllers_file],
        output="screen",
    )

    # 4. Robot State Publisher (TF'leri ve Joint'leri Unity'ye yollayacak)
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # 5. Broadcaster ve Trajectory Controller'ı ayaklandır
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager"],
    )

    return LaunchDescription([
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        robot_controller_spawner
    ])
