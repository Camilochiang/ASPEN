#!/usr/bin/python3
import cv2
import numpy as np
import rospy
import os 
import sys

os.chdir("/home/ubuntu/Agroscope/ASPEN/Software/Images")

def listener():
    image = cv2.imread('Wallpaper_xavier.png')
    cv2.imshow('image',image)
    #while cv2.getWindowProperty('image', 0) >= 0:
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print('out')
    sys.exit()

if __name__ == '__main__':
    listener()