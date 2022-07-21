# Preparing Xavier NX
## Goal
This file has as goal to describe the software configuration that is used in the project ASPEN. At diference, the .sh file run the instalation without explaning each step

## Content
0. [General configuration](#General-configuration)
1. [Before closing the box](#Before-closing-the-box)
   1. [BMI088](#IMU)
   2. [SONY](#sony)
   3. [ALTUM](#altum)
   4. [LiDAR](#lidar)
2. [Software installation](#software-installation)
   1. [Realsense](#realsense)
      1. [OpenCV](#OpenCV)
      2. [librealsense](#librealsense)
   2. [ROS](#ROS)
   3. [librealsense ROS wrapper](#librealsense-ROS-wrapper)
   4. [Livox](#Livox)
   5. [ASPEN](#aspen)
   6. [Appeareance](#appearence)




3. R3Live
4. YOLOv5 and sort
5. Appearence
6.  Icons

## ***General configuration***
- Install Jetson Pack 4.6.2 into your jetson xavier NX module using nvidia SDK Manager. 
  - If you are using a developer kit, you can create a copy of it using a sd card, as indicate it [here](https://developer.nvidia.com/embedded/learn/get-started-jetson-xavier-nx-devkit#intro). 
- Remember to instal it in the SSD card if is possible
- Connect to your local wifi
- We need to copy the repository for the tool
```bash
cd
mkdir Agroscope 
cd Agroscope
git clone --recurse-submodules https://github.com/Camilochiang/ASPEN
#We will also install netplan 
sudo apt install netplan.io
```

## ***Before closing the box***
 Sensor checking.
To be able to close the box we will first run some test before
### IMU:
```bash
# We have to check i2c connection
sudo i2cdetect -r -y 0
cd ~/Agroscope/ASPEN/Software/ROS/src/bmi088/src
make clean
make
./BMI088_read
```
### SONY:
The following commands will take an image
```bash

```
### ALTUM:
The following command will wait for you to take an image (Push the bottom in the SDL2 for this)
```bash

```
### LiDAR
For testing our LiDAR first we need to 
```bash
ifconfig
cd
sudo cp Agroscope/ASPEN/Software/transfer/01-network-manager-all.yaml /etc/netplan
sudo netplan apply
ifconfig
```
Technically at this point, we can close the box (I wouldn't).

## Software installation
### ***Python***
- We will install pip and create a virtual environment
```bash
sudo apt-get -y install python3-pip
python3 -m pip install --upgrade pip
sudo apt-get install python3-venv
cd ~/Agroscope
python3 -m venv ASPEN_env
echo "" >> ~/.bashrc
echo "#ASPEN project configuration" >> ~/.bashrc
echo "source ~/Agroscope/ASPEN_env/bin/activate" >> ~/.bashrc
source ~/.bashrc
python3 -m pip install --upgrade pip
# We also need numpy for the next step. But, there was a problem with numpy and jetson so we will use a specific version #https://stackoverflow.com/questions/65631801/illegal-instructioncore-dumped-error-on-jetson-nano
python3 -m pip install numpy==1.19.4 
```
### ***Realsense***
To use realsense we need some specific software versions:
- [Opencv 4.5.3](#opencv)
- Realsense firmware 5.12.12.100
- [librealsense 2.43.0](#librealsense)
- [ros wrapper 2.2.23](#librealsense-ros-wrapper)

#### ***OpenCV***
OpenCV is used by RealSense and R3Live (>=3.3), so we will start by instaling it from source (so we have gpu support). That also means that is not necessary to install it using pip later, as it will be already. I had some issues with realsense, more details [here](https://github.com/IntelRealSense/realsense-ros/issues/2326).

```bash
cd ~/Agroscope && mkdir Third_party && cd Third_party
wget https://github.com/opencv/opencv/archive/refs/tags/4.5.3.zip
unzip 4.5.3.zip
rm 4.5.3.zip
cd opencv-4.5.3
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D PYTHON_DEFAULT_EXECUTABLE=/usr/bin/python3.6 \
  -D BUILD_opencv_python3=ON \
  -D WITH_CUDA=OFF ..
# [WARNING]: The following command take around 2 hours or more
sudo make install
# If all works we should have a file here
ls -l /usr/local/lib/python3.6/dist-packages/cv2/python-3.6
# To our python venv!
cp /usr/local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-aarch64-linux-gnu.so ~/Agroscope/ASPEN_env/lib/python3.6/site-packages
# Checking version :D
python3 -c 'import cv2; print(cv2); print(cv2.getBuildInformation())'
```

#### ***librealsense***
We are just missing librealsense and wrapper. For this:
```bash
# Librealsense 2.43
sudo apt install ros-melodic-ddynamic-reconfigure
# Following: https://github.com/IntelRealSense/realsense-ros/issues/1967#issuecomment-1029789663
# We need acces to CUDA 
echo "export CUDA_HOME=/usr/local/cuda" >> .bashrc
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64" >> .bashrc
echo "export PATH=$PATH:$CUDA_HOME/bin" >> .bashrc
source .bashrc
# Now we can start with librealsense
cd ~/Agroscope/Third_party
wget https://github.com/IntelRealSense/librealsense/archive/refs/tags/v2.43.0.zip
unzip v2.43.0.zip
rm v2.43.0.zip
cd librealsense-2.43.0
mkdir build && cd build
cmake -DFORCE_RSUSB_BACKEND=ON \
-DBUILD_PYTHON_BINDINGS:bool=true \
-DPYTHON_EXECUTABLE=/usr/bin/python3.6 \
-DCMAKE_BUILD_TYPE=release \
-DBUILD_EXAMPLES=true \
-DBUILD_GRAPHICAL_EXAMPLES=true \
-DBUILD_WITH_CUDA:bool=true ..
make -j16
sudo make install
# If everything works and the camera is connected, the camera should show up
sudo rs-enumerate-devices
#Lets move some files to its rigth place
sudo cp ~/Agroscope/ASPEN/Software/transfer/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger
```

### ***ROS***
- We will use ROS melodic as has work without problems so far
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt-get update
sudo apt-get install ros-melodic-desktop-full
echo "#ROS configuration" >> .bashrc
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
sudo apt-get install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential
sudo rosdep init
rosdep update
```

### ***librealsense ROS wrapper***
```bash
# Installation
cd ~/Agroscope/ASPEN/Software/ROS/src
wget https://github.com/IntelRealSense/realsense-ros/archive/refs/tags/2.2.23.zip
unzip 2.2.23.zip
rm 2.2.23.zip
# Before continue there are some problems to fix:
sudo nano ~/Agroscope/ASPEN/Software/ROS/src/realsense-ros-2.2.23/realsense2_camera/src/base_realsense_node.cpp
# https://github.com/IntelRealSense/realsense-ros/issues/910 -> add std:: in front of find_if when is missing (Line 234, 2282, 2292)
# We have a problem as we have opencv4...
sudo nano /opt/ros/melodic/share/cv_bridge/cmake/cv_bridgeConfig.cmake
# Andd change:
# set(_include_dirs "include;/usr/include;/usr/include/opencv")
# to:
# set(_include_dirs "include;/usr/include;/usr/include/opencv4")
```

### ROS packages
At this point we will install our ROS packages. As we have an external IMU we will be using a custom version of the livos_ros_driver. More details [here](https://github.com/hku-mars/r2live/issues/56)
```bash
cd ..
catkin_make clean 
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release 
catkin_make install
# We can test it with:
echo "source ~/Agroscope/ASPEN/Software/ROS/devel/setup.bash" >> .bashrc
cd
source .bashrc
roslaunch realsense2_camera rs_camera.launch
# And we need to transfer a file.For details of rs_agroscope.launch, check ASPEN/Software/ctrl/debug/20220419_RS_configuration.md. 
sudo cp ~/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch ~/Agroscope/ASPEN/Software/ROS/src/realsense-ros-2.2.23/realsense2_camera/launch
## If everthing works we should be able to run this and see gpu usage in other window
roslaunch realsense2_camera rs_agroscope.launch
## In a second window:
tegrastats
```

### ***Livox***
- We need to install Livos-SDK
```bash
cd ~/Agroscope/Third_party
git clone https://github.com/Livox-SDK/Livox-SDK.git
cd Livox-SDK
cd build
cmake .. 
make
sudo make install
```
- We can test it with the following:
```bash
cd sample_cc/lidar
./lidar_sample_cc -c "3GGDJ4H00100041" -l
```

## Appearence
We have an issue with the screen resolution that doesnt allow us to change to gnome so first:
- In the logging area select your user and then ubuntu 
- Allow autologging using changing
```bash
sudo nano /etc/gdm3/custom.conf
#change to true
```
-Setting wallpaper and other small things
```bash
gsettings set org.gnome.desktop.background picture-uri 'file:///home/aspen/Agroscope/ASPEN/Software/Images/Wallpaper_xavier.png'
# Show the icons
sudo cp ~/Agroscope/ASPEN/Software/transfer/Agroscope.desktop ~/Desktop
sudo cp ~/Agroscope/ASPEN/Software/transfer/Agroscope_patch.desktop ~/Desktop
# Give permition to our program
sudo chown aspen:aspen ~/Desktop/Agroscope.desktop
sudo chown aspen:aspen ~/Desktop/Agroscope_patch.desktop
# Continuos backspacing
gsettings set org.gnome.desktop.peripherals.keyboard repeat true
# Do not block
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled  false
# Tweaks
sudo apt install chrome-gnome-shell
sudo apt install gnome-tweaks
#Missing keys. The keyboard is not 100% visible. to fix it (https://github.com/pop-os/gnome-shell-theme/issues/34)
#Go to tweaks and change font, scaling factor to 0.61
# Remove icons that we dont want to show (trash and disks)
# Side side bar: autohide on (Settings::dock)
# remove chromium icon that keep apearing
sudo rm /etc/xdg/autostart/nvchrome.sh
```

## ASPEN
- To run aspen we basically just need some python libraries:
```bash
cd ~/Agroscope/ASPEN/Software
python3 -m pip install -r requirements.txt
```



# For checking gpu 
tegrastats









cd ~/Desktop

gsettings set org.gnome.shell.extensions.desktop-icons show-home true
cd 
cd Desktop


```





























## YOLO
We will need some packages
```bash

# It look that numpy has a problem with jetson, so we need a specific version
python3 -m pip install numpy==1.19.4
#python3 -m pip install opencv-python Not sure if I need this oone as i have my local version 
cp /usr/local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-aarch64-linux-gnu.so /home/aspen/Agroscope/Python_venvironments/YOLO_v5_venv/lib/python3.6/site-packages/
python3 -m pip install kivy
python3 -m pip install pygame
python3 -m pip install screeninfo
python3 -m pip install pexpect
python3 -m pip install pyyaml
python3 -m pip install rospkg
python3 -m pip install ffpyplayer
python3 -m pip install pillow
python3 -m pip install Jetson.GPIO

#Torch, from https://cognitivexr.at/blog/2021/03/11/installing-pytorch-and-yolov5-on-an-nvidia-jetson-xavier-nx.html
python3 -m pip install -U future psutil dataclasses typing-extensions pyyaml tqdm seaborn
wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl 
python3 -m pip install torch-1.8.0-cp36-cp36m-linux_aarch64.whl
# Install torchvision v0.9.0 (version for torch 1.8)
sudo apt install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev
python3 -m pip install --upgrade pillow
git clone --branch v0.9.0 https://github.com/pytorch/vision torchvision
cd torchvision
export BUILD_VERSION=0.9.0
python3 setup.py install --user
cd ..

```
We can Check that torch is working and using CUDA with:
```python3
import torch
torch.cuda.is_available()
```

# ***4. BMI088***
- We can actually using the once from RPI! It works :D. Just use make clean to create the executable
```bash
cd /home/aspen/Agroscope/ASPEN/Software/ROS/src/bmi088/scripts
chmod +777 imu.py
cd ..
cd src
make clean
cd ../../..
catkin_make
```
# ***5. R3Live***
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


# 6. Yolov5 and sort
We can copy the repositories from my github
```bash
cd 
cd Agroscope/Data_processing/2_realtime/tools/ML
git clone https://github.com/Camilochiang/yolov5
git clone https://github.com/Camilochiang/sort
cd yolov5
ln -s Agroscope/Data_processing/2_realtime/tools/ML/sort sort
python3 -m pip install -r requirements.txt
```



8. Testing and before starting
We need some paramters of the camera
```bash
rs-enumerate-devices -c
```
For testing, we can follow this steps after running ASPEN_patch
```bash
cd
# To check that all topics are present
rostopic list
rosrun bmi088 imu.py
```
- If there is any error we can check the logs here:
```bash
cat /Agroscope/ASPEN/Software/ctrl/log.log
cat /var/log/syslog
```

# Issues and Comments
We could use it as a service, but jetson get quite slow, not sure why.
```bash
sudo cp /home/aspen/Agroscope/ASPEN/Software/transfer/Agroscope.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable Agroscope
sudo systemctl start Agroscope
sudo systemctl status Agroscope
```
# Having issues with livox
sudo nano /etc/dhcp/dhclient.conf
uncoment alias? change ip?

# resources usage
systemctl stop packagekit
systemctl disable packagekit


## Extracting CAMERA INFO
```bash
rostopic echo /camera/color/camera_info
```

## REALSENSE CONFIGURATION
- you cannot clip distances with the ROS WRAPPER (https://github.com/IntelRealSense/realsense-ros/issues/1412) but you can filter values higher than something for example 10 (m) in our case

## COMPRESING
So I tried compressing images and with ROS2 jetson can only do 19 FPS at 1920 x 1080. as 15 FPS is more than enough, we will keep both, deepth and nmormal at 15 FPS, recorded as compressed

## Check opencv
pkg-config --modversion opencv


# Usefull links
https://www.jetsonhacks.com/nvidia-jetson-xavier-nx-gpio-header-pinout/


# Fixing opencv
```bash
sudo find -name librealsense2_camera.so
# If the file is in two places (that should be: ROS and /opt/ros), delete the librealsense2_camera.so file in the/home/xxx/catkin_ws/devel/lib/path
```

# Fixing the mess with librealsense and ROS wrapper
- We want ROS wrapper to be installed from source. For this the first step is to clean up previus instalations
```bash
# Removing librealsense
sudo apt purge *librealsense2*
# Removing ros wrapper
sudo apt remove ros-melodic-realsense2-camera
sudo apt remove ros-melodic-librealsense2
cd
# Now we can check that nothing is here
cd /opt/ros/melodic/include
ls -l | grep librealsense
```

- LibRealSense:
- On PC: 
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u
sudo apt-get install librealsense2-dkms
sudo apt-get install librealsense2-utils
sudo apt-get install librealsense2-dev
sudo apt-get install librealsense2-dbg
```

- Wrapper:
- On PC
```

```

- Now we want to use my own version of opencv
- My own version of image_transport 
    For this we need two things:
    1. My workspace need to be defined first in the variable ROS_PACKAGE_PATH (Which we can check with printenv | grep ROS_PACKAGE_PATH). This is basically the case when we source a new catkin_workspace.
    2. Your *include_directories* directives set up so that your _local_ packages appear first ie: include_directories( include ${excellent_package_INCLUDE_DIRS} ${catkin_INCLUDE_DIRS} )

- Installing realsense-ros from source
```bash
cd /home/$USER/Agroscope/ASPEN/Software/ROS/src
wget https://github.com/IntelRealSense/realsense-ros/archive/refs/tags/2.3.2.zip
unzip 2.3.2.zip
rm 2.3.2.zip

# Then, I modify /home/ubuntu/Agroscope/ASPEN/Software/ROS/src/realsense-ros-2.3.2/realsense2_camera/CMakeLists.txt So it find opencv :D in my PC!
catkin_init_workspace
cd ..
catkin_make clean
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release
catkin_make install
```

source /home/ubuntu/Agroscope/Data_processing/2_realtime/ROS/devel/setup.bash





Error with lz4
```bash
sudo mv /usr/include/flann/ext/lz4.h /usr/include/flann/ext/lz4.h.bak
sudo mv /usr/include/flann/ext/lz4hc.h /usr/include/flann/ext/lz4.h.bak

sudo ln -s /usr/include/lz4.h /usr/include/flann/ext/lz4.h
sudo ln -s /usr/include/lz4hc.h /usr/include/flann/ext/lz4hc.h
```





# In case we have problems with realsense-ros
cd /usr/include
sudo ln -s opencv4 opencv # Create a symbolic link from opencv to opencv4 and re try 
python3 -c 'import cv2; print(cv2); print(cv2.getBuildInformation())'








- Apearance
```bash

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
```

 - We need to install a driver evdev
This is the important part actually, dont remember why
```bash
sudo apt-get install xserver-xorg-input-evdev
# And make it higher in number that the old one
cd /usr/share/X11/xorg.conf.d
sudo mv 40-libinput.conf 10-libinput.conf 
sudo mv 10-evdev.conf 11-evdev.conf 
```
- Dont remember if this is been used or not. I doub it so is not necessary
```bash
sudo apt install libinput-tools libinih-dev libxdo-dev
#https://extensions.gnome.org/extension/1140/disable-gestures/
#https://github.com/Hikari9/comfortable-swipe
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
```
- Other utilities
```bash
sudo -H pip3 install jetson-stats
sudo apt-get install qt5-default
sudo apt-get -y install nano
sudo apt install htop
sudo apt install curl
ethtool -T eth0
sudo apt update
sudo apt install linuxptp

# Block keyboard from apearing
https://extensions.gnome.org/extension/3222/block-caribou-36/

# To unblock we can use
```bash
gsettings set org.gnome.shell disable-user-extensions true
gsettings set org.gnome.shell disable-user-extensions false
```
- Changing power consuption of NVIDIA JETSON NANO: We will be using option 8
```bash
#https://developer.ridgerun.com/wiki/index.php?title=Xavier/JetPack_4.1/Performance_Tuning/Tuning_Power
sudo /usr/sbin/nvpmodel -m
```
1-15w-4core
2-15w-6core
3-10w-2core
4-10w-4core
5-10w-desk
6-20w-2-core
7-20w-4core
8-20w-6core




- We have to update Cmake for librealsense
```bash
#sudo apt remove --purge --auto-remove cmake
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
And we may want to check other things
```bash
sudo apt-cache show nvidia-jetpack
sudo apt-cache show nvidia-l4t-jetson-multimedia-api
nvcc --version
cat /usr/include/cudnn_version.h
```





sudo groupadd -f -r gpio
sudo usermod -a -G gpio aspen
sudo udevadm control --reload-rules && sudo udevadm trigger





3. **Copy new rules**
sudo cp /home/aspen/Agroscope/Python_venvironments/YOLO_v5_DeepSort_venv/lib/python3.8/site-packages/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/


```bash
sudo cp lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/

