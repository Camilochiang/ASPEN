#!/usr/bin/env python
import rospy
import subprocess
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
import os

# This file send the IMU data to ROS. It need to have the executable file (made from src)

class ImuAttributes(Imu):
    """ Subclass of sensor_msgs/Imu, for filling in IMU attributes """
    def __init__(self, frame_id):
        super(ImuAttributes, self).__init__(
            orientation_covariance=[0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0],
            angular_velocity_covariance=[0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0],
            linear_acceleration_covariance=[0.0, 0.0, 0.0,
                                            0.0, 0.0, 0.0,
                                            0.0, 0.0, 0.0])
        if frame_id:
            self.header.frame_id = frame_id

class ImuMessages(object):
    """ ROS message translation for bmi_088"""
    def __init__(self):
        """ Start the publisher"""
        self.pubs = [rospy.Publisher('imu', Imu, queue_size = 0)]
        self.imus = [ImuAttributes('extermal_imu')]

        rospy.init_node('imu_bmi088', anonymous=False)
 
    def publish(self, hz):
        """ Publish a ROS Range message for each reading.
        :param hz: Frecuency in hertz
        :type hz: int
        """
        imu = int(0)
        msg = self.imus[imu]
        
        rate = rospy.Rate(hz) # 10hz
        print("Starting to publish")
        while not rospy.is_shutdown():
            rospy.loginfo(msg)
            values = thread.stdout.readline().split(",")
            #msg.angular_velocity = Vector3(values[0], values[0], values[0])
            #msg.linear_acceleration = Vector3(x, y, z)            
            msg.linear_acceleration = Vector3(float(values[1].split(":")[1])*9.81, 
                float(values[2].split(":")[1])*9.81, 
                float(values[3].split(":")[1])*9.81)
            msg.angular_velocity = Vector3(float(values[4].split(":")[1]), 
                float(values[5].split(":")[1]), 
                float(values[6].split(":")[1]))
            msg.header.stamp = rospy.Time.now()          # time when message received

            self.pubs[imu].publish(msg)
            rate.sleep()

if __name__ == '__main__':
    try:
        main_folder = '/home/aspen/Agroscope/Third_party/ROS_workspace_2/src/bmi088/src/'
        os.chdir(main_folder)
        
        IMU = ImuMessages()

        thread = subprocess.Popen('./BMI088_read',
            shell = False,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            bufsize=0)

        IMU.publish(200)
    except rospy.ROSInterruptException:
        thread.terminate()
        
        pass