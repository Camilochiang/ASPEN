import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
channel = 33

GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)

while True:
   GPIO.output(channel, GPIO.HIGH)   
   time.sleep(1)
   GPIO.output(channel, GPIO.LOW)
   time.sleep(1)

GPIO.cleanup()