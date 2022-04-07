#!/bin/sh
# Prepare_xavier: install all main components for using aspen-tool
# Starting point:
# Create a copy as indicate here: https://developer.nvidia.com/embedded/learn/get-started-jetson-xavier-nx-devkit#intro

# 0. Wifi 
# 1. ROS
# 2. Python
# 	2.1 Python env
# 3. Sofware
# 	3.1 Livox-SDK
#	3.2 R3Live
#	3.3 Yolov5
# 4. Touch screen

# Granting permits
sudo usermod -aG sudo aspen
visudo
# ADD THIS AT THE END:
aspen   ALL=(ALL) NOPASSWD:ALL

# 1. ROS
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt update
sudo apt install ros-melodic-desktop-full
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
sudo apt install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential
sudo rosdep init
rosdep update

# 2. Python
# We need python 3.8
mkdir Agroscope
cd Agroscope
mkdir Python_venvironments

sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8

# Other requiered staff
sudo apt-get install python3-pip
sudo apt-get install python3.8-venv
cd Python_venvironments
python3.8 -m venv YOLO_v5_DeepSort_venv
cd
source Agroscope/Python_venvironments/YOLO_v5_DeepSort_venv/bin/activate
python3.8 -m pip install --upgrade pip

# 3 Download requiered software
cd Agroscope
mkdir Data_processing
cd Data_processing
mkdir 2_realtime
cd 2_realtime
mkdir ROS
mkdir tools
cd tools
mkdir ML
mkdir software

# 3.1 Livod-SDK
sudo apt install cmake
cd software
git clone https://github.com/Livox-SDK/Livox-SDK.git
cd Livox-SDK
cd build && cmake ..
make
sudo make install
# Also livox ROS driver
cd
cd Agroscope/Data_processing/2_realtime/ROS/
mkdir src
cd src
git clone https://github.com/Livox-SDK/livox_ros_driver.git
cd ..
catkin_make
echo source ./devel/setup.sh >> ~/.bashrc






# 3.2 R3Live
# Install PLC, Eigen, OpenCV
sudo apt install libpcl-dev
sudo apt-get install libeigen3-dev
sudo apt install python3-opencv
sudo apt-get install libcgal-dev pcl-tools
sudo apt-get install ros-melodic-cv-bridge ros-melodic-tf ros-melodic-message-filters ros-melodic-image-transport ros-melodic-image-transport*
# OpenCV need to be installed diferently
cd ../..
cd tools/software
wget https://github.com/opencv/opencv/archive/3.4.16.zip
unzip 3.4.16.zip
rm 3.4.16.zip
cd opencv-3.4.16
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..
sudo make install
pkg-config --modversion opencv

# Before continuing opencv in jetson systems it's under /usr/include/opencv4/opencv2, what R3live doesnt know
# the quickest way to solve this, without rewriting config files is to symlink the directories:
sudo ln -s /usr/include/opencv4/opencv2/ /usr/include/opencv

# Now back to R3Live
# 2022-02-23: R3 live do not work in ARM. So this will have to wait
#git clone https://github.com/hku-mars/r3live.git
#cd ../
#catkin_make
#source /home/aspen/Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash

# 3.3 ML: Yolov5 with deepsort
cd 
cd /home/aspen/Agroscope/Data_processing/2_realtime/tools/ML
git clone --recurse-submodules https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch.git
cd Yolov5_DeepSort_Pytorch
python3.8 -m pip install -r requirements.txt


cd
sudo reboot

# Apearance
sudo apt install chrome-gnome-shell
sudo apt install gnome-tweaks
# You need to activate manually also dash-to-pannel 
# https://extensions.gnome.org/extension/1160/dash-to-panel/
# For changing the lock screnn:
sudo apt install gir1.2-clutter-1.0
# Now go to extensions in tweaks

# Touch screen
sudo apt install gnome-shell-extensions
sudo apt-get install build-essential libqt4-dev libx11-6 libx11-dev

# This is the important part actually
# We need to install a driver evdev
sudo apt-get install xserver-xorg-input-evdev
# And make it higher in number that the old one
cd /usr/share/X11/xorg.conf.d
sudo mv 40-libinput.conf 10-libinput.conf 
sudo mv 10-evdev.conf 11-evdev.conf 


https://extensions.gnome.org/extension/1140/disable-gestures/


sudo apt install libinput-tools libinih-dev libxdo-dev
cd /home/aspen/Agroscope/Data_processing/2_realtime/tools/software
git clone https://github.com/Hikari9/comfortable-swipe.git --depth 1
cd comfortable-swipe
bash install
cd ..
rm -r comfortable-swipe

