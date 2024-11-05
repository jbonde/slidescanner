from guizero import App, Text, PushButton, Window, Box
import serial
from time import sleep
import platform

VER=17 # current version

# Serial com
OSplatform=(platform.system())
try:
    if OSplatform=="Linux": # Assuming RPi as hardware
        port = "/dev/ttyUSB0"  # USB serial for RPi
    else:
        port = "COM3"
    ser = serial.Serial(port, baudrate = 9600)
    print (ser.name)
except:
    print("serial problem")
# MODE
mode="default"
shootingtimer=0

#BUTTON properties
scan_button_width=5
scan_button_height=2

#BOX properties
scan_box_width=170
scan_box_height=80
scan_box_text_small=20
scan_box_text_large=33
scan_box_border=1

# SLIDE properties
slideamount=0
slideremain=0
slidecurrent=0

def timer_update():
    global shootingtimer,slideamount,slideremain
    shootingtimer+=1
    if mode=="default":
        scan_button_reset.text="RESET"
        scan_button_reset.text_color="white"
        scan_button_reset.bg="green"
        scan_button_scan.text="SCAN"
        scan_button_scan.text_color="white"
        scan_button_scan.bg="magenta"
        scan_button_shoot.bg="blue"
        scan_button_shoot.text_color="white"
        scan_button_quit.bg="orange"
        scan_button_quit.text_color="white"
        scan_button_break.bg="grey"
        scan_button_break.text_color="white"
        scan_button_coffee.bg="brown"
        scan_button_coffee.text_color="white"
    if mode=="scan":
        scan()
    if mode=="reset":
        resetting()    
    if mode=="coffee":
        scan_button_reset.bg="brown"
        scan_button_scan.bg="brown"
        scan_button_shoot.bg="brown"
        scan_button_quit.bg="brown"
        scan_button_coffee.bg="brown"
        scan_button_break.bg="brown"
        slideamount=0
        slideremain=0
    if shootingtimer==20:
        shootingtimer=0        
    displayupdate()

def modeset(mood): # setting mode for the timer()
    global mode,shootingtimer
    #if mood=="scan":
    shootingtimer=0
    mode=mood

def serialsend(sermessage):
    ser.write(sermessage)
    sleep(0.2)
    ser.write(b'\x43\x00') # switch off relays

def initialize():
    try:
        serialsend(b'\x42\x00') # Relay Initialise: set the lower four channels as outputs and the upper four as inputs:
        sleep(0.2)
        serialsend(b'\x43\x01') # relay #1 (Camera Initialise)
        print("Camera initialized")
    except:
        print("Initialization failed")

def displayupdate():
    scan_box_total_text_value.value=str(slideamount)
    scan_box_remain_text_value.value=str(slideremain)
    scan_box_current_text_value.value=str(slidecurrent)

def slides(amount):
    global slideamount,slideremain
    slideamount+=int(amount)
    if slideamount>80:
        slideamount=0
    if slideamount<0:
        slideamount=80        
    slideremain=slideamount
    #displayupdate()

def scan():
    global slideremain,mode,shootingtimer
    print("scanning slides: " + str(slideamount))
    scan_button_scan.text="Scanning"
    scan_button_scan.bg="red"
    if shootingtimer==10:
        forward()
    if shootingtimer==20:
        shoot()
        slideremain-=1
    if slideremain==0:
        shootingtimer=0
        mode="reset"

def forward():
    global slidecurrent
    serialsend(b'\x43\x04') # relay #3 (Projector Forward)
    slidecurrent+=1
    if slidecurrent>80:
        slidecurrent=0
    print("Forward")
    
def reverse():
    global slidecurrent
    serialsend(b'\x43\x08') # relay #4 (Projector Reverse)
    slidecurrent-=1
    if slidecurrent<0:
        slidecurrent=80
    print("Reverse")

def shoot():
    #scan_button_shoot.bg="red"
    serialsend(b'\x43\x03') # relay 1+2 for camera exposure
    print("Shoot")

def resetting():
    global slideamount,slideremain,slidecurrent,mode,shootingtimer
    scan_button_reset.bg="red"
    scan_button_reset.text="resetting"
    if shootingtimer==10:
        if slidecurrent>40:
            forward()
        else:
            reverse()
        shootingtimer=0
    if slidecurrent==0:
        slideremain=slideamount
        mode="default"

