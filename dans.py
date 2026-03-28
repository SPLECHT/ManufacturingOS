import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class RobotBeyni(Node):
    def __init__(self):
        super().__init__('robot_beyni')
        # Motor sürücüsüne (Trajectory Controller) bağlanıyoruz
        self.publisher_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        
        # Her 3 saniyede bir sinyal gönderecek zamanlayıcı
        self.timer = self.create_timer(3.0, self.timer_callback)
        self.toggle = False
        
        # Hareket ettireceğimiz eklemlerin isimleri (URDF ile birebir aynı)
        self.joint_names = ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
        self.get_logger().info('ManufacturingOS Üretime Başladı! KEKW')

    def timer_callback(self):
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        
        if self.toggle:
            # SIFIR NOKTASI (Home Position)
            point.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            # HAREKET NOKTASI (Radyan cinsinden açılar)
            # joint_1'i 1 radyan döndür, joint_2'yi 0.5 radyan bük vb.
            point.positions = [1.0, 0.5, -0.5, 0.0, 0.0, 0.0] 
            
        # Motorlara bu hareketi "2 saniye içinde pürüzsüzce" yapmasını emrediyoruz
        point.time_from_start = Duration(sec=2, nanosec=0)
        
        msg.points = [point]
        self.publisher_.publish(msg)
        self.toggle = not self.toggle

def main():
    rclpy.init()
    node = RobotBeyni()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
