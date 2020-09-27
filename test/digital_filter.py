#!/usr/bin/env python
import requests , httplib ,urllib ,time
#!/usr/bin/env python
from random import randint
host = 'cp08-web-icaria555.c9users.io'
url = "/test"
h1 = httplib.HTTPConnection(host)
def sendData(data):
    
    
    spo2_data = data[0]
    h_rate = data[1]
    h_signal = data[2]
    print data
    id = "icaria"
    params = {':uid': id, ':spo2': spo2_data,':h_rate': h_rate, ':h_signal':h_signal}
    
    params = urllib.urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded",
              "Accept": "text/plain"}    
    h1.request("POST", url, params, headers)
    h1.close
    

#r = requests.get('https://cp08-web-icaria555.c9users.io', verify=Fal)
h1 = httplib.HTTPConnection('cp08-web-icaria555.c9users.io')

spo2_data = str(randint(90,99))
h_rate = str(randint(70,80))
id = "icaria"
h_signal = str(randint(0, 100))
for i in range(99):
    h_signal += "," + str(randint(0, 100))


sendData([spo2_data, h_rate, h_signal])