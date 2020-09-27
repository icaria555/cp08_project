import numpy as np
import matplotlib.pyplot as plt
import spidev, time
import RPi.GPIO as GPIO
from scipy import signal
from scipy.signal import butter, lfilter, lfilter_zi, freqz

red = 29
ired = 31

def setup_rasp():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(red, GPIO.OUT)#set pin output red
    GPIO.setup(ired, GPIO.OUT)#set pin output ired
    
def red_or_ired(boo):
    GPIO.output(red, boo)
    GPIO.output(ired, not(boo))

spi = spidev.SpiDev()
spi.open(0,0)
setup_rasp()

def analog_read(channel):
    #recieve spi_data from adc converter return number 0 - 4096
    raw = spi.xfer2([4 | 2 |(channel>>2), (channel &3) << 6,0]) #recive data from data sheet
    output = ((raw[1]&15) << 8) + raw[2] 
    return output
    
class Signal:
    #this class use for manage signal data by filter , find peak , find period
    #input led_state : "red , "ired" ;for control spo2 probe led
    #          fs            : sample_rate(int)
    #          t              : time
    def __init__(self, led_state, fs, t):
        self.sig_data = []            #signal data  that receive from ADC
        self.sig_data2 = []          #same as sig_data but add extend data for filter part
        self.period = 0
        self.h_amp = 0
        self.l_amp = 0
        self.fs = fs
        self.t = t
        self.led_light = led_state
    
    def readInput(self):
        channel = 0
        sig_data = []
        sig_data2 = []
        if self.led_light == 'red':
            red_or_ired(True)
        else:
            red_or_ired(False)
        time.sleep(0.5)
        for i in range(int(self.fs * self.t) + int(self.fs*0.5)):
            sig_data2.append(analog_read(channel))
            time.sleep(1.0/self.fs)
        self.sig_data2 = sig_data2
        for i in range(int(self.fs * self.t) ):
            sig_data.append(sig_data2[i])        
        self.sig_data = sig_data
        return sig_data
    
    def high_amp_point(self):
        sig_data =  self.sig_data
        peak_max = [i for i in signal.argrelmax(np.array(sig_data))[0]]
        return peak_max

    def high_amp(self):
        point = self.high_amp_point()
        high = [self.sig_data[i] for i in point]
        self.h_amp = sum(high)*1.0/len(high)
        return high
    
    def low_amp_point(self):
        sig_data =  self.sig_data
        peak_min = [i for i in signal.argrelmin(np.array(sig_data))[0]]
        return peak_min

    def low_amp(self):
        point = self.low_amp_point()
        low = [self.sig_data[i] for i in point]
        self.l_amp = sum(low)*1.0/len(low)
        return low

    def peak_to_peak(self):
        high_peak = self.high_amp()
        low_peak = self.low_amp()
        peak_value = []
        if(len(high_peak) > len(low_peak)):
            for i in range(len(low_peak)):
                current_peak = high_peak[i] - low_peak[i]
                peak_value.append( current_peak )
                #print "{:.3} peak value".format(current_peak)
        else:
            for i in range(len(high_peak)):
                current_peak = high_peak[i] - low_peak[i]
                peak_value.append( current_peak )
                #print "{:.3} peak value".format(current_peak)
        return sum(peak_value)*1.0 / len(peak_value)

    def peak_to_peak_heartsig(self):
        #this method use for find heart signal 's peak data
        #output is avg high ,low peak data
        #process of this method view wipe noise by check peak data
        high_peak = self.high_amp()
        low_peak = self.low_amp()
        peak_value = []
        if(len(high_peak) > len(low_peak)):
            for i in range(len(low_peak)):
                current_peak = high_peak[i] - low_peak[i]
                if(current_peak < 50): return 0
                peak_value.append( current_peak )
                #print "{:.3} peak value".format(current_peak)
        else:
            for i in range(len(high_peak)):
                current_peak = high_peak[i] - low_peak[i]
                if(current_peak < 50): return 0
                peak_value.append( current_peak )
                #print "{:.3} peak value".format(current_peak)
        return sum(peak_value)*1.0 / len(peak_value)

    def add_offset(self, offset):
        self.sig_data = self.sig_data + offset
        return self.sig_data

    def positive_offset(self):
        sig_data = self.sig_data
        offset = min(self.low_amp()) * -1
        sig_data = offset+ sig_data
        self.sig_data = sig_data
        return sig_data
    
    def find_period(self):
        highamp_sample = self.high_amp_point()
        time_h_avg = 0
        last_highamp_sample = highamp_sample[0]/self.fs

        lowamp_sample = self.low_amp_point()
        time_l_avg = 0
        last_lowamp_sample = lowamp_sample[0]/self.fs
        
        for i in range(1, len(highamp_sample)):
            now = highamp_sample[i]/self.fs
            time_h_avg += now - last_highamp_sample
            last_highamp_sample = now

        for i in range(1, len(lowamp_sample)):
            now = lowamp_sample[i]/self.fs 
            time_l_avg += now  - last_lowamp_sample
            last_highamp_sample = now
            
        time_h_avg = time_h_avg/(len(highamp_sample) - 1)
        time_l_avg = time_l_avg/(len(lowamp_sample) - 1)
        self.period = (time_h_avg + time_l_avg) / 2.0
        return self.period

    def find_period_heartsig(self):
        highamp_sample = self.high_amp_point()
        time_h_avg = 0
        last_highamp_sample = highamp_sample[0]/self.fs

        lowamp_sample = self.low_amp_point()
        time_l_avg = 0
        last_lowamp_sample = lowamp_sample[0]/self.fs
        
        for i in range(1, len(highamp_sample)):
            now = highamp_sample[i]/self.fs
            period_time = now - last_highamp_sample
            #print 60/period_time , "period time"
            if(period_time <= 0.3 or  period_time > 3) :
                return 100
            time_h_avg += period_time
            last_highamp_sample = now

        for i in range(1, len(lowamp_sample)):
            now = lowamp_sample[i]/self.fs
            period_time = now  - last_lowamp_sample
            #print 60/period_time , "period time low"
            if(period_time <= 0.3 or  period_time > 3) :
                return 100
            time_l_avg += period_time
            last_highamp_sample = now
            
        time_h_avg = time_h_avg/(len(highamp_sample) - 1)
        self.period = time_h_avg 
        return self.period

    def butter_lowpass_filter(self, highcut, order=5):
        shift_time = int(self.fs*0.5)
        nyq = 0.5 * self.fs
        high = highcut / nyq
        b, a = butter(order, high, btype='low', analog=False)
        zi = lfilter_zi(b, a)
        y_out, zo = lfilter(b, a, self.sig_data2, zi=zi*self.sig_data[0])
        y2 = []
        for i in range(shift_time , int(self.fs * self.t) + shift_time):
            y2.append(y_out[i])      
        return y2
    
    def butter_bandpass_filter(self, lowcut, highcut, order=5):
        shift_time = int(self.fs*0.5)
        nyq = 0.5 * self.fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band', analog=False)
        zi = lfilter_zi(b, a)
        y_out, zo = lfilter(b, a, self.sig_data2, zi=zi*self.sig_data[0])
        y2 = []
        for i in range(shift_time , int(self.fs * self.t) + shift_time):
            y2.append(y_out[i])      
        return y2

    def filter_signal(self):
        #this method use for filter analog signal data
        # output : filted analog signal data
        highcut = 3.7
        lowcut = 0.7
        order = 4
        #filter_output = self.butter_lowpass_filter(highcut, order) # lowpass filter
        filter_output = self.butter_bandpass_filter(lowcut, highcut, order) # bandpass filter
        self.sig_data = filter_output
        return filter_output
        
