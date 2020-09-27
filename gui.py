"""

Health Care Device GUI
by Rungroj Kulapan

"""
from pygame import *
import pygame
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import pylab
import http.client, sys, time, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def readHealthData():
    #use for read inputgui file
    #output : inputgui string data
    data = ""
    with open(os.path.join(__location__,'Data/inputgui'), 'r') as f:
        data = f.readline()
    #print(data
    return data

def show_fps(fps_num, last_fps):
    #use for show fps
    clock.tick()
    if(pygame.time.get_ticks() - last_fps > 1000 ):
        #print("FPS", clock.get_fps())
        last_fps = pygame.time.get_ticks()
        #print(last_fps)
    return last_fps

init()
matplotlib.use("Agg")
#create figure for graph
fig = pylab.figure(figsize=[8, 2], # Inches
                   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
                   frameon=False
                   )
ax = fig.gca() 
plt.axis('off')
ylim = 1500
ax.set_ylim([0,ylim])

#plt.autoscale(enable=True, axis='y', tight=True)
data_length = len(readHealthData().split("_")[2].split(","))
ax.set_xlim([0,data_length])
hsignal = [0 for i in range(data_length)]
line, = ax.plot(hsignal,'')#create line

#setup GUI Graphic
size = width,height = 800,480 #screen size ans space config
#api = display.set_mode(size, pygame.FULLSCREEN) #set fullscreen
api = display.set_mode(size) #set GUI size
caption = 'Healht Care'
pygame.display.set_caption(caption, 'Spine Runtime')#set title

#load resources for GUI
#image

back = image.load(os.path.join(__location__,'Picture/background.jpg')).convert()
back2 = image.load(os.path.join(__location__,'Picture/backgroud2.png')).convert_alpha()
connected = image.load(os.path.join(__location__,'Picture/connected.png')).convert_alpha()
disconnected = image.load(os.path.join(__location__,'Picture/disconnected.png')).convert_alpha()
exitbutton = image.load(os.path.join(__location__,'Picture/exit.png')).convert_alpha()
w, h = connected.get_size()
connected = pygame.transform.scale(connected, (int(w*0.18), int(h*0.18)))
disconnected = pygame.transform.scale(disconnected, (int(w*0.18), int(h*0.18)))
w, h = exitbutton.get_size()
exitbutton = pygame.transform.scale(exitbutton, (int(w*0.15), int(h*0.15)))
#font
font1 = pygame.font.Font(os.path.join(__location__,"Font/FFF_Tusj.ttf"), 100)
font2 = pygame.font.SysFont(os.path.join(__location__,"Font/KaushanScript-Regular.otf"), 40)
warring_font = pygame.font.Font(os.path.join(__location__,"Font/FFF_Tusj.ttf"), 20)
ipfont = pygame.font.Font(os.path.join(__location__,"Font/FFF_Tusj.ttf"), 15)

Running = True
sceen = 'main'
warring_massage = ""
status_text = ""
clock = pygame.time.Clock()
last_fps = 0
state_logic = 0
status_connect = ""
last_stataus_connect = ""
name = ""
while(Running):
    event.pump()
    
    events = pygame.event.get()
    for eve in events:
        if eve.type == QUIT:
            pygame.quit()
            sys.exit()
    with open(os.path.join(__location__,"Data/system_status"), 'r') as f :
            status_text = f.readline().split(" ")
            while(len(status_text) < 5 ):
                #print("test len status", status_text)
                status_text = f.readline().split(" ")
            #print(status_text)
    with open(os.path.join(__location__,"Data/hardware_and_username.txt"), 'r') as f :
        raw = f.readline().split("_")
        while(len(raw)!= 3):
            pass
        name = raw[1]
    m = list(mouse.get_pressed())
    mx,my = mouse.get_pos()
    px , py = 0,0    
    last_fps = show_fps(60, last_fps)
    f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    ip_address = f.read()
    
    
    if(sceen == 'main'):#on main menu
        
        api.blit(transform.scale(back,size),(0,0))#set background
        api.blit(back2,(0,270))#set background2 for graph
        if(status_text[2] == "network:ok"):
            api.blit(connected,(0,0))
        else:
            api.blit(disconnected,(0,0))        
        raw = readHealthData().split("_")#read inputgui file and split data to array
        spo2, h_rate, h_signal, timenow, warring_t, high = raw#saparate type data
        h_signal = [float(i) for i in h_signal.split(",")]
        label = ipfont.render(ip_address, 1, (255,216,0))
        api.blit(label, (0, 100))#add ip address
        label = ipfont.render(name, 1, (255,216,0))
        api.blit(label, (0, 80))#add ip address

        if(float(high) - ylim > 0):#change y limit graph if current value is too high or too less
            ylim = float(high) + 50
            ax.set_ylim([0,ylim])
        elif(float(high) - ylim < -100):
            ylim = float(high) + 50
            ax.set_ylim([0,ylim])
        if(spo2 != None):
            spo2 = str(int(float(spo2)))
            label = font1.render(spo2, 1, (255,216,0))#add spo2 value
            api.blit(label, (280-font1.get_linesize(), 150))
            h_rate = str(int(float(h_rate)))
            label = font1.render(h_rate, 1, (255,216,0))#add heart rate value
            api.blit(label, (630-font1.get_linesize(), 150))
            label = font2.render(timenow, 1, (42,146, 106))
            api.blit(label, (600, 10))#add updated time
        label = warring_font.render(warring_t, 1, (42,146, 106))
        api.blit(label, (100, 10))#add waring massage
            
        #draw Heart Sigal
        line.set_ydata(h_signal)
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        #convert canvas to surface object for paste in GUI
        raw_data = canvas.buffer_rgba()#change fig to buffer rgba(png)
        size_g = canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data, size_g, "RGBA")#buffer to surface
        api.blit(surf, (0,270))#add to GUI
        api.blit(exitbutton, (760, 0))
        #pylab.savefig('foo.png', transparent=True)
        state_logic = 1
        if((760 <= mx <= 800) and (0 <= my <= 50)):
            if(m[0]):
                pass
                #os.system("sudo shutdown now") 
    display.update()# update screen#time.sleep(0.01)