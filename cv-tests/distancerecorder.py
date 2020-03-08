from gpiozero import LED
import os
from picamera import PiCamera
import cv2 as cv
import numpy as np
cselect=LED(4)
cenable1=LED(17)
cenable2=LED(18)
laser=LED(20)
i2c='i2cset -y 1 0x70 0x00 0x04'
os.system(i2c)
cselect.off()
cenable1.off()
cenable2.on()
camera=PiCamera()
camera.resolution=(3280,2464)
fileoutput=input("Enter Filename: ")
fileoutput='/media/pi/usbdrive/' + fileoutput + '.csv'
fileoutputtype="w"#
#Have a look into a way to check for existing files so we can change this to a (append)
threshinput=input("Enter Camera Threshold: ")
threshinput=float(threshinput)
#Threshold of maximum value to remove noise
radius=5
#diffuses the maximum value across a certain amount to get rid of anomalies
camera.meter_mode='backlit'
camera.saturation=50

def camera1():
    cselect.off()
    cenable1.off()
    cenable2.on()
    i2c='i2cset -y 1 0x70 0x00 0x04'
    os.system(i2c)
       
def camera3():
    cselect.off()
    cenable1.on()
    cenable2.off()
    i2c='i2cset -y 1 0x70 0x00 0x06'
    os.system(i2c)
    
def ccheck():
    camera._check_camera_open()
    
def cpreview():
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    print("camera active")
    
def cstop():
    camera.stop_preview()
    
def measure():
    distancein=input("Input measured distance to centre of object: ")
    camera1()
    #forces a long exposure time to get the best chance of seeing the laser line on the image, especially in the case of looking towards windows.
    expt=camera.exposure_speed
    if expt < 4000:
        camera.shutter_speed=4000
    else:
        camera.shutter_speed=0
    laser.on()
    camera.capture('lon1.jpg','jpeg',use_video_port=True)
    laser.off()
    camera.capture('loff1.jpg','jpeg',use_video_port=True)
    camera2()
    expt=camera.exposure_speed
    if expt < 4000:
        camera.shutter_speed=4000
    else:
        camera.shutter_speed=0
    camera.capture('lon2.jpg','jpeg',use_video_port=True)
    laser.off()
    camera.capture('loff2.jpg','jpeg',use_video_port=True)
    lon1=cv.imread('lon1.jpg')
    lon2=cv.imread('lon2.jpg')
    loff1=cv.imread('loff1.jpg')
    loff2=cv.imread('loff2.jpg')
    ysize=lon1.shape[0]
    xsize=lon1.shape[1]
    #rotate the images, the cameras are rotated 90 degrees, this is not strictly speaking necessary, but just makes things easier to work with.
    centerim=(xsize/2,ysize/2)
    M=cv.getRotationMatrix2d(centerim,270,1.0)
    lon1=cv.warpAffine(lon1,M,(xsize,ysize))
    lon2=cv.warpAffine(lon2,M,(xsize,ysize))
    loff1=cv.warpAffine(loff1,M,(xsize,ysize))
    loff2=cv.warpAffine(loff2,M,(xsize,ysize))
    #subtract laser off from laser off images
    src1=cv.subtract(lon1,loff1)
    src2=cv.subtract(lon2,loff2)
    #create grayscale image from colour(not color, we are english...) image. Originally tried only taking the red channel, but this works better.
    red1=cv.cvtColor(src1,cv.COLOR_BGR2GRAY)
    red2=cv.cvtColor(src2,cv.COLOR_BGR2GRAY)
    #blur the image to get rid of random false maximum values
    blur1=cv.GaussianBlur(red1,(radius,radius),0)
    blur2=cv.GaussianBlur(red2,(radius,radius),0)
    (MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(blur1)
    threshamount1=MaxVal1*threshinput
    retval1,threshold1=cv.threshold(red1,threshamount1,255,cv.THRESH_TOZERO);
    (MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(threshold1)
    maxvalue1=np.argmax(threshold1,axis=0)
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(blur2)
    threshamount2=MaxVal2*threshinput
    retval2,threshold2=cv.threshold(red2,threshamount2,255,cv.THRESH_TOZERO);
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(threshold2)
    maxvalue2=np.argmax(threshold2,axis=0)
    
    
    
def main():
    userin=""
    #while userin!='end':
        
    #camera.close()

    
if __name__ == "__main__":
    main()