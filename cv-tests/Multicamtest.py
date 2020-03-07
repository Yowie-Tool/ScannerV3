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
    print("Photo Taken on Camera 1")

    
def camera1preview():
    i2c = "i2cset -y 1 0x70 0x00 0x04"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(640,480)
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    os.system('read -sn 1 -p "Press any key to continue..."')
    camera.stop_preview()
    camera.close()
    

def camera2photo():
    i2c = "i2cset -y 1 0x70 0x00 0x06"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(3280,2464)
    gp.output(7, False)
    gp.output(11, True)
    gp.output(12, False)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    sleep(2)
    camera.capture('camera2.jpg')
    camera.stop_preview()
    print("Photo Taken on Camera 1")
    camera.close()
    
def camera2preview():
    i2c = "i2cset -y 1 0x70 0x00 0x06"
    os.system(i2c)
    camera=PiCamera()
    camera.resolution=(640,480)
    gp.output(7, False)
    gp.output(11, True)
    gp.output(12, False)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    print("Camera A")
    os.system('read -sn 1 -p "Press any key to continue..."')
    camera.stop_preview()
    camera.close()
    

def main():
    userin=""
    while userin != "end":
        userin=input("Command: ")
        if userin=='p1':
            camera1photo()
        if userin=='c1':
            camera1preview()
        if userin=='p2':
            camera2photo()
        if userin=='c2':
            camera2preview()
        if userin=='s':
            cameraend()
        if userin=='h':
            print ("photo1 - take photo with camera 1")
            print ("c1 - start preview on camera 1")
            print ("photo2 - take photo with camera 2")
            print ("c2 - start preview on camera 2")
    
    camera.close()

    
if __name__ == "__main__":
    main()