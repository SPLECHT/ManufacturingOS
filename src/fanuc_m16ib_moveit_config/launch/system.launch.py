import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    desc_pkg = get_package_share_directory('manufacturing_os_description')
    config_pkg = get_package_share_directory('fanuc_m16ib_moveit_config')

    # URDF ve SRDF yolları (robot.urdf dosyanın tam yerini kontrol et)
    urdf_file = os.path.join(desc_pkg, 'urdf', 'fanuc_m16ib', 'robot.urdf')
    srdf_file = os.path.join(config_pkg, 'srdf', 'fanuc_m16ib.srdf')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()
    with open(srdf_file, 'r') as f:
        robot_srdf = f.read()

    robot_description = {'robot_description': robot_desc}
    robot_description_semantic = {'robot_description_semantic': robot_srdf}

    # 1. Robot State Publisher (Kemikleri Yayınlar)
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 2. ros2_control Node (Donanım Yöneticisi)
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_description, os.path.join(config_pkg, 'config', 'ros2_controllers.yaml')],
        output='screen'
    )

    # 3. Controller Spawner'ları (Kasları Çalıştırır)
    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )
    traj_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fanuc_arm_controller'],
    )

    # 4. MoveGroup (Beyin - Yörünge Planlayıcı)
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            os.path.join(config_pkg, 'config', 'kinematics.yaml'),
            os.path.join(config_pkg, 'config', 'moveit_controllers.yaml'),
            {'use_sim_time': False}
        ]
    )

    return LaunchDescription([
        rsp_node,
        ros2_control_node,
        jsb_spawner,
        traj_spawner,
        move_group_node
    ])
