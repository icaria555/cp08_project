import RPi.GPIO as GPIO
import time

red = 29
ired = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(red, GPIO.OUT)#set pin output red
GPIO.setup(ired, GPIO.OUT)#set pin output ired

#turn on led red or ired
#true = turn on red and turn off ired, false =   turn on ired and turn off red
def red_or_ired(boolean):
    GPIO.output(red, boolean)
    GPIO.output(ired, not(boolean))

while (True):
    red_or_ired(True)
    time.sleep(1)
    red_or_ired(False)
    time.sleep(1)
