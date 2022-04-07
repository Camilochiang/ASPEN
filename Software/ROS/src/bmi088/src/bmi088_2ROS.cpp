#include "ros/ros.h"
#include "std_msgs/String.h"
#include "sensor_msgs/Imu.h"
#include <sstream>
#include <signal.h>
#include <iostream>

extern "C" {
  uint32_t tm;
  double ax, ay, az, gx, gy, gz;

  int starter();
  int get_data();

}

void signal_handler(int s)
{
  ROS_INFO_STREAM("Caught signal. Closing BMI088 streamer");
  exit(1); 
}

int main(int argc,char** argv)
{
  ROS_INFO_STREAM("BMI088 streamer started");

  //Start ROS;
  ros::init(argc, argv, "bmi088_streamer", ros::init_options::NoSigintHandler);
  signal(SIGINT, signal_handler);
  ros::NodeHandle n;
  ros::Publisher bmi0888_pub = n.advertise<sensor_msgs::Imu>("/imu", 1000);

  ros::Rate loop_rate(200);

  //starter();
  int count = 0;

  sensor_msgs::Imu msg;
  std::stringstream ss;

  starter();

  while (ros::ok())
  { 
    //get_data();
    msg.header.stamp = ros::Time::now();
    msg.linear_acceleration.x = ax;
    msg.linear_acceleration.y = ay;
    msg.linear_acceleration.z = az;
    msg.angular_velocity.x = gx;
    msg.angular_velocity.y = gy;
    msg.angular_velocity.z = gz;

    bmi0888_pub.publish(msg);

    ros::spinOnce();
    loop_rate.sleep();
    ++count;
  }
  return 0;
}