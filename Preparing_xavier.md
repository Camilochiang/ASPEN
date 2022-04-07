## Preparing xavier NX
# Goal
This file have as goal to describe the software configuration for requiered for using the project ASPEN

# Content
1. General configuration:
    1. ROS
        1. Livox
        2. RealSense
    2. Python
        1. Python env
    3. Livox-SDK
        1. livox_ros_driver
        2. PTP
    4. BMI088        
    5. R3Live
    6. YOLOv5
    7. Appearence
    8. Autostart

# 1. General configuration:
- Create a copy as indicate here: https://developer.nvidia.com/embedded/learn/get-started-jetson-xavier-nx-devkit#intro
- Connect to your local wifi
- We need to copy the repository for the tool
```bash
#uname -m
cd
mkdir Agroscope 
cd Agroscope
mkdir Data_processing
cd Data_processing
mkdir ROS
mkdir tools
cd ..
git clone https://github.com/Camilochiang/ASPEN.git
cd
```
- We also want to log inmediatly into the desktop
```bash
# Granting permits
sudo usermod -aG sudo aspen
visudo
# ADD THIS AT THE END:
aspen   ALL=(ALL) NOPASSWD:ALL
```

- We have to update Cmake for librealsnese
```bash
sudo apt remove --purge --auto-remove cmake
sudo apt update
sudo apt install -y software-properties-common lsb-release
sudo apt clean all

wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
sudo apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
sudo apt update
sudo apt install kitware-archive-keyring
sudo rm /etc/apt/trusted.gpg.d/kitware.gpg
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6AF7F09730B3F0A4
sudo apt update
sudo apt install cmake
cmake --version
# And we will install ninja as is also needed later
sudo apt install ninja-build
# And we need to cette the variable 
echo "export VCPKG_FORCE_SYSTEM_BINARIES=1" >> ~/.bashrc
source ~/.bashrc
#sudo apt-get install autoreconf libudev-dev
sudo apt install libudev-dev
```

# 1.1 ROS
- We will use ROS melodic as has work without problems so far
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt update
sudo apt install ros-melodic-desktop-full
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
sudo apt install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential
sudo rosdep init
rosdep update
```
# 2. Realsense
We need two installations:

librealsense
```bash
cd Agroscope/Data_processing/2_realtime/tools/software
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh
./vcpkg integrate install
##CMake projects should use: "-DCMAKE_TOOLCHAIN_FILE=/home/aspen/Agroscope/Data_processing/2_realtime/tools/software/vcpkg/scripts/buildsystems/vcpkg.cmake"
./vcpkg install realsense2
```
ROS wrapper
```bash
sudo mv /home/ubuntu/Agroscope/ASPEN/Software/lib/99-realsense-libusb.rules /etc/udev/rules.d/
sudo apt install ros-$ROS_DISTRO-realsense2-camera
```
Then we have to resource the bash file And it should work
```bash
source ~/.bashrc
sudo cp /home/aspen/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch /opt/ros/melodic/share/realsense2_camera/launch
roslaunch realsense2_camera rs_agroscope.launch
```
What modifications were need it to realsense (Present in rs.launch)?
- Turn off laser = line 3 set to 0 https://github.com/IntelRealSense/realsense-ros/issues/1195
- Dpth at 1280 x 720 at 30 FPS : lines 23 to 26
- RGB at 1920 x 1080 30 FPS : lines 41 to 44
- 


# 2. Python
- We will be using python 3.6 and a virtual_env so:
```bash
cd
cd Agroscope
mkdir Python_venvironments

sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt-get install python3-pip
sudo apt-get install python3-venv
cd Python_venvironments
python3 -m venv YOLO_v5_venv
cd
echo "source Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate" >> .bashrc
source ~/.bashrc
python3 -m pip install --upgrade pip
```
- We will need some packages
```bash
#https://stackoverflow.com/questions/65631801/illegal-instructioncore-dumped-error-on-jetson-nano
# It look that numpy has a problem with jetson, so we need a specific version
python3 -m pip install numpy==1.19.4
python3 -m pip install opencv-python
python3 -m pip install kivy
python3 -m pip install pygame
python3 -m pip install screeninfo
python3 -m pip install pexpect
python3 -m pip install pyyaml
python3 -m pip install rospkg
python3 -m pip install ffpyplayer
```

- OpenCV will be used later for R3LIVE, but need to be installed diferently
```bash
cd 
cd Agroscope/Data_processing/2_realtime/tools/software
wget https://github.com/opencv/opencv/archive/3.4.16.zip
unzip 3.4.16.zip
rm 3.4.16.zip
cd opencv-3.4.16
mkdir build
cd build
# [WARNING]: The following command take around 1 hour or more
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_TOOLCHAIN_FILE=/home/aspen/Agroscope/Data_processing/2_realtime/tools/software/vcpkg/scripts/buildsystems/vcpkg.cmake
sudo make install
pkg-config --modversion opencv
```

# 3. Livox-SDK
- Preparing our network: From the manual
***All Mid-70 sensors are set to static IP address mode by default with an IP address of 192.168.1.XX. The default subnet is 255.255.255.0 and gateways are 192.168.1.1***
```bash
sudo apt install netplan.io
sudo mv /home/aspen/Agroscope/ASPEN/Software/lib/01-network-manager-all.yaml /etc/netplan
sudo netplan generate
sudo netplan apply
sudo reboot
sudo ifconfig eth0 192.168.1.30
```
- First we need to install Livos-SDK
```bash
cd
cd Agroscope/Data_processing/2_realtime/tools/software
git clone https://github.com/Livox-SDK/Livox-SDK.git
cd Livox-SDK
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/home/aspen/Agroscope/Data_processing/2_realtime/tools/software/vcpkg/scripts/buildsystems/vcpkg.cmake
make
sudo make install
```
We can test it to: NOT SURE HOW TO CHECK THAT IS WORKING
```bash
#dpkg --print-architecture
#cd sample_cc/lidar
#./lidar_sample_cc -c "3GGDJ4H00100041" -l
#cd ../..
#cd sample/hub_lvx_file
#./hub_lvx_sample -c "3GGDJ4H00100041" -l -t 10
```

- As we have an external IMU we will be using a custom version of the livos_ros_driver. More details here https://github.com/hku-mars/r2live/issues/56
```bash
cd
cd Agroscope/Data_processing/2_realtime/ROS/src
#scp -r /home/ubuntu/Agroscope/Data_processing/2_realtime/ROS_spaces/ROS_workspace_3/src/livox_ros_driver_for_R2LIVE aspen@192.168.0.46:
git clone https://github.com/Camilochiang/livox_ros_driver.git
cd ..
catkin_make
echo "source /Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash" >> .bashrc
```
And we can test it 
```bash
cd
source .bashrc
roslaunch livox_ros_driver livox_lidar_msg.launch
```

# 4. BMI088
- We can actually using the once from RPI! It works :D
- Just use make clean to create the executable
```bash
cd /home/aspen/Agroscope/ASPEN/Software/ROS/src/bmi088/scripts
chmod +777 imu.py
cd ..
cd src
make clean
cd ../../..
catkin_make
echo "source Agroscope/ASPEN/Software/ROS/devel/setup.bash" >> .bashrc
source .bashrc
rosrun bmi088 imu.py
```
And we can test it 
```bash
cd
source .bashrc
rosrun bmi088 imu.py
```

# 5. R3Live
Install PLC, Eigen, OpenCV
```bash
sudo apt install libpcl-dev
sudo apt-get install libeigen3-dev
sudo apt install python3-opencv
sudo apt-get install libcgal-dev pcl-tools
sudo apt-get install ros-melodic-cv-bridge ros-melodic-tf ros-melodic-message-filters ros-melodic-image-transport ros-melodic-image-transport*
```
Before continuing opencv in jetson systems it's under /usr/include/opencv4/opencv2, what R3live doesnt know
the quickest way to solve this, without rewriting config files is to symlink the directories:
```
sudo ln -s /usr/include/opencv4/opencv2/ /usr/include/opencv
```

Now back to R3Live
2022-02-23: R3 live do not work in ARM. So this will have to wait
```bash
#git clone https://github.com/hku-mars/r3live.git
#cd ../
#catkin_make
#source /home/aspen/Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash
```
# 6. Yolov5
```bash
cd 
cd Agroscope/Data_processing/2_realtime/tools/ML
git clone --recurse-submodules https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch.git
cd Yolov5_DeepSort_Pytorch
python3 -m pip install -r requirements.txt
```

6. Appearence
# Setting wallpaper again
```bash
gsettings set org.gnome.desktop.background picture-uri 'file:///home/aspen/Agroscope/ASPEN/Software/Images/Wallpaper_xavier.png'
# Show the icons
gsettings set org.gnome.shell.extensions.desktop-icons show-home true
cd 
cd Desktop
# Give permition to our program
sudo chown aspen:aspen Agroscope.desktop
```

7. Autostart of ROS and others
We will be using a service to manage ROS
```bash
sudo cp /home/aspen/Agroscope/ASPEN/Software/transfer/Agroscope.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable Agroscope
sudo systemctl start Agroscope
```
```
cd
sudo mv Agroscope/ASPEN/Software/transfer/Agroscope.service /etc/systemd/system

sudo systemctl status Agroscope
cd /etc/profile.d
sudo chmod +777 Agroscope.sh
```

8. Start app
- Click in the icon!




















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



# Add PTP for time sync
# First we check that is available
ethtool -T eth0
sudo apt update
sudo apt install linuxptp


# Checking 
https://www.jetsonhacks.com/nvidia-jetson-xavier-nx-gpio-header-pinout/
    