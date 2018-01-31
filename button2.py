import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)

GPIO.setup(05, GPIO.IN)#Button to GPIO05
#GPIO.setup(24, GPIO.OUT)  #LED to GPIO24
GPIO.setwarnings(False)

try:
    while True:
         button_state = GPIO.input(05)
         time.sleep(0.1)
         #if button_state == True:
             #GPIO.output(24, True)
         if button_state == True:
             #print('Button Pressed...')
             print('Button Not Pressed...')
             time.sleep(0.1)
             #print('Turning systemn off')
             time.sleep(1)
             #os.system('sudo poweroff')
         else:
             #GPIO.output(24, False)
             #print('Button Not Pressed...')
             print('Pressed...')
             time.sleep(0.1)
             print('Turning systemn off')
             os.system('sudo poweroff')

except:
    GPIO.cleanup()