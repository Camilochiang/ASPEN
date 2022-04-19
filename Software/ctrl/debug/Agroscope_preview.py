#!/usr/bin/python3
import cv2
import rospy
import numpy as np
from sensor_msgs.msg import Image

def callback(data):
    #data2 = np.fromstring(data.data, np.uint8)
    data2 = np.frombuffer(data.data, dtype=np.uint8).reshape(1080, 1920, -1)
    cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Align Example', data2)
    cv2.waitKey(0)

def listener():
    rospy.init_node('listener', anonymous=False)
    rospy.Subscriber("camera/color/image_raw", Image, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()