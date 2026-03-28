import os
from launch import LaunchDescription
from launch.actions import TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # URDF dosyasının tam yolunu al ve içindeki metni oku
    urdf_path = os.path.expanduser('~/ManufacturingOS/src/manufacturing_os_description/urdf/motoman_gp8.urdf')
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # 1. GAZEBO'YU DOĞRUDAN ROS2 PAKETİYLE BAŞLAT (Yeni ve Kusursuz Yöntem)
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')),
    )

    # 2. TCP KÖPRÜSÜ (Unity Bağlantısı)
    tcp_endpoint = Node(
        package='ros_tcp_endpoint',
        executable='default_server_endpoint',
        parameters=[{'ROS_IP': '0.0.0.0', 'ROS_TCP_PORT': 10000}],
        output='screen'
    )

    # ================= ROBOT 1 =================
    rsp_1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='robot1',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )
    spawn_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot1/robot_description', '-entity', 'robot1', '-robot_namespace', 'robot1', '-x', '0.0', '-y', '1.0', '-z', '0.0'],
        output='screen'
    )
    jsb_1 = Node(package='controller_manager', executable='spawner', namespace='robot1', arguments=['joint_state_broadcaster', '-c', '/robot1/controller_manager'], output='screen')
    jtc_1 = Node(package='controller_manager', executable='spawner', namespace='robot1', arguments=['joint_trajectory_controller', '-c', '/robot1/controller_manager'], output='screen')

    # ================= ROBOT 2 =================
    rsp_2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='robot2',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )
    spawn_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot2/robot_description', '-entity', 'robot2', '-robot_namespace', 'robot2', '-x', '0.0', '-y', '-1.0', '-z', '0.0'],
        output='screen'
    )
    jsb_2 = Node(package='controller_manager', executable='spawner', namespace='robot2', arguments=['joint_state_broadcaster', '-c', '/robot2/controller_manager'], output='screen')
    jtc_2 = Node(package='controller_manager', executable='spawner', namespace='robot2', arguments=['joint_trajectory_controller', '-c', '/robot2/controller_manager'], output='screen')

    # SPAM ENGELLEYİCİ: Gazebo'ya robotların inmesi için 5 saniye bekle
    delay_spawners = TimerAction(
        period=5.0,
        actions=[jsb_1, jtc_1, jsb_2, jtc_2]
    )

    return LaunchDescription([
        gazebo,
        tcp_endpoint,
        rsp_1, spawn_1,
        rsp_2, spawn_2,
        delay_spawners
    ])
