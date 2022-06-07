cmake_minimum_required(VERSION 3.0.2)
project(bmi088)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
  sensor_msgs
  genmsg
)

generate_messages(
   DEPENDENCIES
   std_msgs  # Or other packages containing msgs
   sensor_msgs
)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES bmi088
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs genmsg
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

## The important part here is to share the library previusly created with .so
#add_executable(bmi088_2ROS src/bmi088_2ROS.cpp)
#target_link_libraries(bmi088_2ROS ${catkin_LIBRARIES} ${PROJECT_SOURCE_DIR}/src/libtest.so)
#add_dependencies(bmi088_2ROS bmi088_generate_messages_cpp)