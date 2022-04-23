#!/bin/bash
# This script configure Jetson xavier NX at booting time.

# Starting
log=/home/$USER/Agroscope/ASPEN/Software/ctrl/log.log
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
	#sudo netplan apply
	echo "$now: ROS melodic prepared" >> $log
	# Load livox, realsense and BMI088 drivers
	source /home/$USER/Agroscope/ASPEN/Software/ROS/devel/setup.bash >> $log 2>&1
	now=$(date)	
	echo "$now: ROS drivers loaded [Livox, BMIO088]" >> $log
	#Python env
	source /home/$USER/Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate >> $log 2>&1
	now=$(date)
	echo "$now: Agroscope venv loaded" >> $log
	
	roscore >> $log 2>&1 &
	roslaunch realsense2_camera rs_agroscope.launch --wait >> $log 2>&1 &
	roslaunch livox_ros_driver livox_lidar_msg.launch --wait >> $log 2>&1 &
	now=$(date)
	echo "$now: Livox, RS and IMU ROSlaunch started" >> $log 

	# Wait until the camera topic is available
	(
	val=0
	while true; do
		topiclist=$(rostopic list)
		topiclist=(${topiclist/|/ })
		if [ ${topiclist[0]} == "/camera/align_to_color/parameter_descriptions" ]; then
			val=100; sleep 1; echo $val
			break
		fi
	done 
	) | 
	zenity --progress \
		--title="Loading drivers" \
		--text='Looking for availability of ROS topics' \
		--pulsate \
		--auto-kill=true \
		--auto-close=true

	# And now wait for ever :D
	while true;do
		sleep 1
	done
	#rosrun bmi088 imu.py  &

} || {
	echo "$now: Agroscope startup failed." >> $log
	exit 1
}
