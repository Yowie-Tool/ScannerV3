#!/usr/bin/python3

#Test program for Arducam multi camera adapter V2.2 with cameras attached to ports A and C
import RPi.GPIO as gp
import os
from picamera import PiCamera
import time
#from PyQt5 import QtCore,QtGui,QtWidgets
#from PyQt5 import uic
camera=PiCamera()
camera.resolution(3280,2464)
gp.setup(7,gp.OUT)
gp.setup(11,gp.OUT)
gp.setup(12,gp.OUT)
gp.setup(13,gp.OUT)

def main():
    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)
    capture(1)
    
    gp.output(7, False)
    gp.output(11, True)
    gp.output(12, False)
    capture(3)
    
def capture(cam):
    camera.start_preview()
    sleep(2)
    camera.capture('camera%d.jpg'%cam)

if __name__ == "__main__":
    main()