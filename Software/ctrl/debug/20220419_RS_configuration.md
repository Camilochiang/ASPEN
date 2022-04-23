# REALSENSE CONFIGURATION

Realsense offer several configurations (librealsense) and specially the ROS wrapper, have either issues with jetson, so this is the best configuration that we got (considering that jetson xavier NX cannot compress more than 19 FPS at 1920 x 1280

## Laser power to 0
There is interference with one of the channels of the spectral camera, so we will not use the laser from realsense

## /camera/colorizer/histogram_equalization_enabled: false
I dont remember why 

## Filters:
- disparity, spatial, temporal
	- Why no colorizing? Well, dont need to compress the images and is faster to use if they are not compressed. RS can use compresing + colorizing to give a RGB image from the depth, but that take time
	- Why not holefilling? not recomended as it create weird data.
	- We use: Disparity, to get better resolution at short distances; spatial and  temporal

## enable_sync and align_depth = true
- When we set both to true doesn work in jetson, so we need a special combination of software
	https://github.com/IntelRealSense/realsense-ros/issues/1967#issuecomment-1029789663
	- Jetson Nano B01with Jetpack 4.6
	- ROS melodic
	- librealsense 2.43.0 build from source with CUDA support according to [this guide](https://github.com/IntelRealSense/librealsense/issues/6964#issuecomment-707501049)
	- ROS Wrapper 2.2.23 build from source
		- It need to be modified: in realsense-ros-2.2.23/realsense2_camera/src/base_realsense_node.cpp add std:: in from of find_if where is missing
	- D415 camera with firmware 5.12.12.100 (March 2021, Release 5.5) ??
		We can change the firmware with ```rs-fw-update -l```
		Then with the serial number we can run: ```rs-fw-update -f Signed_Image_UVC_5_12_12_100.bin```
		Other firmware https://dev.intelrealsense.com/docs/firmware-releases


## RGB configuration
- RGB at 1920 x 1080 30 FPS : lines 41 to 44

## Depth configuration
- Dpth at 1280 x 720 at 30 FPS : lines 23 to 26



## New instalation
DFORCE_RSUSB_BACKEND
