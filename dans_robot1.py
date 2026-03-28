import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class SingleRobotBeyni(Node):
    def __init__(self):
        super().__init__('robot1_otonom_beyni')
        # Sadece Robot 1'in motor sürücüsüne yayın yapıyoruz
        self.pub_robot1 = self.create_publisher(JointTrajectory, '/robot1/joint_trajectory_controller/joint_trajectory', 10)
        self.timer = self.create_timer(3.0, self.timer_callback)
        self.toggle = False
        self.joint_names = ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
        self.get_logger().info('Robot 1 Otonom Dansa Başladı! KEKW')

    def timer_callback(self):
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        pt = JointTrajectoryPoint()
        
        if self.toggle:
            pt.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            pt.positions = [1.0, 0.8, -0.5, 0.0, 0.0, 0.0] 
            
        pt.time_from_start = Duration(sec=2, nanosec=0)
        msg.points = [pt]
        self.pub_robot1.publish(msg)
        self.toggle = not self.toggle

def main():
    rclpy.init()
    node = SingleRobotBeyni()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
