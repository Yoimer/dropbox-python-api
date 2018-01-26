import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(05, GPIO.IN)#Button to GPIO05
GPIO.setup(24, GPIO.OUT)  #LED to GPIO24

try:
    while True:
         button_state = GPIO.input(05)
         if button_state == True:
             GPIO.output(24, True)
             print('Button Pressed...')
             time.sleep(1)
         else:
             GPIO.output(24, False)
             print('Button Not Pressed...')
             time.sleep(1)
except:
    GPIO.cleanup()