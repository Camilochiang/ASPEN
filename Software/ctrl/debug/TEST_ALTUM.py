import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
channel_1 = 7

GPIO.setup(channel_1, GPIO.IN)

GPIO.wait_for_edge(channel_1, GPIO.RISING)
print('Edge detected')

GPIO.cleanup()