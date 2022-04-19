# REALSENSE CONFIGURATION

## Laser power to 0
There is interference with one of the channels of the spectral camera, so we will not use the laser from realsense

## Filters:
- Why no colorizing? Well, dont need to compress the images and is faster to use if they are not compressed. RS can use compresing + colorizing to give a RGB image from the depth, but that take time
- Why not holefilling? not recomended as it create weird data.
- We use: Disparity, to get better resolution at short distances; spatial and  temporal

## Enable conf = false
- When I set it to true, no me


## Align depth image with color
when using different resolutions the wrapper didnt giv any output in /camera/aligned_depth_to_color/image_raw. The topic was there, but no output.



# TOPICS 
/camera/color/camera_info
/camera/color/image_raw
/camera/color/image_raw/compressed
/camera/color/image_raw/compressed/parameter_descriptions
/camera/color/image_raw/compressed/parameter_updates
/camera/color/image_raw/compressedDepth
/camera/color/image_raw/compressedDepth/parameter_descriptions
/camera/color/image_raw/compressedDepth/parameter_updates
/camera/color/image_raw/theora
/camera/color/image_raw/theora/parameter_descriptions
/camera/color/image_raw/theora/parameter_updates
/camera/color/metadata
/camera/depth/camera_info
/camera/depth/image_rect_raw
/camera/depth/image_rect_raw/compressed
/camera/depth/image_rect_raw/compressed/parameter_descriptions
/camera/depth/image_rect_raw/compressed/parameter_updates
/camera/depth/image_rect_raw/compressedDepth
/camera/depth/image_rect_raw/compressedDepth/parameter_descriptions
/camera/depth/image_rect_raw/compressedDepth/parameter_updates
/camera/depth/image_rect_raw/theora
/camera/depth/image_rect_raw/theora/parameter_descriptions
/camera/depth/image_rect_raw/theora/parameter_updates
/camera/depth/metadata
/camera/disparity_end/parameter_descriptions
/camera/disparity_end/parameter_updates
/camera/disparity_start/parameter_descriptions
/camera/disparity_start/parameter_updates
/camera/extrinsics/depth_to_color
/camera/realsense2_camera_manager/bond
/camera/rgb_camera/auto_exposure_roi/parameter_descriptions
/camera/rgb_camera/auto_exposure_roi/parameter_updates
/camera/rgb_camera/parameter_descriptions
/camera/rgb_camera/parameter_updates
/camera/spatial/parameter_descriptions
/camera/spatial/parameter_updates
/camera/stereo_module/auto_exposure_roi/parameter_descriptions
/camera/stereo_module/auto_exposure_roi/parameter_updates
/camera/stereo_module/parameter_descriptions
/camera/stereo_module/parameter_updates
/camera/temporal/parameter_descriptions
/camera/temporal/parameter_updates
/diagnostics
/imu
/livox/lidar
/rosout
/rosout_agg
/tf
/tf_static


What modifications were need it to realsense (Present in rs.launch)?
- Turn off laser = line 3 set to 0 https://github.com/IntelRealSense/realsense-ros/issues/1195
- Dpth at 1280 x 720 at 30 FPS : lines 23 to 26
- RGB at 1920 x 1080 30 FPS : lines 41 to 44
