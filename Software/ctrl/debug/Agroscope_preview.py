#!/usr/bin/python3
import cv2
import rospy
import numpy as np
from sensor_msgs.msg import Image

def callback(data):
    cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Align Example', np.asanyarray(data.data))

def listener():
    rospy.init_node('listener', anonymous=False)

    rospy.Subscriber("camera/color/image_raw", Image, callback)

    rospy.spin()

if __name__ == '__main__':
    listener()