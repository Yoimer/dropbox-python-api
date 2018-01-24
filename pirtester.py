import RPi.GPIO as GPIO
import time
import os
import datetime

#get date and time in year-month-day-hour-minute-second format
now = datetime.datetime.now()

# assing path to the new taken picture
OSCOMMAND = 'raspistill -o '
PHOTOPATH = '/home/pi/Dropbox/camera-images/'
EXTENSION = '.jpg'

temp = now.strftime("%Y-%m-%d %H:%M:%S")

# replace spaces by a minus symbol
temp = temp.replace(' ', '-')

# replace colons by a minus simbol
temp = temp.replace(':', '-')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(3, GPIO.OUT)         #LED output pin
while True:
       i=GPIO.input(11)
       if i==0:                 #When output from motion sensor is LOW
             print "No intruders",i
             GPIO.output(3, 0)  #Turn OFF LED
             time.sleep(0.1)
       elif i==1:               #When output from motion sensor is HIGH
             print "Intruder detected",i
             GPIO.output(3, 1)  #Turn ON LED
             time.sleep(0.1)
             os.system(OSCOMMAND + PHOTOPATH + temp + EXTENSION)