import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pymodbus.client import ModbusTcpClient

class ModbusBridgeNode(Node):
    def __init__(self):
        super().__init__('modbus_factoryio_bridge')
        
        # --- 1. MODBUS CONNECTION ---
        self.get_logger().info("Connecting to Factory IO Modbus Server...")
        
        # NOTE: Use '10.0.2.2' if connecting from VirtualBox to Windows Host. 
        # Use '127.0.0.1' if running locally or via WSL.
        self.modbus_client = ModbusTcpClient("192.168.0.102", port=502)
        
        if self.modbus_client.connect():
            self.get_logger().info("CONNECTION SUCCESSFUL! ManufacturingOS is online and deployed to the field.")
        else:
            self.get_logger().error("Failed to connect to Factory IO! Did you press the PLAY button in Factory IO?")
            return

        # --- 2. ROS 2 PUBLISHERS & SUBSCRIBERS ---
        # Channel to trigger Unity and the Action Server
        self.publisher_ = self.create_publisher(String, '/manufacturing_os/trigger', 10)
        
        # Channel to listen for the "Task Done" signal from the robot
        self.done_sub = self.create_subscription(String, '/manufacturing_os/robot_done', self.robot_done_callback, 10)
        
        # --- 3. STATE CONTROL VARIABLES ---
        self.kutu_geldi_mi = False  # Locks the End (Robot) sensor
        self.kutu_yolda_mi = False  # Locks the Start (Emitter) sensor
        
        # Initialize System: Start the conveyor (Coil 0 -> True)
        self.modbus_client.write_coil(address=0, value=True)
        self.get_logger().info("Conveyor started. System is waiting for a payload...")
        
        # Loop to check sensors 10 times per second
        self.timer = self.create_timer(0.1, self.modbus_loop)

    def modbus_loop(self):
        # ---------------------------------------------------------
        # A) START SENSOR CHECK (Input 1 - Front of Emitter)
        # ---------------------------------------------------------
        spawn_result = self.modbus_client.read_discrete_inputs(address=1, count=1)
        if not spawn_result.isError():
            spawn_sensor = spawn_result.bits[0]
            
            # Rising Edge: Trigger exactly when the sensor FIRST detects the box
            if spawn_sensor and not self.kutu_yolda_mi:
                self.get_logger().info("EMITTER SPAWNED A NEW BOX! Dispatching spawn command to Unity ...")
                self.kutu_yolda_mi = True
                
                # Shout to Unity: Spawn the box!
                msg = String()
                msg.data = "SPAWN_NEW_BOX"
                self.publisher_.publish(msg)
                
            # Reset the system for new boxes when the sensor is cleared
            elif not spawn_sensor and self.kutu_yolda_mi:
                self.kutu_yolda_mi = False

        # ---------------------------------------------------------
        # B) END SENSOR CHECK (Input 0 - Front of Robot)
        # ---------------------------------------------------------
        if self.kutu_geldi_mi:
            return # Skip reading if the box is already there; wait for the robot to finish.

        end_result = self.modbus_client.read_discrete_inputs(address=0, count=1)
        if not end_result.isError():
            end_sensor = end_result.bits[0]
            
            if end_sensor: # Sensor detected the box!
                self.get_logger().warn("PAYLOAD DETECTED AT STATION! Halting the conveyor...")
                
                # Stop the Conveyor (Coil 0 -> False)
                self.modbus_client.write_coil(address=0, value=False)
                self.kutu_geldi_mi = True
                
                # Tell the Unity Robot and ROS 2 Action Server to execute the trajectory!
                msg = String()
                msg.data = "KUTU_HAZIR_ROBOT_HAREKETE_GECSİN"
                self.publisher_.publish(msg)

    def robot_done_callback(self, msg):
        # This function is triggered when the robot completes its trajectory
        if msg.data == "ROBOT_ISLEMI_BITTI_KONVEYORU_BASLAT":
            self.get_logger().info("Robotic manipulation completed. Destroying the box in Unity and resuming conveyor...")
            
            # 1. Send message to Unity to destroy the box
            # (The box on the Factory IO side is destroyed mechanically by the Remover)
            destroy_msg = String()
            destroy_msg.data = "DESTROY_BOX"
            self.publisher_.publish(destroy_msg)
            
            # 2. Restart the Conveyor (Coil 0 -> True)
            self.modbus_client.write_coil(address=0, value=True)
            
            # 3. Unlock the end sensor (Start waiting for the next box)
            self.kutu_geldi_mi = False 

def main(args=None):
    rclpy.init(args=args)
    node = ModbusBridgeNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.modbus_client.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
