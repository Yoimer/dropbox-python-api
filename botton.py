import RPi.GPIO as GPIO
import time
import os

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
             print('Turning systemn off')
             time.sleep(2)
             os.system('sudo poweroff')
         else:
             GPIO.output(24, False)
             print('Button Not Pressed...')
             time.sleep(1)
except:
    GPIO.cleanup()