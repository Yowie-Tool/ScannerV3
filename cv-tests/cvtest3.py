#!/usr/bin/python3
import cv2 as cv
import numpy as np
from nanpy import (ArduinoApi, SerialManager)
import time
from picamera import PiCamera
import math
from statistics import mean
camangle = (62.2/(180/math.pi))
camangled=(28.9/(180/math.pi))
Bconst = (58.9/(180/math.pi))
cosB = math.cos(Bconst)
aconst = (1920*(math.sin(Bconst)))/(math.sin(camangle))
aconstsqrd = math.pow(aconst,2)
camera=PiCamera()
camera.resolution=(1920,1442)
camera.meter_mode='backlit'
#camera.saturation=50
camera.shutter_speed=4000
lsrctrl = 32
connection = SerialManager(device='/dev/ttyACM0')
a = ArduinoApi(connection=connection)
a.pinMode(lsrctrl, a.OUTPUT)
a.digitalWrite(lsrctrl, a.HIGH)
camera.start_preview(fullscreen=False,window=(100,20,640,480))
time.sleep(2)
camera.capture('/home/pi/Pictures/lon.jpg','jpeg',use_video_port=True)
a.digitalWrite(lsrctrl, a.LOW)
camera.capture('/home/pi/Pictures/loff.jpg','jpeg',use_video_port=True)
camera.close()
img1=cv.imread('/home/pi/Pictures/lon.jpg')
img2=cv.imread('/home/pi/Pictures/loff.jpg')
src=cv.subtract(img1,img2)
red=src[:,:,2]
ysize=red.shape[0]
xsize=red.shape[1]
#bluram=input('Blur amount, must be odd: ')
bluram=5
radius=int(bluram)
#threshinput=input('threshold: ')
threshinput=0.2
threshinput=float(threshinput)
blur=cv.GaussianBlur(red,(radius,radius),0)
(minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur)
threshamount = maxVal*threshinput
threshamount=int(threshamount)
print('Red Threshold value: %d' %threshamount)
retval, threshold = cv.threshold(red, threshamount, 255, cv.THRESH_TOZERO);
retval, invthresh=cv.threshold(threshold,2,255,cv.THRESH_BINARY)
maxvalue=np.argmax(threshold,axis=1)
standdev=np.std(threshold,axis=1)

yint=0
numrecold=0
while yint < ysize:
    xcolumn=maxvalue[yint]
    pxminus=threshold[yint,((maxvalue[yint])-1)]
    if yint > 0:
        pyminus=threshold[(yint-1),(maxvalue[yint])]
    else:
        pyminus=threshold[yint,(maxvalue[yint])]
    if yint == (ysize-1):
        pyplus=threshold[yint,(maxvalue[yint])]
    else:
        pyplus=threshold[(yint+1),(maxvalue[yint])]
    if xcolumn < (xsize-1):
        pxadd=threshold[yint,((maxvalue[yint])+1)]
    else:
        pxadd=threshold[yint,((maxvalue[yint]))] 
    if xcolumn > 0 and pxminus !=0 and pxadd !=0 and pyplus!=0 and pyminus !=0:
        maxvalueis=red[yint,xcolumn]
        print ('OK Row: %d column %d Value %d sd %f SDCALC %f' %(yint,xcolumn,maxvalueis,standdev[yint],(maxvalueis/standdev[yint])))
        yint=yint+1
        numrecold=numrecold+1
    else:
        yint=yint+1

yint=0
numrecnew=0
while yint < ysize:
    xcolumn=maxvalue[yint]
    maxvalueis=red[yint,xcolumn]
    checksd=maxvalueis/standdev[yint]
    if checksd<25:
        print ('OK Row: %d column %d Value %d sd %f SDCALC %f' %(yint,xcolumn,maxvalueis,standdev[yint],(maxvalueis/standdev[yint])))
        yint=yint+1
        numrecnew=numrecnew+1
    else:
        yint=yint+1

yint=0

print ('Recorded with threshold, old method %d' %(numrecold))
print ('Recorded with threshold, new method %d' %(numrecnew))
    

    
    
