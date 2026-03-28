#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from moveit_commander import MoveGroupCommander, roscpp_initialize

class GoHomeNode(Node):
    def __init__(self):
        super().__init__('go_home_node')
        self.get_logger().info("🏠 Robot 'Home' (Sıfır) Pozisyonuna Çekiliyor...")

        # ROS 2 ve C++ arka planını başlat (MoveIt için gerekli)
        roscpp_initialize(sys.argv)

        # DİKKAT: Buradaki "manipulator" ismini kendi MoveIt Setup Assistant'ta
        # belirlediğin Move Group ismiyle değiştir (Örn: "fanuc_arm", "manipulator" vb.)
        self.group_name = "manipulator" 
        
        try:
            self.move_group = MoveGroupCommander(self.group_name)
        except Exception as e:
            self.get_logger().error(f"❌ MoveGroup başlatılamadı! İsim doğru mu? Hata: {e}")
            sys.exit(1)

        # Hızları güvenli bir seviyeye çek (Home'a giderken acele etmesin, kimseye çarpmasın)
        self.move_group.set_max_velocity_scaling_factor(0.1)  # Maksimum hızın %10'u
        self.move_group.set_max_acceleration_scaling_factor(0.1)

    def send_robot_home(self):
        # Fanuc robotlarının genelde tüm eksenlerinin 0 olduğu yer Home pozisyonudur.
        # Eğer sizin robotun Home pozisyonu farklıysa buradaki radyan değerlerini değiştirebilirsin.
        home_joint_values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.get_logger().info(f"Hedef Eklem Açıları (Radyan): {home_joint_values}")

        # Eklemleri hedefe ayarla
        self.move_group.set_joint_value_target(home_joint_values)

        # Planla ve Hareket Et (wait=True diyerek hareket bitene kadar kodu bekletiyoruz)
        success = self.move_group.go(wait=True)

        # Hareket bittikten sonra hedefleri temizle (Güvenlik için)
        self.move_group.stop()
        self.move_group.clear_pose_targets()

        if success:
            self.get_logger().info("✅ Operasyon Tamamlandı: Robot güvenli bir şekilde Home pozisyonuna park edildi. Sistemi kapatabilirsiniz.")
        else:
            self.get_logger().error("❌ HATA: MoveIt yörüngeyi hesaplayamadı veya robota ulaşamadı!")

def main(args=None):
    rclpy.init(args=args)
    
    home_node = GoHomeNode()
    home_node.send_robot_home()
    
    home_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
