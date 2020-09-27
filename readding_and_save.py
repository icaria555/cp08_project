from random import randint
import os.path
import requests , httplib ,urllib ,time
from datetime import date
from datetime import timedelta


if ( __name__ == "__main__"):
    date_up = date.today()
    now = date.today()
    one = timedelta(days = 1)
    while(True):
        spo2 = randint(70, 100)
        h_rate = randint(40, 80)
        
        h_signal = str(randint(0, 100))
        for i in range(199):
            h_signal += "," + str(randint(0, 100))
        
        text_out = '{0}_{1}_{2}_{3}\n'.format(spo2, h_rate, h_signal, date_up.strftime("%d-%m-%Y"))
        print text_out
        date_up = date_up + one
        stat = ''
        stat2 = ''
        
        while(stat != "writting:complete" and stat2 != "readding:complete"):
            with open('Data/system_status', 'r') as f :
                text_stat = f.readline().split(" ")
                print "test", text_stat
                stat = text_stat[0]
                stat2 = text_stat[1]

        with open('Data/system_status', 'w') as f :
            f.write('writting:doing' + " " + text_stat[1] + " " + text_stat[2])
            
        with open('Data/output.txt', 'a') as f:
            f.write(text_out)
        with open('Data/inputgui', 'w') as f:
            f.write(text_out)
            
        with open('Data/system_status', 'w') as f:
            f.write('writting:complete' + " " + text_stat[1] + " " + text_stat[2])
        time.sleep(6)