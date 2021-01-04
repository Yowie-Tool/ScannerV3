import RPi.GPIO as GPIO
import os
from picamera import PiCamera
import time
import cv2 as cv
import numpy as np
chan_listc=[12,16,18] #camera switcher pins
chan_listl=[29,31,33] #laser pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(chan_listc, GPIO.OUT)
GPIO.setup(chan_listl, GPIO.OUT)
i2c='i2cset -y 1 0x70 0x00 0x04'
try:
    os.system(i2c)
except:
    print("i2c switch failed")
os.system(i2c)
GPIO.output(chan_listc,(1,0,0))
GPIO.output(chan_listl,0)
camera=PiCamera()
camera.resolution=(640,480)
capnum=0


def camera1():
    i2c='i2cset -y 1 0x70 0x00 0x04'
    try:
        os.system(i2c)
    except:
        print("i2c switch failed")
    GPIO.output(chan_listc,(1,0,0))
    
def camera3():
    i2c='i2cset -y 1 0x70 0x00 0x06'
    try:
        os.system(i2c)
    except:
        print("i2c switch failed")
    GPIO.output(chan_listc,(0,1,0)) 

def ccheck():
    camera._check_camera_open()
    
def cpreview():
    camera.start_preview(fullscreen=False,window=(200,80,600,400))
    print("camera active")
    
def cstop():
    camera.stop_preview()
    
def capture():
    camera.resolution=(3280,2464)
    shutterspeed=1
    maxvalueinit=0
    GPIO.output(chan_listl,1)
    camera.exposure_mode='off'
    camera.iso=100
    while maxvalueinit<255:
        camera.shutter_speed=shutterspeed
        camera.capture('lcalib.jpeg',use_video_port=True)
        calib=cv.imread('lcalib.jpeg')
        calibb=calib[:,:,0]
        (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibb)
        maxvalueinit=maxVal
        shutterspeed=shutterspeed+1
        print("shutter speed %d" %(shutterspeed)) 
    camera.resolution=(3280,2464)
    starttime=time.time()
    GPIO.output(chan_listl,0)
    camera.capture('loff.jpeg',use_video_port=True)
    GPIO.output(chan_listl,1)
    camera.capture('lon.jpeg',use_video_port=True)
    GPIO.output(chan_listl,0)
    endtime=time.time()
    print("captured in %d seconds"%(endtime-starttime))
    starttime=time.time()
    loff=cv.imread('loff.jpeg')
    lon=cv.imread('lon.jpeg')
    src=cv.subtract(lon,loff)
    blue=src[:,:,0]
    threshamount = input("Enter threshold amount 1-255: ")
    threshamount = int(threshamount)
    retval, threshold_ar = cv.threshold(blue, threshamount, 255, cv.THRESH_TOZERO);
    maxvalue = np.argmax(threshold_ar,axis=1)
    row, col = threshold_ar.shape
    text_file=open("output.txt","wt")
    for i in range(row):
        if maxvalue[i] != 0:
            for i2 in range(col):
                text_file.write(str(threshold_ar[i,i2]) + ",")
            text_file.write("\n")
    text_file.close()
    endtime=time.time()
    print("images read and saved %d seconds"%(endtime-starttime))
    
    
def laserc():
    GPIO.output(chan_listl,1)
    
def laseroff():
    GPIO.output(chan_listl,0)
    
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
        if userin=='l1':
            laserc()
        if userin =='l0':
            laseroff()
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