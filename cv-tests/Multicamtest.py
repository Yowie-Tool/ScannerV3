#!/usr/bin/python3

#Test program for Arducam multi camera adapter V2.2 with cameras attached to ports A and C
import RPi.GPIO as gp
import os
from picamera import PiCamera
import time
#from PyQt5 import QtCore,QtGui,QtWidgets
#from PyQt5 import uic
camera=PiCamera()
camera.resolution=(3280,2464)
gp.setwarnings(False)
gp.setmode(gp.BOARD)
gp.setup(7,gp.OUT)
gp.setup(11,gp.OUT)
gp.setup(12,gp.OUT)
gp.setup(13,gp.OUT)

def camera1photo():
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview()
    time.sleep(2)
    camera.capture('camera1.jpg')
    camera.stop_preview()
    
def camera1preview():
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview()

def cameraend():
    camera.stop_preview()

def camera2photo():
    gp.output(7, True)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview()
    time.sleep(2)
    camera.capture('camera2.jpg')
    camera.stop_preview()
    
def camera2preview():
    gp.output(7, True)
    gp.output(11, False)
    gp.output(12, True)
    camera.start_preview()

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