"""

Health Care Device sending process
by Rungroj Kulapan

"""
from random import randint
import os.path, time
import requests, http.client, urllib, time
import sys

headers = {"Content-type": "application/x-www-form-urlencoded",
              "Accept": "text/plain"}
id = ""
hardware_name = ""
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def sendData(data, head):
    #input   : string array : spo2, heart, heart_signal(array)
    #output  : httpstatus code
    #purpose : use for send data to webserver and make sure data recieve
    global id
    head.connect()
    spo2_data = data[0]
    h_rate = data[1]
    h_signal = data[2]
    checkDate = data[3]
    url = "/senddata"
    params = {':uid': id, ':spo2': spo2_data,':h_rate': h_rate, ':h_signal': h_signal,':check_date':checkDate}
    
    params = urllib.parse.urlencode(params)
    head.request("POST", url, params, headers)#send post request
    response = head.getresponse()#recieve response from web server
    httpstatus = response.status #get http status code
    massage = response.read()#show recieve massage
    head.close()#end connection
    return httpstatus, massage

def connectToServer(head):
    #input   : headder
    #purpose : use for send data to webserver and make sure data recieve
    global id, hardware_name
    head.connect()    
    url = "/owner"
    params = {':hardware_name': hardware_name, ':owner': id}    
    if(len(id) == 0 and len(hardware_name) == 0):
        params = {':hardware_name': 'none', ':owner': 'none'} 
    params = urllib.parse.urlencode(params)
    head.request("POST", url, params, headers)#send post request
    response = head.getresponse()#recieve response from web server
    httpstatus = response.status #get http status code
    massage = response.read().split("_")#show recieve massage
    
    if(len(massage) == 3 and httpstatus == 200):
        hardware_name, name, id = massage
        with open(os.path.join(__location__,'Data/hardware_and_username.txt'), 'w') as f :
            f.write(hardware_name + "_" + name + "_" + id)
        
    head.close()#end connection
    return httpstatus, massage
    
if __name__ == '__main__':
    host = 'cp08-web-icaria555.c9users.io' #web server url
    h = http.client.HTTPConnection(host) #create HTTP object
    status = ''
    raw_output = "" 
    try:
        with open(os.path.join(__location__,'Data/hardware_and_username.txt'), 'r') as f :
            raw = f.readline().split("_")
            while(len(raw) < 2):                
                raw = f.readline().split("_")
            hardware_name, name, id = raw
        httpstatus = connectToServer(h)[0]
        while(httpstatus != 200 or len(id) < 1):
            with open(os.path.join(__location__,"Data/system_status"), 'r') as f :                
                status = f.readline().split(" ")
                while(len(status) != 5 ):
                    status = f.readline().split(" ")
            with open(os.path.join(__location__,"Data/system_status"), 'w') as fstat :
                if len(id) < 1:
                    fstat.write(status[0] + " " + status[1] + " " + "network:noowner"
                                + " " + status[3] + " " + status[4])
                else:
                    fstat.write(status[0] + " " + status[1] + " " + "network:disconnect"
                                + " " + status[3] + " " + status[4])
                httpstatus = connectToServer(h)[0]
        with open(os.path.join(__location__,"Data/system_status"), 'r') as f :
            status = f.readline().split(" ")
            while(len(status) != 5 ):
                status = f.readline().split(" ")
        
        with open(os.path.join(__location__,"Data/system_status"), 'w') as fstat :
            fstat.write(status[0] + " " + status[1] + " " + "network:ok" + " "
                        + status[3] + " " + status[4])
        while(True):                
            with open(os.path.join(__location__,"Data/system_status"), 'r') as f :
                status = f.readline().split(" ")
                while(len(status) != 5 ):
                    status = f.readline().split(" ")
            if(status[0] == "writting:complete"):#check if other process try write Data file
                delete_start = 0
                line = ""
                httpstatus = connectToServer(h)[0]
                with open(os.path.join(__location__,"Data/system_status"), 'w') as fstat :#change system status for prevent other process write Data file
                    fstat.write(status[0] + " " + "readding:doing" + " " + status[2]
                                + " " + status[3] + " " + status[4])
                with open(os.path.join(__location__,'Data/output.txt'), 'r') as f_read:#read output.txt file
                    raw_output = f_read.read()
                    if(len(raw_output) > 0):#check if file have data
                        line = raw_output.splitlines(True)#split all file's line 
                        for i in range(len(line)):#send data to webserver 
                            raw_data = line[delete_start].split("_")
                            ishttponline, massage = sendData(raw_data, h)
                            if ishttponline == 200 and massage == 'success':#check if webserver recieve data
                                delete_start += 1 # add count for remove output.txt line
                                status[2] = "network:ok"
                            else:
                                status[2] = "network:disconnect"
                if(httpstatus == 200):
                    status[2] = "network:ok"
                else:
                    status[2] = "network:disconnect"
                with open(os.path.join(__location__,"Data/system_status"), 'w') as fstat :
                    #write system_status for prevent other file read or write Data file
                    fstat.write("writting:doing" + " " + "readding:complete" + " " + status[2]
                                + " " + status[3] + " " + status[4])
                with open(os.path.join(__location__,'Data/output.txt'), 'w') as f_write:
                    #delete sent line
                    if(len(raw_output) > 0):
                        if(len(line) > 1):
                            f_write.writelines(line[delete_start:])
                        else:
                            f_write.write("")
                with open(os.path.join(__location__,"Data/system_status"), 'w') as fstat :
                    #change system_status to make normal state
                    fstat.write("writting:complete" + " " + "readding:complete" + " " + status[2]
                                + " " + status[3] + " " + status[4])
            time.sleep(1)
    except KeyboardInterrupt:
        h.close()
        sys.exit(0)