if ( __name__ == "__main__"):
    fs = 100.0    # sample rate time/seconds
    T = 2.0         # seconds
    n = int(T * fs) # total number of samples
    t = np.linspace(0, T, n, endpoint=False)
    red_sig = Signal('red', fs, T)
    ired_sig = Signal('ired', fs, T)
    y = red_sig.readInput()
    y = [ 0 for i in y]

    plt.ion()
    fig = plt.figure()
    plt.ylim(0 , 4000)
    ax = fig.add_subplot(111)
    line1, = ax.plot(t, y, 'b-') 
    line2, = ax.plot(t, y, 'r-') 
    line3, = ax.plot(t, y, 'ko')
    line4, = ax.plot(t, y, 'g-')
    line5, = ax.plot(t, y, 'm-')
    
    while(True):
        #line5.set_ydata(ired_sig.readInput())
        ired_sig.readInput()
        ired_sig.filter_signal()
        line4.set_ydata(ired_sig.positive_offset())
        #ired_sig.positive_offset()
        #line2.set_ydata(red_sig.readInput())
        red_sig.readInput()
        red_sig.filter_signal()
        line1.set_ydata(red_sig.positive_offset())
        #red_sig.positive_offset()
        
        red_h = red_sig.high_amp_point()
        red_l = red_sig.low_amp_point()
        ired_h = ired_sig.high_amp_point()
        ired_l = ired_sig.low_amp_point()

        red_h_v = []
        red_l_v = []
        ired_h_v = []
        ired_l_v = []

        for i in  red_h:
            y[i] = red_sig.sig_data[i]
            red_h_v.append(y[i])
        for i in  red_l:
            y[i] = red_sig.sig_data[i]
            red_l_v.append(y[i])
        for i in  ired_h:
            y[i] = ired_sig.sig_data[i]
            ired_h_v.append(y[i])
        for i in  ired_l:
            y[i] =ired_sig.sig_data[i]
            ired_l_v.append(y[i])

        #print len(ired_h_v) , "length ired high amp"
        peak_red = red_sig.peak_to_peak_heartsig()
        peak_ired = ired_sig.peak_to_peak_heartsig()
        if(peak_ired == 0 ):
            ratio = 1000
        else:
            ratio = peak_red * 1.0 / peak_ired
        Spo2 = 110 - (25*ratio)
        if(ratio <0.4):
            Spo2 = 0
        ired_period =  ired_sig.find_period_heartsig() 
        print Spo2 , ratio
        print 60 / ired_period, "period"  ,ired_period
        
        line3.set_ydata(y)
        fig.canvas.draw()
        #while(red_sig.h_l_amp() == 0, 0):
        #    red_sig.readInput()
        #    print "test"
        y = [ 0 for i in y]
