import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class RobotTaskController(Node):
    def __init__(self):
        super().__init__('robot_task_controller')
        
        # 1. Modbus'tan gelen tetiklemeyi dinle
        self.subscription = self.create_subscription(
            String,
            '/manufacturing_os/trigger',
            self.trigger_callback,
            10)
            
        # 2. İş bitince Modbus'a "Devam Et" diyecek kanal
        self.done_pub = self.create_publisher(String, '/manufacturing_os/robot_done', 10)
        
        # 3. ACTION CLIENT: Robota hareket emri verip bitmesini bekleyen sistem
        self.action_client = ActionClient(
            self, 
            FollowJointTrajectory, 
            '/robot2/joint_trajectory_controller/follow_joint_trajectory'
        )
        
        self.is_robot_working = False
        self.get_logger().info("Waiting for Sensor data ...")

    def trigger_callback(self, msg):
        if msg.data == "KUTU_HAZIR_ROBOT_HAREKETE_GECSİN" and not self.is_robot_working:
            self.get_logger().warn("Package is here. Robot is moving ...")
            self.is_robot_working = True
            self.send_robot_goal()

    def send_robot_goal(self):
        self.get_logger().info('Waiting for Action Server ...')
        self.action_client.wait_for_server()

        goal_msg = FollowJointTrajectory.Goal()
        trajectory = JointTrajectory()
        # Senin Unity'deki joint isimlerinle BİREBİR aynı olmalı
        trajectory.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        # --- HAREKET 1: KUTUYA GİT (Örnek Radyan Açıları) ---
        point1 = JointTrajectoryPoint()
        point1.positions = [0.5, -0.5, 0.5, 0.0, 0.0, 0.0] 
        point1.time_from_start = Duration(sec=2, nanosec=0)
        trajectory.points.append(point1)

        # --- HAREKET 2: BEKLEME POZİSYONUNA GERİ DÖN ---
        point2 = JointTrajectoryPoint()
        point2.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point2.time_from_start = Duration(sec=4, nanosec=0)
        trajectory.points.append(point2)

        goal_msg.trajectory = trajectory

        self.get_logger().info('Trajectory is send. Robot is moving ...')
        self.send_goal_future = self.action_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Trajectory error ...')
            self.is_robot_working = False
            return
        
        # Hedef kabul edildi, şimdi bitmesini bekle
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        # BU FONKSİYON SADECE ROBOT HAREKETİ BİTİNCE ÇALIŞIR
        self.get_logger().info('Mission Complete ...')
        
        # PLC'ye konveyörü tekrar başlatması için sinyal gönder
        done_msg = String()
        done_msg.data = "ROBOT_ISLEMI_BITTI_KONVEYORU_BASLAT"
        self.done_pub.publish(done_msg)
        
        # Yeni kutu için sistemi sıfırla
        self.is_robot_working = False

def main(args=None):
    rclpy.init(args=args)
    node = RobotTaskController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
