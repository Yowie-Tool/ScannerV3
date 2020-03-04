import cv2 as cv
import numpy as np
#from nanpy import (ArduinoApi, SerialManager)
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
camera.saturation=50
camera.shutter_speed=4000
lsrctrl = 32
#connection = SerialManager(device='/dev/ttyACM0')
#a = ArduinoApi(connection=connection)
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
threshinput=input('threshold: ')
#threshinput=0.5
threshinput=float(threshinput)
blur=cv.GaussianBlur(red,(radius,radius),0)
(minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur)
threshamount = maxVal*threshinput
threshamount=int(threshamount)
print('Red Threshold value: %d' %threshamount)
retval, threshold = cv.threshold(red, threshamount, 255, cv.THRESH_TOZERO);
retval, invthresh=cv.threshold(threshold,2,255,cv.THRESH_BINARY)
cv.imshow('Binary',invthresh)
cv.waitKey(0)
cv.destroyAllWindows()
maxvalue=np.argmax(threshold,axis=1)
standdev=np.std(threshold,axis=1)
yint=0
numrec=0
xvalues=[]
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
        redp=img2[yint,xcolumn,2]
        greenp=img2[yint,xcolumn,1]
        bluep=img2[yint,xcolumn,0]
        cosC=((2*aconstsqrd)-(2*aconst*xcolumn*cosB))/((2*aconst*(math.sqrt((aconstsqrd+(xcolumn*xcolumn)-(2*aconst*xcolumn*cosB))))))
        angle=math.acos(cosC)
        totalangle=angle+camangled
        oppcalc=400*(math.tan(totalangle))
        hypcalc=math.hypot(oppcalc,200)
        calc2=math.asin(oppcalc/hypcalc)
        rcalc = calc2 
        xdistance = -(hypcalc*(math.cos(rcalc)))
        xdistance = int(xdistance)
        ydistance = hypcalc*(math.sin(rcalc))
        ydistance = int(ydistance)
        print ('Row: %d column %d Value %d X %d Y %d r %d g %d b %d sd %f' %(yint,xcolumn,maxvalueis,xdistance,ydistance,redp,greenp,bluep,standdev[yint]))
        yint=yint+1
        numrec=numrec+1
        xvalues.append(xcolumn)
    else:
        yint=yint+1
if numrec> 0:
    xav=mean(xvalues)
    xav=int(xav)
    xmax=max(xvalues)
else:
    xav=0
    xmax=0
print ('Number at %f Threshold: %d with average: %d Max: %d' %(threshinput,numrec,xav,xmax))

    

    
    
