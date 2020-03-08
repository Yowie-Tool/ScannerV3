#!/usr/bin/python3

#Test program for Arducam multi camera adapter V2.2 with cameras attached to ports A and C
from gpiozero import LED
import os
from picamera import PiCamera
from time import sleep
cselect=LED(4)
cenable1=LED(17)
cenable2=LED(18)
laser=LED(20)
camera=PiCamera()


def camera1photo():
    i2c = "i2cset -y 1 0x70 0x00 0x04"
    os.system(i2c)
    cselect.off()
    cenable1.off()
    cenable2.on()
    camera.resolution=(3280,2464)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    sleep(2)
    camera.capture('camera1.jpg')
    camera.stop_preview()
    print("Photo Taken on Camera 1")

    
def camera1preview():
    i2c = "i2cset -y 1 0x70 0x00 0x04"
    os.system(i2c)
    cselect.off()
    cenable1.off()
    cenable2.on()
    camera.resolution=(640,480)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    os.system('read -sn 1 -p "Press any key to continue..."')
    camera.stop_preview()
    

def camera2photo():
    i2c = "i2cset -y 1 0x70 0x00 0x06"
    os.system(i2c)
    cselect.off()
    cenable1.on()
    cenable2.off()
    camera.resolution=(3280,2464)
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    sleep(2)
    camera.capture('camera2.jpg')
    camera.stop_preview()
    print("Photo Taken on Camera 2")
    
def camera2preview():
    i2c = "i2cset -y 1 0x70 0x00 0x06"
    os.system(i2c)
    camera.resolution=(640,480)
    cselect.off()
    cenable1.on()
    cenable2.off()
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    print("Camera A")
    os.system('read -sn 1 -p "Press any key to continue..."')
    camera.stop_preview()
    
def laseron():
    laser.on()
    print("Laser on")
    
def laseroff():
    laser.off()
    print("Laser off")


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
        if userin=='l1':
            laseron()
        if userin=='l0':
            laseroff()
        if userin=='h':
            print ("p1 - take photo with camera 1")
            print ("c1 - start preview on camera 1")
            print ("p2 - take photo with camera 2")
            print ("c2 - start preview on camera 2")
            print ('l1 - Turn laser on')
            print ('l0 - Turn Laser off')
    
    camera.close()

    
if __name__ == "__main__":
    main()