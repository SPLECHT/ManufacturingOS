import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro
import yaml

def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        return None

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

def generate_launch_description():
    # 1. Orijinal Xacro/URDF dosyanı okuyoruz
    robot_description_path = os.path.join(get_package_share_directory('manufacturing_os_description'), 'urdf', 'robot.urdf.xacro')
    robot_description_config = xacro.process_file(robot_description_path, mappings={'robot_name': 'manufacturing_robot'})
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 2. Bizim elimizle yazdığımız SRDF ve Kinematik dosyaları
    robot_description_semantic = {'robot_description_semantic': load_file('manufacturing_robot_moveit_config', 'config/manufacturing_robot.srdf')}
    robot_description_kinematics = {'robot_description_kinematics': load_yaml('manufacturing_robot_moveit_config', 'config/kinematics.yaml')}
    
    # 3. KONTROLCÜ DÜZELTMESİ (Gazebo Action Server bağlantısı)
    moveit_controllers = {
        'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager',
        'moveit_simple_controller_manager': {
            'controller_names': ['joint_trajectory_controller'],
            'joint_trajectory_controller': {
                'type': 'FollowJointTrajectory',
                'action_ns': 'follow_joint_trajectory',
                'default': True,
                'joints': ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
            }
        }
    }

    # 4. Yörünge Ayarları (Simülasyon Hata Payları)
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    # 5. OMPL PLANLAYICI DÜZELTMESİ (CHOMP yerine endüstri standardı OMPL)
    ompl_planning_pipeline_config = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': """default_planner_request_adapters/AddTimeOptimalParameterization default_planner_request_adapters/ResolveConstraintFrames default_planner_request_adapters/FixWorkspaceBounds default_planner_request_adapters/FixStartStateBounds default_planner_request_adapters/FixStartStateCollision default_planner_request_adapters/FixStartStatePathConstraints""",
            'start_state_max_bounds_error': 0.1
        }
    }

    # 6. Asıl Beyin: Move Group Düğümü
    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            moveit_controllers,
            trajectory_execution,
            ompl_planning_pipeline_config,
            {'use_sim_time': False} # Gazebo ile saatlerin senkron olması çok kritik!
        ],
    )

    return LaunchDescription([run_move_group_node])
