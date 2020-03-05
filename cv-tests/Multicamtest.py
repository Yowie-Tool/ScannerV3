#!/usr/bin/python3

#Test program for Arducam multi camera adapter V2.2 with cameras attached to ports A and C
import RPi.GPIO as gp
import os
from picamera import PiCamera
from time import sleep
gp.setwarnings(False)
gp.setmode(gp.BOARD)
gp.setup(7,gp.OUT)
gp.setup(11,gp.OUT)
gp.setup(12,gp.OUT)
gp.setup(13,gp.OUT)

def camera1photo():
    i2c = "i2cset -y 1 0x70 0x00 0x04"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(3280,2464)
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    sleep(2)
    camera.capture('camera1.jpg')
    camera.stop_preview()
    camera.close()
    
def camera1preview():
    i2c = "i2cset -y 1 0x70 0x00 0x04"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(3280,2464)
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))

def cameraend():
    camera.stop_preview()
    camera.close()

def camera2photo():
    i2c = "i2cset -y 1 0x70 0x00 0x05"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(3280,2464)
    gp.output(7, True)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    sleep(2)
    camera.capture('camera2.jpg')
    camera.stop_preview()
    camera.close()
    
def camera2preview():
    i2c = "i2cset -y 1 0x70 0x00 0x05"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(3280,2464)
    gp.output(7, True)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))

def main():
   userin=""
   while userin != "end":
        userin=input("Command: ")
        if userin=='photo1':
            camera1photo()
        if userin=='1':
            camera1preview()
        if userin=='photo2':
            camera2photo()
        if userin=='2':
            camera2preview()
        if userin=='s':
            cameraend()
        if userin=='h':
            print ("photo1 - take photo with camera 1")
            print ("1 - start preview on camera 1")
            print ("photo2 - take photo with camera 2")
            print ("2 - start preview on camera 2")
            print ("s - stop preview (either camera)")

    
if __name__ == "__main__":
    main()