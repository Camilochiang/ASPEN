# Comments:
Here there are some comments in the problems that I had when installing all this material together

## 20220420
Libraries problem for realsense in xavier NX
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

    ## Other tries:
    ## Try 3 Opencv 3.4.16 no CUDA / firmware 5.13.0.50 /lib 2.50 / wrapper 2.3.2
    Is not working. lets update all to the last version

## 20220520
After recording some bags (and it looks that is working), is time to start analysing some data.
    First we will implement a boundary box extraction for data analysis
    Second, meanwhile we wait for FAST-LIVO, we will add the depth frame to the algorithm

We start today by creating a new ROS package that is wrapper of yolo v5 , sort and also draw polygons arround fruits


## 20220602
I have been working in the tracker. Tried specially a C++ implementation of sort and is not really working as it compite with r3live in resources. I will re try with python sort even if it take a bit of longer time to process. Also the idea is that if you see a tomate for more than 10 frames then it should produce a ros message. (something like that). I should also try with the realtime implementation of bytetrack. I have hopes on that one 

# Trying to link to python3
catkin_make -DCATKIN_ENABLE_TESTING=False -DCMAKE_BUILD_TYPE=Release

## 22020629
I have a look to the altum camera data. It look that the GPS do not connect so we cannot use it. Can we can do is to may be use the IMU from the DSL2, but the data is not soo much.
I also decided to try [FAST_LIO_PC](https://github.com/yanliang-wang/FAST_LIO_LC) to see if it work better for closing 
