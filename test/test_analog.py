
import RPi.GPIO as GPIO
import time
import spidev, time

red = 29
ired = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(red, GPIO.OUT)#set pin output red
GPIO.setup(ired, GPIO.OUT)#set pin output ired
spi = spidev.SpiDev()
spi.open(0,0)
#turn on led red or ired
#true = turn on red and turn off ired, false =   turn on ired and turn off red
def red_or_ired(boolean):
    GPIO.output(red, boolean)
    GPIO.output(ired, not(boolean))
    
def analog_read(channel):
    raw = spi.xfer2([4 | 2 |(channel>>2), (channel &3) << 6,0]) #recive data from data sheet
    output = ((raw[1]&15) << 8) + raw[2] #r
    return output
text = ""
text2 = ""
i = 0
sample = 200
timestart = time.time()
timestart2 = time.time()

red_or_ired(False)

file = open("dat_ired.txt", "w")

for i in range(3000):
    reading = analog_read(0)
    #text += "reading = %d \t voltage = %f V \n" % (reading ,voltage)
    print reading

    time.sleep(0.01)
    i+= 1




    
