#!/bin/bash
# This script configure Jetson xavier NX at booting time.

# Starting
log=/home/ubuntu/Agroscope/ASPEN/Software/ctrl/log.log
export DISPLAY=:1

# Waiting for desktop : This 5 lines were for using with systemd, but we change to icon so tecnically is not necessary
echo " " >> $log
pgrep gnome-session > /dev/null

while [[ $? -eq 1 ]]; do
    echo "$now: Waiting for desktop..."  >> $log
done

{
	now=$(date)
	echo "$now: Device started" >> $log
	source /opt/ros/melodic/setup.sh >> $log 2>&1
	export ROS_HOSTNAME=localhost >> $log 2>&1
	export ROS_MASTER_URI=http://localhost:11311 >> $log 2>&1
	export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH >> $log 2>&1
	export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6 >> $log 2>&1
	sudo ifconfig eth0 192.168.1.30
	echo "$now: ROS melodic prepared" >> $log
	# Load livox and realsense drivers
	# Livox 
	source /home/ubuntu/Agroscope/Data_processing/2_realtime/ROS_spaces/ROS_workspace_3/devel/setup.bash >> $log 2>&1
	#source "/home/ubuntu/Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash" >> $log 2>&1
	# BMI088
	#source "/home/ubuntu/Agroscope/ASPEN/Software/ROS/devel/setup.bash" >> $log 2>&1	
	now=$(date)	
	echo "$now: ROS drivers loaded [Livox, BMIO088]" >> $log
	#Python env
	source /home/ubuntu/Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate >> $log 2>&1
	now=$(date)
	echo "$now: Agroscope venv loaded" >> $log
	roslaunch livox_ros_driver livox_lidar_msg.launch >> $log 2>&1 &
	roslaunch realsense2_camera rs_agroscope.launch >> $log 2>&1 &
	now=$(date)
	echo "$now: Livox, RS and IMU ROSlaunch started" >> $log 
	while true;do
		sleep 1
	done
	#rosrun bmi088 imu.py  &

} || {
	echo "$now: Agroscope startup failed." >> $log
	exit 1
}
