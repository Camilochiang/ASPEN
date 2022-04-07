import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
channel_1 = 7
channel_2 = 15

GPIO.setup(channel_1, GPIO.IN)
GPIO.setup(channel_2, GPIO.OUT, initial=GPIO.LOW)

while True:
   GPIO.output(channel_2, GPIO.HIGH)
   print('channel_2 high')   
   print(GPIO.input(channel_1))
   time.sleep(1)

   GPIO.output(channel_2, GPIO.LOW)
   print('channel_2 low')   
   print(GPIO.input(channel_1))
   time.sleep(1)

GPIO.cleanup()