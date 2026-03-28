#!/bin/bash
echo "--- XACRO DİNAMİK ÜRETİM BANDI BAŞLIYOR ---"

#echo "1. AGV (Patron) Sistemi Kuruluyor..."
#ros2 run robot_state_publisher robot_state_publisher src/manufacturing_os_description/urdf/agv.urdf --ros-args -r __ns:=/agv1 &
#sleep 2
#ros2 run gazebo_ros spawn_entity.py -entity agv1 -file src/manufacturing_os_description/urdf/agv.urdf -x 3.4 -y 3.7 -z 0.5 -robot_namespace agv1
#sleep 2

echo "2. Robot 1 Şablondan Üretiliyor ve Sahneye Alınıyor..."
# Xacro'ya diyoruz ki: Al bu şablonu, adını robot1 yap ve geçici bir dosya oluştur.
xacro src/manufacturing_os_description/urdf/robot.urdf.xacro robot_name:=robot1 > /tmp/robot1_temp.urdf
ros2 run robot_state_publisher robot_state_publisher /tmp/robot1_temp.urdf --ros-args -r __ns:=/robot1 &
sleep 2
ros2 run gazebo_ros spawn_entity.py -entity robot1 -file /tmp/robot1_temp.urdf -x 0.0 -y 0.0 -z 0.0 -robot_namespace robot1
sleep 4

echo "Robot 1 Beyinleri Yükleniyor..."
ros2 run controller_manager spawner joint_state_broadcaster -c /robot1/controller_manager --ros-args -r __node:=jsb_r1 &
ros2 run controller_manager spawner joint_trajectory_controller -c /robot1/controller_manager --ros-args -r __node:=jtc_r1 &
sleep 2

echo "3. Robot 2 Şablondan Üretiliyor ve Sahneye Alınıyor..."
xacro src/manufacturing_os_description/urdf/robot.urdf.xacro robot_name:=robot2 > /tmp/robot2_temp.urdf
ros2 run robot_state_publisher robot_state_publisher /tmp/robot2_temp.urdf --ros-args -r __ns:=/robot2 &
sleep 2
ros2 run gazebo_ros spawn_entity.py -entity robot2 -file /tmp/robot2_temp.urdf -x 0.0 -y -2.7 -z 0.0 -robot_namespace robot2
sleep 4

echo "Robot 2 Beyinleri Yükleniyor..."
ros2 run controller_manager spawner joint_state_broadcaster -c /robot2/controller_manager --ros-args -r __node:=jsb_r2 &
ros2 run controller_manager spawner joint_trajectory_controller -c /robot2/controller_manager --ros-args -r __node:=jtc_r2 &

echo "--- BÜTÜN SİSTEM DİNAMİK OLARAK AKTİF ---"
