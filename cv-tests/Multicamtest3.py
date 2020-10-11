import RPi.GPIO as GPIO
import os
from picamera import PiCamera
import time
chan_listc=[12,16,18] #camera switcher pins
chan_listl=[29,31,33] #laser pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(chan_listc, GPIO.OUT)
GPIO.setup(chan_listl, GPIO.OUT)
i2c='i2cset -y 1 0x70 0x00 0x04'
os.system(i2c)
GPIO.output(chan_listc,(1,0,0))
GPIO.output(chan_listl,0)
camera=PiCamera()
camera.resolution=(640,480)
capnum=0

def camera1():
    GPIO.output(chan_listc,(1,0,0))
    i2c='i2cset -y 1 0x70 0x00 0x04'
    os.system(i2c)
    
def camera3():
    GPIO.output(chan_listc,(0,1,0))
    i2c='i2cset -y 1 0x70 0x00 0x06'
    os.system(i2c)    

def ccheck():
    camera._check_camera_open()
    
def cpreview():
    camera.start_preview(fullscreen=False,window=(200,80,600,400))
    print("camera active")
    
def cstop():
    camera.stop_preview()
    
def capture():
    global capnum
    camera.resolution=(3280,2464)
    starttime=time.time()
    camera.capture('capture%d.jpg'%capnum,'jpeg',use_video_port=True)
    capnum=capnum+1
    endtime=time.time()
    print("captured in %d seconds"%(endtime-starttime))
    
def laserc():
    GPIO.output(chan_listl,1)
    
def main():
    userin=""
    while userin != "end":
        userin=input("Command: ")
        if userin=='c1':
            camera1()
        if userin=='c3':
            camera3()
        if userin=='p':
            cpreview()
        if userin=='s':
            cstop()
        if userin=='cc':
            ccheck()
        if userin=='cap':
            capture()
        if userin=='l':
            laserc()
        if userin=='h':
            print ("c1 - select camera 1")
            print ("c3 - select camera 3")
            print ("cc - Camera check")
            print ("p - Preview")
            print ("s - Stop Preview")
            print ("l = laser (on or off)")
            print ("cap = capture")
    
    camera.close()
    GPIO.cleanup()

    
if __name__ == "__main__":
    main()