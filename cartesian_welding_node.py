import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
import json

from std_msgs.msg import String
from geometry_msgs.msg import Pose, Point, Quaternion
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.action import ExecuteTrajectory

class CartesianWeldingNode(Node):
    def __init__(self):
        super().__init__('cartesian_welding_node')

        self.group_name = 'manipulator'
        self.end_effector_link = 'tool0'

        # 1. DDS'ten gelen koordinatları dinle
        self.perception_sub = self.create_subscription(
            String, '/manufacturing_os/workpiece_data', self.perception_callback, 10)

        # 2. Modbus'a işin bittiğini haber verecek yayıncı
        self.done_pub = self.create_publisher(String, '/manufacturing_os/robot_done', 10)

        # 3. MoveIt Arayüzleri
        self.collision_pub = self.create_publisher(CollisionObject, '/collision_object', 10)
        self.cartesian_client = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.execute_client = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')

        self.is_busy = False
        self.get_logger().info("🔥 Otonom Kaynak (Dedektif Modu) Düğümü Hazır! Kutu bekleniyor...")

    def perception_callback(self, msg):
        if self.is_busy:
            return
            
        self.get_logger().info("📦 Unity'den kutu koordinatları alındı! Teşhis başlıyor...")
        self.is_busy = True

        try:
            data = json.loads(msg.data)
            
            # ŞİMDİLİK KAPALI (Teşhis için çarpışma korkusunu devreden çıkarıyoruz)
            self.add_collision_box(data)

            waypoints = []
            
            # 1. BAŞLANGIÇ NOKTASI (10 cm yukarıdan güvenli yaklaşım)
            start_pose = Pose()
            start_pose.position.x = data['corners'][0][0]
            start_pose.position.y = data['corners'][0][1]
            start_pose.position.z = data['corners'][0][2] + 0.10  
            start_pose.orientation = Quaternion(x=0.0, y=1.0, z=0.0, w=0.0) # Torç aşağı bakıyor
            waypoints.append(start_pose)
            
            self.get_logger().info(f"🚀 GÜVENLİ YAKLAŞIM: X: {start_pose.position.x:.3f}, Y: {start_pose.position.y:.3f}, Z: {start_pose.position.z:.3f}")

            # 2. KÖŞELERİ DOLAŞMA (Kutunun 2 cm üzerinden)
            corner_index = 1
            for corner in data['corners']:
                p = Pose()
                p.position.x = corner[0]
                p.position.y = corner[1]
                p.position.z = corner[2] + 0.02 
                p.orientation = Quaternion(x=0.0, y=1.0, z=0.0, w=0.0) # Torç hep aşağı baksın
                waypoints.append(p)
                
                # İŞTE BİZİ KURTARACAK LOG SATIRI
                self.get_logger().info(f"🔍 HEDEF NOKTA {corner_index}: X: {p.position.x:.3f}, Y: {p.position.y:.3f}, Z: {p.position.z:.3f}")
                corner_index += 1

            # 3. KAREYİ TAMAMLA (İlk köşeye geri dön)
            waypoints.append(waypoints[1])

            # 4. GÜVENLİ UZAKLAŞMA (Z ekseninde tekrar yukarı çık)
            end_pose = Pose()
            end_pose.position.x = data['corners'][0][0]
            end_pose.position.y = data['corners'][0][1]
            end_pose.position.z = data['corners'][0][2] + 0.10
            end_pose.orientation = Quaternion(x=0.0, y=1.0, z=0.0, w=0.0)
            waypoints.append(end_pose)

            # Adım 3: Yörüngeyi MoveIt'e hesaplat
            self.plan_and_execute_cartesian_path(waypoints)

        except Exception as e:
            self.get_logger().error(f"❌ JSON işleme hatası: {e}")
            self.is_busy = False

    def add_collision_box(self, data):
        box_obj = CollisionObject()
        box_obj.header.frame_id = "base_link"
        box_obj.id = "target_workpiece"

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [data['dimensions'][0], data['dimensions'][1], data['dimensions'][2]]
        box_obj.primitives.append(primitive)

        pose = Pose()
        pose.position.x = data['center'][0]
        pose.position.y = data['center'][1]
        pose.position.z = data['center'][2]
        box_obj.primitive_poses.append(pose)

        box_obj.operation = CollisionObject.ADD
        self.collision_pub.publish(box_obj)

    def plan_and_execute_cartesian_path(self, waypoints):
        self.get_logger().info("🧠 Kartezyen Yörünge (Düz Çizgi) hesaplanıyor...")
        self.cartesian_client.wait_for_service()

        req = GetCartesianPath.Request()
        req.header.frame_id = "base_link"
        req.group_name = self.group_name
        req.waypoints = waypoints
        req.max_step = 0.01  # Her 1 cm'de bir milimetrik nokta at
        req.jump_threshold = 0.0 

        future = self.cartesian_client.call_async(req)
        future.add_done_callback(self.path_planned_callback)

    def path_planned_callback(self, future):
        res = future.result()
        if res.fraction < 0.9: 
            self.get_logger().error(f"❌ HATA: Yörüngenin sadece %{res.fraction * 100:.1f}'i hesaplanabildi. Kutu robotun menzili dışında!")
            self.is_busy = False
            return

        self.get_logger().info("✅ Yörünge başarıyla hesaplandı. Motorlara güç veriliyor...")
        self.execute_client.wait_for_server()

        goal_msg = ExecuteTrajectory.Goal()
        goal_msg.trajectory = res.solution

        self.send_goal_future = self.execute_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.execution_complete_callback)

    def execution_complete_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("❌ Yörünge Gazebo/Robot tarafından reddedildi.")
            self.is_busy = False
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.finish_cycle)

    def finish_cycle(self, future):
        result = future.result().result
        if result.error_code.val == 1: 
            self.get_logger().info("✨ Otonom Kaynak işlemi KUSURSUZ tamamlandı!")
            
            done_msg = String()
            done_msg.data = "ROBOT_ISLEMI_BITTI_KONVEYORU_BASLAT"
            self.done_pub.publish(done_msg)
        else:
            self.get_logger().error(f"⚠️ Robot kaynak yaparken bir hata oluştu! Hata Kodu: {result.error_code.val}")

        self.is_busy = False

def main(args=None):
    rclpy.init(args=args)
    node = CartesianWeldingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