sudo gpasswd -a "$USER" "$(ls -l /dev/input/event* | awk '{print $4}' | head --line=1)"
comfortable-swipe start



cd Others
git clone https://github.com/Plippo/twofing.git
cd twofing
sudo apt-get install build-essential libx11-dev libxtst-dev libxi-dev x11proto-randr-dev libxrandr-dev xserver-xorg-input-evdev xserver-xorg-input-evdev-dev
make
sudo make install

cd rules
cd /usr/share/X11/xorg.conf.d
sudo su
echo 'Section "InputClass"
  Identifier "calibration"
  Driver "evdev"
  # replace DEVICENAME in the following line with your device name
  MatchProduct "wch Touch"

  Option "EmulateThirdButton" "1"
  Option "EmulateThirdButtonTimeout" "750"
  Option "EmulateThirdButtonMoveThreshold" "30"
EndSection' >> 71-touchscreen-waveshare.conf










# Utilities
sudo apt-get -y install nano
sudo apt install curl
# Continuos backspacing
gsettings set org.gnome.desktop.peripherals.keyboard repeat true
# Block keyboard from apearing
https://extensions.gnome.org/extension/3222/block-caribou-36/


# cd Agroscope/Data_processing/2_realtime/ROS/

# Starting 
cd

echo " # Agroscope plugin: Allow the use of ROS environment and specific packages for rosbag analisis and some personal likes
{ # Try:
    source /opt/ros/melodic/setup.bash
    export ROS_HOSTNAME=localhost
    export ROS_MASTER_URI=http://localhost:11311
    #sudo rosdep init

    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
    xhost local:$USER > /dev/null

    #echo -e "${YELLOW}[DEBUG]: Using ROS_workspace_3 from Agroscope post processing for R3LIVE${NC}"
    #source /home/aspen/Agroscope/Data_processing/2_realtime/ROS_spaces/ROS_workspace_3/devel/setup.bash

    #Take care of CUDA for machine learning
    #echo -e "${YELLOW}[DEBUG]: Using cuda v11.0 - Installed for yolact_edge${NC}"
    #export PATH=/usr/local/cuda-11.0/bin${PATH:+:${PATH}}
    #export LD_LIBRARY_PATH=/usr/local/cuda-11.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    #export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64

    source /home/aspen/Agroscope/Python_venvironments/YOLO_v5_DeepSort_venv/bin/activate
    echo "    Agrosocope_base python virtual environment loaded"
    
    # Set nano as default
    export EDITOR='nano -w'
} || { # OR
    echo "Agroscope plug-in fail. Please check instalation"
}" >>.bashrc


# Add PTP for time sync
# First we check that is available
ethtool -T eth0
sudo apt update
sudo apt install linuxptp

# To run our software we need to activate rc.local at /etc/rc.local
# First we need to create a service
sudo touch /etc/systemd/system/rc-local.service
sudo tee -a /etc/systemd/system/rc-local.service > /dev/null <<EOT
[Unit]
 Description=/etc/rc.local Compatibility
 ConditionPathExists=/etc/rc.local

[Service]
 Type=forking
 ExecStart=/etc/rc.local start
 TimeoutSec=0
 StandardOutput=tty
 RemainAfterExit=yes

[Install]
 WantedBy=multi-user.target
EOT

# We transfer our software
cd 
#git clone 
# Now we can do it local
sudo scp -r ubuntu@192.168.0.29:Agroscope/Tool /home/aspen/Agroscope
sudo chmod +777 /home/aspen/Agroscope/Tool/Software/ctrl/Startup.sh
sudo chmod +777 /home/aspen/Agroscope/Tool/Software/ctrl/Startup.log


# Then we create our rc.local
sudo touch /etc/rc.local
sudo tee -a /etc/rc.local > /dev/null <<EOT
#!/bin/bash -e
sudo -H -u aspen bash -c /home/aspen/Agroscope/Tool/Software/ctrl/Startup.sh &
exit 0
EOT

sudo chmod +x /etc/rc.local
sudo systemctl enable rc-local
sudo systemctl status rc-local
sudo systemctl start rc-local.service


# Checking 
https://www.jetsonhacks.com/nvidia-jetson-xavier-nx-gpio-header-pinout/


## the startup.sh file need to be open to use / have permitions
chmod +777 Startup.sh
chmod +777 Startup.log

# Also the Start.sh is not working from rc.local, so as we have a visual interface we can call it from crontab



# Then we restart
sudo reboot