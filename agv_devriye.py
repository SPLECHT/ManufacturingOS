import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class AgvDevriye(Node):
    def __init__(self):
        super().__init__('agv_devriye_node')
        # Sadece AGV'nin motor sürücüsüne hız (cmd_vel) yayını yapıyoruz
        self.publisher_ = self.create_publisher(Twist, '/agv1/cmd_vel', 10)
        
        # Saniyede 10 kere (10 Hz) komut göndererek akıcı hareket sağlıyoruz
        timer_period = 0.1 
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('AGV Devriye (Patrol) Modu Aktif! Çember çiziliyor... KEKW')

    def timer_callback(self):
        msg = Twist()
        
        # İleri doğru sabit hız (m/s)
        msg.linear.x = 0.5  
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        
        # Sabit açısal hız (rad/s) - Bu değer aracın sola doğru kavis çizmesini sağlar
        # Dairenin Yarıçapı Formülü: R = v / w ($R = 0.5 / 0.25 = 2.0$ Metre)
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.25 

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AgvDevriye()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Script kapatılırken AGV'yi durdurmak için fren komutu
        fren = Twist()
        node.publisher_.publish(fren)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