def breaking():
    global mode
    mode="default"

def quitting():
    try:
        GPIO.cleanup()
    except:
        print("GPIO cleanup not possible")
    try:
        app.destroy()
    except:
        print("Will not hide system")

# App initialization
app = App(title="Slidescan control panel", layout="grid")

# Set fullscreen and remove topmost attribute after initialization
app.tk.attributes("-fullscreen", True)
screen_width = app.tk.winfo_screenwidth()
screen_height = app.tk.winfo_screenheight()
app.tk.geometry(f"{screen_width}x{screen_height}+0+0")
print(screen_width)
print(screen_height)
app.text_size=36

x=0
y=0
scan_box_current = Box(app, width=scan_box_width, height=scan_box_height, grid=[x,y])
scan_box_current_text_title = Text(scan_box_current, text="CURRENT", align="top", size=scan_box_text_small)
scan_box_current_text_value = Text(scan_box_current, text="amount", align="top", size=scan_box_text_large)
scan_box_current.set_border(scan_box_border,"black")
x+=1
scan_box_total = Box(app, width=scan_box_width, height=scan_box_height, grid=[x,y])
scan_box_total_text_title = Text(scan_box_total, text="TOTAL", align="top", size=scan_box_text_small)
scan_box_total_text_value = Text(scan_box_total, text="amount", align="top", size=scan_box_text_large)
scan_box_total.set_border(scan_box_border,"black")
x+=1
scan_box_remain = Box(app, width=scan_box_width, height=scan_box_height, grid=[x,y])
scan_box_remain_text_title = Text(scan_box_remain, text="REMAIN", align="top", size=scan_box_text_small)
scan_box_remain_text_value = Text(scan_box_remain, text="amount", align="top", size=scan_box_text_large)
scan_box_remain.set_border(scan_box_border,"black")
x+=1
#scan_button_stop = PushButton(app, text="STOP", width=scan_button_width, height=scan_button_height, grid=[x,y])
scan_box_version = Box(app, width=scan_box_width, height=scan_box_height, grid=[x,y])
scan_box_version_text_title = Text(scan_box_version, text="VERSION", align="top", size=scan_box_text_small)
scan_box_version_text_value = Text(scan_box_version, text=str(VER), align="top", size=scan_box_text_large)
scan_box_version.set_border(scan_box_border,"black")

x=0
y=1
scan_button_minus10 = PushButton(app, lambda:slides("-10"), text="-10", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_minus1 = PushButton(app, lambda:slides("-1"), text="-1", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_plus1 = PushButton(app, lambda:slides("1"), text="+1", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_plus10 = PushButton(app, lambda:slides("10"), text="+10", width=scan_button_width, height=scan_button_height, grid=[x,y])

x=0
y=2
scan_button_shoot=PushButton(app, command=shoot, text="SHOOT", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_reverse=PushButton(app, command=reverse, text="<", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_forward=PushButton(app, command=forward, text=">", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_scan = PushButton(app, lambda:modeset("scan"), text="SCAN", width=scan_button_width, height=scan_button_height, grid=[x,y])

x=0
y=3
scan_button_coffee = PushButton(app, lambda:modeset("coffee"), text="COFFEE", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_break = PushButton(app, command=breaking, text="BREAK", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_reset = PushButton(app, lambda:modeset("reset"), text="RESET", width=scan_button_width, height=scan_button_height, grid=[x,y])
x+=1
scan_button_quit = PushButton(app, command=quitting, text="QUIT", width=scan_button_width, height=scan_button_height, grid=[x,y])
scan_button_quit.disable()

initialize()
app.repeat(100, timer_update)
app.display()

# RELAY board
# https://www.easydaq.co.uk/
# PT No.100/DA/2007/003
# USB4SRMx RLY ISS A
# https://www.easydaq.co.uk/datasheets/Data%20Sheet%2051%20(USB4SRMxN%204%20relays%20(30VDC@1A)%20+%204%20DIO%20chan%20card).pdf
# 3.5" TFT display
# installing PITFT https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install-2 
#

'''
# Autostart
mkdir /home/pi/.config/autostart
nano /home/pi/.config/autostart/scan.desktop

[Desktop Entry]
Type=Application
Name=Scan
Exec=/usr/bin/python3 /home/pi/slidescan.py
'''
