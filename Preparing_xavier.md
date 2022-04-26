# Preparing xavier NX
## Goal
This file have as goal to describe the software configuration that is used in the project ASPEN

## Content
1. [General configuration](##General-configuration)
2. [OpenCV](##OpenCV)
2. ROS
    1. Livox
        1. Ethernet
    2. RealSense
3. Python
    1. Python env
4. BMI088        
5. R3Live
6. YOLOv5 and sort
7. Appearence
8. Icons

## General configuration
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
-  Missing keys
The keyboard is not 100% visible. to fix it
https://github.com/pop-os/gnome-shell-theme/issues/34
Go to tweaks and change font, scaling factor to 0.61
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
# Continuos backspacing
gsettings set org.gnome.desktop.peripherals.keyboard repeat true
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

## OpenCV
OpenCV is used by RealSense and R3Live (>=3.3), so we will start by instaling it from source. That also means that is not necessary to install it using pip later, as it will be already
```bash
cd 
cd Agroscope/Data_processing/2_realtime/tools/software
wget https://github.com/opencv/opencv/archive/3.4.16.zip
unzip 3.4.16.zip
rm 3.4.16.zip
cd opencv-3.4.16
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D PYTHON_EXECUTABLE=/usr/bin/python3.6 \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D WITH_CUDA=OFF ..
# [WARNING]: Do we really want opencv to use python3? I guess so, but not sure.
# [WARNING]: The following command take around 1 hour or more
sudo make install
pkg-config --modversion opencv
# we can confirm with
python3 -c 'import cv2; print(cv2); print(cv2.getBuildInformation())'
# We should copy this so file later to our python venv!
cp /usr/local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-aarch64-linux-gnu.so //home/aspen/Agroscope/Python_venvironments/YOLO_v5_venv/lib/python3.6/site-packages
```

# Updating opencv to 4.5.3
Im having issues with realsense, more details [here](https://github.com/IntelRealSense/realsense-ros/issues/2326)
```bash
cd 
cd Agroscope/Data_processing/2_realtime/tools/software
wget https://github.com/opencv/opencv/archive/refs/tags/4.5.3.zip
unzip 4.5.3.zip
rm 4.5.3.zip
cd opencv-4.5.3
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D WITH_CUDA=OFF ..
# [WARNING]: The following command take around 2 hours or more
sudo make install
# Checking version :D
pkg-config --modversion opencv
# we can confirm with both of these commands:
jtop 
python3 -c 'import cv2; print(cv2); print(cv2.getBuildInformation())'
# Again, We should copy this so file later to our python venv!
cp /usr/local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-aarch64-linux-gnu.so /home/aspen/Agroscope/Python_venvironments/YOLO_v5_venv/lib/python3.6/site-packages
# We should check it
source /home/$USER/Agroscope/Python_venvironments/YOLO_v5_venv/bin/activate
python3 -c 'import cv2; print(cv2); print(cv2.getBuildInformation())'
deactivate
# In case we have problems with realsense-ros
cd /usr/include
sudo ln -s opencv4 opencv # Create a symbolic link from opencv to opencv4

```


## ***2 ROS***
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
## 2.1 Livox
- First we need to install Livos-SDK
```bash
cd
cd Agroscope/Data_processing/2_realtime/tools/software
git clone https://github.com/Livox-SDK/Livox-SDK.git
cd Livox-SDK
cd build
cmake .. #-DCMAKE_TOOLCHAIN_FILE=/home/aspen/Agroscope/Data_processing/2_realtime/tools/software/vcpkg/scripts/buildsystems/vcpkg.cmake
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
cd Agroscope/ASPEN/Software/ROS/src
#scp -r /home/ubuntu/Agroscope/Data_processing/2_realtime/ROS_spaces/ROS_workspace_3/src/livox_ros_driver_for_R2LIVE aspen@192.168.0.46:
git clone https://github.com/Camilochiang/livox_ros_driver_external_IMU.git
```
we can test it later.

### 2.1.1 Wifi and Ethernet connection
- Preparing our network: From the manual
***All Mid-70 sensors are set to static IP address mode by default with an IP address of 192.168.1.XX. The default subnet is 255.255.255.0 and gateways are 192.168.1.1***
```bash
sudo apt install netplan.io
sudo cp /home/aspen/Agroscope/ASPEN/Software/lib/01-network-manager-all.yaml /etc/netplan
sudo netplan generate
sudo netplan apply
```
- Country code
```bash
sudo nano /etc/default/crda and add CH
```
## 2.2  Realsense
Originally I installed directly following the instructions here bellow, but there are some problems of realsense and jetson. Also, it didnt have GPU support, so we finally follow version 2:

**Original instructions**
```bash
#We need two installations: first librealsense
cd Agroscope/Data_processing/2_realtime/tools/software
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh
./vcpkg integrate install
##CMake projects should use: "-DCMAKE_TOOLCHAIN_FILE=/home/aspen/Agroscope/Data_processing/2_realtime/tools/software/vcpkg/scripts/buildsystems/vcpkg.cmake"
./vcpkg install realsense2
#Then ROS wrapper
sudo mv /home/ubuntu/Agroscope/ASPEN/Software/lib/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger
sudo apt install ros-$ROS_DISTRO-realsense2-camera
#Then we have to resource the bash file And it should work
source ~/.bashrc
sudo cp /home/aspen/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch /opt/ros/melodic/share/realsense2_camera/launch
roslaunch realsense2_camera rs_agroscope.launch
# sudo nano /opt/ros/melodic/share/realsense2_camera/launch/rs_agroscope.launch
```
**Version 2:**
```bash
# First we have to clean the previus one
sudo apt remove ros-melodic-realsense2-camera
sudo apt remove ros-melodic-ddynamic-reconfigure
sudo apt remove ros-melodic-librealsense2

sudo apt install ros-melodic-ddynamic-reconfigure
# Following: https://github.com/IntelRealSense/realsense-ros/issues/1967#issuecomment-1029789663
cd
echo "export CUDA_HOME=/usr/local/cuda" >> .bashrc
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64" >> .bashrc
echo "export PATH=$PATH:$CUDA_HOME/bin" >> .bashrc
source .bashrc

cd /home/aspen/Agroscope/Others
wget https://github.com/IntelRealSense/librealsense/archive/refs/tags/v2.43.0.zip
unzip v2.43.0.zip
rm v2.43.0.zip
cd librealsense-2.43.0
mkdir build
cd build
cmake -DFORCE_RSUSB_BACKEND=ON \
-DBUILD_PYTHON_BINDINGS:bool=true \
-DPYTHON_EXECUTABLE=/usr/bin/python3.6 \
-DCMAKE_BUILD_TYPE=release \
-DBUILD_EXAMPLES=true \
-DBUILD_GRAPHICAL_EXAMPLES=true \
-DBUILD_WITH_CUDA:bool=true ..
make -j16
sudo make install
# If everything works, the camera should show up
rs-enumerate-devices
```

And now the wrapper: 
First lets move some files to its rigth place
```bash
cd
sudo cp /home/aspen/Agroscope/ASPEN/Software/lib/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger
sudo cp /home/aspen/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch /home/aspen/Agroscope/ASPEN/Software/ROS/src/realsense-ros-2.2.23/realsense2_camera/launch
```
And now install the wrapper
```bash
cd /home/aspen/Agroscope/ASPEN/Software/ROS/src
wget https://github.com/IntelRealSense/realsense-ros/archive/refs/tags/2.2.23.zip
unzip 2.2.23.zip
rm 2.2.23.zip
# Before continue there are some problems to fix:
# https://github.com/IntelRealSense/realsense-ros/issues/910 -> add std:: in front of find_if when is missing (2 places I believe)
catkin_init_workspace
cd ..
catkin_make clean 
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release 
catkin_make install
```
For details of rs_agroscope.launch, check ASPEN/Software/ctrl/debug/20220419_RS_configuration.md. We can test it with:
```bash
source /home/$USER/Agroscope/ASPEN/Software/ROS/devel/setup.bash
roslaunch realsense2_camera rs_camera.launch
```

## Try 3 Opencv 3.4.16 no CUDA / firmware 5.13.0.50 /lib 2.50 / wrapper 2.3.2
Is not working. lets update all to the last version
```bash
#FIRMWARE
cd Agroscope/ASPEN/Software/transfer/
rs-fw-update -f Signed_Image_UVC_5_13_0_50.bin

#LibRealSense
cd /home/$USER/Agroscope/Others
sudo rm -r librealsense-2.43.0
wget https://github.com/IntelRealSense/librealsense/archive/refs/tags/v2.50.0.zip
unzip v2.50.0.zip
rm v2.50.0.zip
cd librealsense-2.50.0
mkdir build && cd build
# For CUDA SUPPORT:
cmake -DFORCE_RSUSB_BACKEND=ON \
-DBUILD_PYTHON_BINDINGS=true \
-DPYTHON_EXECUTABLE=/usr/bin/python3.6 \
-DCMAKE_BUILD_TYPE=release \
-DBUILD_EXAMPLES=true \
-DBUILD_GRAPHICAL_EXAMPLES=true \
-DBUILD_WITH_CUDA=true ..

# on my pc is not working..
sudo apt-get 

#ROS wrapper
cd /home/aspen/Agroscope/ASPEN/Software/ROS/src
#wget https://github.com/IntelRealSense/realsense-ros/archive/refs/tags/2.3.2.zip
# I had to download it manualy
unzip 2.3.2.zip
rm 2.3.2.zip
catkin_init_workspace
cd ..
catkin_make clean
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release
catkin_make install

source /home/$USER/Agroscope/ASPEN/Software/ROS/devel/setup.bash

# We can move our configuration
sudo cp /home/$USER/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch /opt/ros/melodic/share/realsense2_camera/launch
roslaunch realsense2_camera rs_agroscope.launch
```

## Try 4: Opencv 4.5.3 / firmware 5.12.12.100 / lib 2.43.0 / wrapper 2.2.23
```bash
cd
cd Agroscope/ASPEN/Software/transfer/
rs-fw-update -f Signed_Image_UVC_5_12_12_100.bin

#LibRealSense
cd /home/$USER/Agroscope/Others
sudo rm -r librealsense-2.50.0
wget https://github.com/IntelRealSense/librealsense/archive/refs/tags/v2.43.0.zip
unzip librealsense-2.43.0.zip
rm librealsense-2.43.0.zip
cd librealsense-2.43.0
mkdir build && cd build
cmake -DFORCE_RSUSB_BACKEND=ON \
-DBUILD_PYTHON_BINDINGS=true \
-DPYTHON_EXECUTABLE=/usr/bin/python3.6 \
-DCMAKE_BUILD_TYPE=release \
-DBUILD_EXAMPLES=true \
-DBUILD_GRAPHICAL_EXAMPLES=true \
-DBUILD_WITH_CUDA=true ..
make -j4
sudo make install

#Checking dynamic presence
sudo apt install ros-melodic-ddynamic-reconfigure

#Wrapper
cd /home/aspen/Agroscope/ASPEN/Software/ROS/src
wget https://github.com/IntelRealSense/realsense-ros/archive/refs/tags/2.2.23.zip
unzip 2.2.23.zip
rm 2.2.23.zip
catkin_init_workspace
cd ..
catkin_make clean
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release
catkin_make install

source /home/$USER/Agroscope/ASPEN/Software/ROS/devel/setup.bash
roslaunch realsense2_camera rs_camera.launch

#WORKING! :D
cp /home/$USER/Agroscope/ASPEN/Software/transfer/rs_agroscope.launch /home/aspen/Agroscope/ASPEN/Software/ROS/src/realsense-ros-2.2.23/realsense2_camera/launch
roslaunch realsense2_camera rs_agroscope.launch
```

Now that we have everything in ROS, we can also test the lidar
```bash
roslaunch livox_ros_driver livox_lidar_msg.launch
```



# Note: remove spatial filter maybe later. if CPU usage is too high
https://github.com/IntelRealSense/realsense-ros
https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_jetson.md#building-from-source-using-native-backend
https://github.com/IntelRealSense/realsense-ros/issues/2176



Another option for the wrapper:
```bash
sudo apt list -a ros-melodic-realsense2-camera
sudo apt-get remove ros-melodic-realsense2-camera
sudo apt-get remove ros-melodic-realsense2-description


```


## ***3. Python***
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

Check that torch is working and using CUDA
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

7. Icons
- We basically only need to move the icons
```bash
cp Agroscope/ASPEN/Software/transfer/Agroscope.desktop /Desktop
cp Agroscope/ASPEN/Software/transfer/Agroscope_patch.desktop /Desktop
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


# preparing gitthub
- You can add a a submodule like this:
cd /home/ubuntu/Agroscope/ASPEN/Software/ROS/src
git submodule add https://github.com/Camilochiang/livox_ros_driver_external_IMU
git submodule add https://github.com/Camilochiang/r3live


