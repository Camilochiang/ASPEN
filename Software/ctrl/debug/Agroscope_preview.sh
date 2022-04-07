#!/bin/bash
log=/home/aspen/Agroscope/ASPEN/Software/ctrl/Startup.log
{
	source /opt/ros/melodic/setup.sh >> $log 2>&1
	export ROS_HOSTNAME=localhost >> $log 2>&1
	export ROS_MASTER_URI=http://localhost:11311 >> $log 2>&1
	export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH >> $log 2>&1
	export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6 >> $log 2>&1
	sudo ifconfig eth0 192.168.1.30
	echo "$now: ROS melodic prepared" >> $log
	source /home/aspen/Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash >> $log 2>&1
	source /home/aspen/Agroscope/ASPEN/Software/ROS/devel/setup.bash >> $log 2>&1
	source /home/aspen/Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate >> $log 2>&1
	sudo ifconfig eth0 192.168.1.30

	now=$(date)
	echo "$now: Finish loading" >> $log


	find /usr | zenity --progress --auto-close --text="Working..." --display=:1.0 --width=500 --height=100 &
	zpid=$!

	# Wait until the camera is available
	rostopic list | grep "color/image_raw" >> /dev/null
	while [[ $? -eq 1 ]]; do
		echo "waiting for cameras" >> $log
	done

	kill $zpid

	python3 /home/aspen/Agroscope/ASPEN/Software/ctrl/debug/Agroscope_preview.py >>$log 2>&1

} || {
	echo "$now: Agroscope plug-in fail to open GUI." >> $log
	exit 1
}