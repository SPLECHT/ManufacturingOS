import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math
import time

class FactoryOrchestrator(Node):
    def __init__(self):
        super().__init__('factory_orchestrator')
        
        # AGV Publisher ve Subscriber
        self.cmd_vel_pub = self.create_publisher(Twist, '/agv1/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/agv1/odom', self.odom_callback, 10)
        
        # Robot Kollar için Trajectory Publisher'ları
        self.robot1_traj_pub = self.create_publisher(JointTrajectory, '/robot1/joint_trajectory_controller/joint_trajectory', 10)
        self.robot2_traj_pub = self.create_publisher(JointTrajectory, '/robot2/joint_trajectory_controller/joint_trajectory', 10)
        
        # ROS Hedef Koordinatları (Unity'den çevrildi: X = Unity Z, Y = -Unity X)
        self.waypoints = [
            (-2.7, 3.7),   # State 0: Product Point
            (0.8, 0.0),   # State 1: Robot 1 Grab Pos
            ("ROBOT1", 0), # State 2: Robot 1 İşlem Yapsın
            (-2.7, 3.7),   # State 3: Product Point
            (0.8, -2.7),  # State 4: Robot 2 Grab Pos
            ("ROBOT2", 0), # State 5: Robot 2 İşlem Yapsın
            (3.4, 3.7)     # State 6: Spawn Point
        ]
        
        self.current_state = 0
        self.agv_x = 0.0
        self.agv_y = 0.0
        self.agv_yaw = 0.0
        self.agv_ready = False
        
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("ManufacturingOS Orkestratörü Başlatıldı!")

    def odom_callback(self, msg):
        self.agv_x = msg.pose.pose.position.x
        self.agv_y = msg.pose.pose.position.y
        
        # Quaternion'dan Yaw açısını bulma
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.agv_yaw = math.atan2(siny_cosp, cosy_cosp)
        self.agv_ready = True

    def trigger_robot_animation(self, robot_id):
        self.get_logger().info(f"{robot_id} Animasyonu Başlatılıyor...")
        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
        
        points = []

        # 1. FAZ: Parçayı AGV'den Al (Zaman: 2. Saniye)
        p1 = JointTrajectoryPoint()
        p1.positions = [-1.57, 0.5, 0.5, 0.0, -1.0, 0.0]
        p1.time_from_start.sec = 2
        
        # 2. FAZ: Workstation'a Dön ve Parçayı Bırak (Zaman: 5. Saniye)
        p2 = JointTrajectoryPoint()
        p2.positions = [0.0, 0.2, 0.2, 0.0, -0.5, 0.0]
        p2.time_from_start.sec = 5
        
        points.extend([p1, p2])

        # 3. FAZ: İŞLEM DÖNGÜSÜ (Kaynak/Montaj Simülasyonu)
        # Parçayı bıraktıktan sonra Workstation üzerinde 5 kez "git-gel" (zig-zag) yapacak.
        current_time = 5
        for i in range(5): 
            # Hafif yukarı/geri çekil
            p_up = JointTrajectoryPoint()
            p_up.positions = [0.0, 0.1, 0.3, 0.0, -0.2, 0.0] 
            current_time += 1  # 1 saniye sürsün
            p_up.time_from_start.sec = current_time
            
            # Hafif aşağı/ileri bastır (İşlem anı)
            p_down = JointTrajectoryPoint()
            p_down.positions = [0.0, 0.3, 0.1, 0.0, -0.8, 0.0] 
            current_time += 1  # 1 saniye sürsün
            p_down.time_from_start.sec = current_time
            
            points.extend([p_up, p_down])

        # 4. FAZ: İşlem Bitti, Güvenli "Ev" (Home) Pozisyonuna Dön
        p_home = JointTrajectoryPoint()
        p_home.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        current_time += 2 # Eve dönüş 2 saniye sürsün
        p_home.time_from_start.sec = current_time
        points.append(p_home)

        # Hazırlanan tüm rotayı mesaja yükle
        traj_msg.points = points
        
        # Rotayı ilgili robota fırlat!
        if robot_id == "ROBOT1":
            self.robot1_traj_pub.publish(traj_msg)
        else:
            self.robot2_traj_pub.publish(traj_msg)
            
        # DİKKAT: AGV'Yİ BEKLETME SÜRESİ
        # Robotun tüm kaynak işlemi 17 saniye sürecek (current_time). 
        # Ama biz Python'u (ve AGV'yi) sadece parçayı bırakana kadar (6 saniye) bekletiyoruz!
        time.sleep(6.0) 
        self.get_logger().info(f"{robot_id} parçayı tezgaha koydu! AGV yola çıkıyor, Robot ise işlem yapmaya devam ediyor...")

    def control_loop(self):
        if not self.agv_ready:
            return
            
        target = self.waypoints[self.current_state]
        
        # Eğer hedef bir Robot Animasyonu ise
        if type(target[0]) == str:
            self.trigger_robot_animation(target[0])
            self.current_state = (self.current_state + 1) % len(self.waypoints)
            return

        # Eğer hedef bir X, Y koordinatı ise AGV'yi sür
        target_x, target_y = target
        dx = target_x - self.agv_x
        dy = target_y - self.agv_y
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        
        angle_error = target_angle - self.agv_yaw
        # Açı hatasını -pi ile +pi arasında tut
        while angle_error > math.pi: angle_error -= 2 * math.pi
        while angle_error < -math.pi: angle_error += 2 * math.pi

        cmd = Twist()
        
        # --- YENİ VE PÜRÜZSÜZ SÜRÜŞ ALGORİTMASI ---
        if distance > 0.2: # 20 cm hata payı
            
            # 1. Orantılı Dönüş: Hata ne kadar büyükse o kadar hızlı dön (Kp = 2.0)
            cmd.angular.z = 2.0 * angle_error
            
            # Fırıldak gibi dönmesini engellemek için dönüş hızını sınırla
            if cmd.angular.z > 1.5: cmd.angular.z = 1.5
            elif cmd.angular.z < -1.5: cmd.angular.z = -1.5

            # 2. Dinamik İleri Hız (Sürekli akış)
            if abs(angle_error) > 0.5: 
                # Eğer hedef arkasında veya çok yandaysa (30 dereceden fazla), hızı kesip sadece dönsün
                cmd.linear.x = 0.2
            else: 
                # Hedefi burnunun önüne aldıysa hiç durmadan tam gaz ileri!
                cmd.linear.x = 1.5
                
            self.cmd_vel_pub.publish(cmd)
        else:
            # Hedefe varıldı, zınk diye dur
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_vel_pub.publish(cmd)
            self.get_logger().info(f"Hedefe Varıldı: State {self.current_state}")
            time.sleep(1.0) # 1 saniye bekle
            self.current_state = (self.current_state + 1) % len(self.waypoints)

def main(args=None):
    rclpy.init(args=args)
    node = FactoryOrchestrator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
