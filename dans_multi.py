import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class MultiRobotBeyni(Node):
    def __init__(self):
        super().__init__('multi_robot_beyni')
        # İki farklı robotun motor sürücülerine bağlanıyoruz (Namespaces)
        self.pub_robot1 = self.create_publisher(JointTrajectory, '/robot1/joint_trajectory_controller/joint_trajectory', 10)
        self.pub_robot2 = self.create_publisher(JointTrajectory, '/robot2/joint_trajectory_controller/joint_trajectory', 10)
        
        self.timer = self.create_timer(3.0, self.timer_callback)
        self.toggle = False
        self.joint_names = ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
        self.get_logger().info('ManufacturingOS Çoklu Üretim Bandı Aktif! KEKW')

    def timer_callback(self):
        msg1 = JointTrajectory()
        msg2 = JointTrajectory()
        msg1.joint_names = self.joint_names
        msg2.joint_names = self.joint_names
        
        pt1 = JointTrajectoryPoint()
        pt2 = JointTrajectoryPoint()
        
        if self.toggle:
            # SIFIR NOKTASI (İkisi de dik durur)
            pt1.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            pt2.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            # FARKLI HAREKETLER (Asenkron)
            # Robot 1: İleri eğilir ve sola döner
            pt1.positions = [1.0, 0.8, -0.5, 0.0, 0.0, 0.0] 
            # Robot 2: Geriye bükülür ve sağa döner
            pt2.positions = [-1.0, -0.8, 0.5, 0.0, 0.0, 0.0] 
            
        pt1.time_from_start = Duration(sec=2, nanosec=0)
        pt2.time_from_start = Duration(sec=2, nanosec=0)
        
        msg1.points = [pt1]
        msg2.points = [pt2]
        
        self.pub_robot1.publish(msg1)
        self.pub_robot2.publish(msg2)
        
        self.toggle = not self.toggle

def main():
    rclpy.init()
    node = MultiRobotBeyni()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
