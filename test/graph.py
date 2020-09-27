
"""
A simple example of an animated plot
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import randint
import time
import spidev, time
import RPi.GPIO as GPIO
import sys
from scipy.signal import butter, lfilter, freqz, lfilter_zi
from scipy import signal as sig

red = 29
ired = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(red, GPIO.OUT)#set pin output red
GPIO.setup(ired, GPIO.OUT)#set pin output ired

#turn on led red or ired
#true = turn on red and turn off ired, false =   turn on ired and turn off red
def red_or_ired(boo):
    GPIO.output(29, boo)
    GPIO.output(38, not(boo))

def sum_avg(dat):
    avg = 0
    for i in dat:
        avg += i

        print avg, "test"
    return avg / len(dat)


aa = True
red_or_ired(True)
fig, ax = plt.subplots()
plt.ylim(0 , 4000)


x = np.arange(0, 3, 0.01)
y = [0 for i in range(len(x))]
line, = ax.plot(x, y)
line2, = ax.plot(x, y)
line3, = ax.plot(x, y, 'ko')
 
spi = spidev.SpiDev()
spo2 = randint(70, 100)
h_rate = randint(40, 80)
h_signal = str(randint(0, 100))

spi.open(0,0)
tt = True
count = 0
#recieve spi_data from adc converter return number 0 - 4096 
def analog_read(channel):
    raw = spi.xfer2([4 | 2 |(channel>>2), (channel &3) << 6,0]) #recive data from data sheet
    output = ((raw[1]&15) << 8) + raw[2] #r
    return output
def find_period(order, length, fs):
    timerate = length/fs
    time_avg = 0
    last_order = order[0]/fs
    for i in range(1, len(order)):
        now = order[i]/fs  - last_order
        time_avg += now
        last_order = order[i]/fs
    return time_avg/(len(order) - 1)

def write(file, txt):
    file.seek(0)
    file.write(txt)
    file.truncate()
    
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    print low , high , "test" , fs
    b, a = butter(order, high, btype='low', analog=False)
    zi = lfilter_zi(b, a)
    y_out, zo = lfilter(b, a, data, zi=zi*data[0])
    return y_out

def filter_signal(sig_data):
    highcut = 3
    lowcut = 0.7
    fs = 100.0
    order = 5
    raw_sig = sig_data
    filter_output = butter_bandpass_filter(raw_sig, lowcut, highcut, fs, order)
    return filter_output
    
def animate(*args):
    global tt, count
    global h_signal,y
    timestart = time.time()
    name = 'redandired0.txt'.format(count%2)
    signal = []
    #f_out = open(name, 'w')
    for i2 in range(300):
        try:
            
            voltage = float(analog_read(0))
            h_signal += "," + str(voltage)
            signal.append(voltage)

            time.sleep(0.01)
            
        except KeyboardInterrupt:
             sys.exit(0)
    
    #signal2 = [signal[i] for i in range(50 ,350)]
    #print len(signal2)
    #print i%2 == 0
    y4 = filter_signal(signal)
    tt = not(tt)
    red_or_ired(tt)
    #write(f_out, h_signal)
    #f_out.close()
    h_signal = ""
    fs = 100.0
    
    peak_max = [i for i in sig.argrelmax(y4)[0]]
    peak_min = [i for i in sig.argrelmin(y4)[0]]
    print [ y4[i] for i in peak_max], "peak max"
    print [ y4[i] for i in peak_min], "peak min"
    print 60.0 / find_period(peak_max, len(y4), fs) , "BPM"
    colors = [40 for i in range(len(peak_max))]

   
    
    max =  [y4[i] for i in sig.argrelmax(y4)[0]]

    min = [y4[i] for i in sig.argrelmin(y4)[0]]

    #print "max", sum(max)/len(max)
        
    #print "min", sum(min)/len(min)
    #print  sig.find_peaks_cwt(y4,np.arange(200, len(y4))),  "filter peak"
    #print  sig.find_peaks_cwt(signal,np.arange(1, len(signal))),  "raw peak"
    
    
    line.set_ydata(y4)  # update the data
    line2.set_ydata(signal)
    line3.set_data(peak_max, [ y4[i] for i in peak_max])
    #if(count == 1):
    #    sys.exit(0)
    count += 1
    #sys.exit(0)

   

    return line,line2,line3,

# Init only required for blitting to give a clean slate.
def init():
    line.set_ydata(np.ma.array(x, mask=True))
    line2.set_ydata(np.ma.array(x, mask=True))
    setzero = [0 for i in range(len(line3.get_xdata()))]
    line3.set_ydata(np.ma.array(setzero, mask=True))
    print "test"
    return line,line2,line3

ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
                              interval=0, blit=True)
plt.show()
