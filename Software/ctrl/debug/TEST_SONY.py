import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
channel_hotshoe = 15
channel_focus = 31 # Geen cable
channel_image = 32 # RED?
GPIO.setup(channel_hotshoe, GPIO.IN)
GPIO.setup(channel_focus, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(channel_image, GPIO.OUT, initial = GPIO.HIGH)

def callback_fn(channel):
   print('Edge detected') 

GPIO.add_event_detect(channel_hotshoe, GPIO.FALLING, callback=callback_fn)

# Take an image
# First we focus
GPIO.output(channel_focus, GPIO.LOW)
GPIO.output(channel_image, GPIO.LOW)
time.sleep(1)
GPIO.output(channel_focus, GPIO.HIGH)
GPIO.output(channel_image, GPIO.HIGH)
time.sleep(1)


GPIO.cleanup()
