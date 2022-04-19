#!/bin/bash -i
# Why bash interactive? Like that I have no problems with virtualenv. If not, doesn't detect the virtualenv. The desktop entry need terminal=true
# This script configure our app to start properly.
LOG=/home/$USER/Agroscope/ASPEN/Software/ctrl/log.log
export DISPLAY=:1
export KIVY_NO_ARGS=1
#Starting GUI
{
	now=$(date)
	echo "" >> $LOG
	echo "$now: Starting GUI" >> $LOG
	source /home/$USER/Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate >> $LOG 2>&1
	cd /home/$USER/Agroscope/ASPEN/Software/
	inputStr=$(zenity --list \
		--print-column=ALL \
		--title="Choose your model" \
		--width=350 --height=250 \
		--column="Model" --column="Conf_thres" --column="F1" --column="Depth(m)" \
		"Apple" "0.439" "0.78" "3.00" \
		"Strawberry" "0.548" "0.89" "1.00" \
		"Tomato" "0.384" "0.81" "0.50"\
		"None" "NaN" "NaN" "2")
	#Cancel goes out
	if [[ "$?" != "0" ]] ; then
    	exit 1
	fi
	inputStr=(${inputStr//|/ })
	python3 main.py --model ${inputStr[0]} --conf_thres ${inputStr[1]} --depth_limit ${inputStr[3]}  >> $LOG 2>&1
	#NOTE: true or false without caps!
	echo "$now: End of routine" >> $LOG
	exit 1
} || {
	echo "$now: Agroscope plug-in fail to open GUI." >> $LOG
	exit 1
}
