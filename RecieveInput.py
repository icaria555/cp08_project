"""

Health Care Device read spo2 sensor
by Rungroj Kulapan

"""
import signal_part
import numpy as np
from datetime import date
from datetime import timedelta
import sys, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

class ReceiveInput():
    #class for change spo2, heart rate, heart signal to text and save as file
    #and use for estimate which is really heart signal
    date_up = date(2016, 5, 1)
    one = timedelta(days = 1)
    today = date.today()
    
    def __init__(self):
        self.spo2 = '0'
        self.h_rate = '0'
        self.high = 0
        self.h_sig = ''
        
    def add_h_sig(self, h_sig):
        #change heart signal to text object
        text = str(h_sig[0])
        for i in range(1, len(h_sig)):
            text = text + "," + str(h_sig[i])
        self.h_sig = text
        return text
        
    def ratio_to_spo2(self, ratio):
        #change ratio to spo2
        spo2 = 0
        if(ratio <= 0.4):
            spo2 = 0
        elif(ratio > 0.4 and ratio <= 1.4):
            spo2 = 110.6 - (26*ratio)
        elif(ratio >1.4 and ratio <= 2.4):
            spo2 = 123.6 - (34*ratio)
        elif(ratio > 2.4 and ratio <= 3.4):
            spo2 = 136 - (40*ratio)
        elif(ratio > 3.4):
            spo2 = 0
        return spo2
        
    def calculate_spo2(self, red_value, ired_value):
        
        peak_red = red_value.peak_to_peak_heartsig()
        peak_ired = ired_value.peak_to_peak_heartsig()
        if( peak_ired == 0 or peak_red == 0 ): return 0
        #calculate Spo2
        self.high = peak_ired
        ratio = peak_red * 1.0 / peak_ired
        spo2 = self.ratio_to_spo2(ratio)
        if(spo2 < 0): return 0
        self.spo2 = spo2
        return spo2

    def alpha_calculate_spo2(self, red_value, ired_value):
        #altenative method for calculate spo2 use / instand -
        red_h_v = red_value[1]
        red_l_v = red_value[0]
        ired_h_v = ired_value[1]
        ired_l_v = ired_value[0]

        ratio = 0
        #calculate Spo2
        #red_all = float(sum(red_h_v)/len(red_h_v))/float(sum(red_l_v)/len(red_l_v))
        red_all = float(red_h_v[len(red_h_v) - 1]) / red_l_v[len(red_l_v) - 1]
        #ired_all = float(sum(ired_h_v)/len(ired_h_v))/float(sum(ired_l_v)/len(ired_l_v))
        ired_all = float(ired_h_v[len(ired_h_v) - 1]) / ired_l_v[len(ired_l_v) - 1]
        print "red" , red_all , "ired" , ired_all
        
        ratio = red_all / ired_all
        self.spo2 = self.ratio_to_spo2(ratio)
        return self.spo2

    def calculate_heartbeat(self, signal_period):
        if( signal_period <= 0 or signal_period >= 100): return 0
        bpm = 60.0 / signal_period
        print signal_period
        self.h_rate = str(bpm)
        return bpm

    def export(self):
        global __location__
        stat = ''
        stat2 = ''
        while(stat != "writting:complete" and stat2 != "readding:complete"):
            with open(os.path.join(__location__,'Data/system_status'), 'r') as f :
                text_stat = f.readline().split(" ")
                print stat != "writting:complete"
                print "test", text_stat
                if(len(text_stat) == 5):
                    stat = text_stat[0]
                    stat2 = text_stat[1]

        with open(os.path.join(__location__,'Data/system_status'), 'w') as f :
            f.write('writting:doing' + " " + text_stat[1] + " " + text_stat[2] + " " + text_stat[3] + " " + text_stat[4])
            
        ReceiveInput.date_up = ReceiveInput.date_up + ReceiveInput.one
        ReceiveInput.today = date.today()
        text_out = '{0}_{1}_{2}_{3}'.format(self.spo2, self.h_rate, self.h_sig, ReceiveInput.today.strftime("%d-%m-%Y"))
        warring = ""
        text_status_spo2 = 'spo2:ok'
        text_status_h_rate = 'h_rate:ok'
        if(self.spo2 < 90):
            warring = "Your Oxygen level is low, try again or see doctor"
            text_status_spo2 = 'spo2:notok'
        if(self.h_rate < 60 or self.h_rate > 120 ):
            warring = "Your Heart rate is abnormal, try again or see doctor"
            text_status_h_rate = 'h_rate:notok'
        if(ReceiveInput.date_up > ReceiveInput.today):
            ReceiveInput.date_up = ReceiveInput.today
        with open(os.path.join(__location__,'Data/output.txt'), 'a') as f:
            f.write(text_out + "\n")
        with open(os.path.join(__location__,'Data/inputgui'), 'w') as f:
            f.write(text_out + "_" + warring + "_" + str(self.high))
        with open(os.path.join(__location__,'Data/system_status'), 'w') as f:
            
            f.write('writting:complete' + " " + text_stat[1] + " " + text_stat[2] + " " + text_status_spo2 + " " + text_status_h_rate)
        

if ( __name__ == "__main__"):
    output = ReceiveInput()    
    fs = 100.0    # sample rate time/seconds
    T = 2.0         # seconds
    n = int(T * fs) # total number of samples
    red_sig = signal_part.Signal('red', fs, T)#create signal object for read red led signal
    ired_sig = signal_part.Signal('ired', fs, T)#create signal object for read ired led signal
    
    while(True):
        ired_sig.readInput()#read red led signal
        ired_sig.filter_signal()#filter signal
        red_sig.readInput()#read ired led signal
        red_sig.filter_signal()#filter signal

        red_sig.positive_offset()
        ired_sig.positive_offset()

        spo2 = output.calculate_spo2(red_sig, ired_sig)
        period = output.calculate_heartbeat(ired_sig.find_period())
        sig = output.add_h_sig(red_sig.sig_data)
        
        print "another spo2" , spo2 , period 
        if(period < 220 and period > 0 and spo2 > 0):#check if is heart signal
            output.export()
            print "export ", spo2, period
