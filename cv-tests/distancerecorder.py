from gpiozero import LED
import os
from picamera import PiCamera
import cv2 as cv
import numpy as np
import time
cselect=LED(4)
cenable1=LED(17)
cenable2=LED(18)
laser=LED(20)
i2c='i2cset -y 1 0x70 0x00 0x04'
os.system(i2c)
#using the arducam splitter nomenclature, ours will only need 2 GPIOs
cselect.off()
cenable1.off()
cenable2.on()
camera=PiCamera()
#setting at maximum resolution for 8MP camera for test.
camera.resolution=(3280,2464)
#Have a look into a way to check for existing files so we can change this to a (append)
fileoutput=input("Enter Filename: ")
fileoutput='/media/pi/usbdrive/' + fileoutput + '.csv'
fileoutputtype="w"
file_object=open(fileoutput,fileoutputtype)
file_object.write("distance in,max value 1,median value 1, max value 2, median value2 \n")
#Threshold of maximum value to remove noise
threshinput=input("Enter Camera Threshold: ")
threshinput=float(threshinput)
rangeinput=input("Enter Gaussian range in pixels: ")
rangeinput=int(rangeinput)
#diffuses the maximum value across a certain amount to get rid of anomalies
radius=5
#largest metering area available (30% of width of CCD)
camera.meter_mode='backlit'
#increases colour saturation in camera.
camera.saturation=50

def camera1():
    cselect.off()
    cenable1.off()
    cenable2.on()
    i2c='i2cset -y 1 0x70 0x00 0x04'
    os.system(i2c)
       
def camera2():
    cselect.off()
    cenable1.on()
    cenable2.off()
    i2c='i2cset -y 1 0x70 0x00 0x06'
    os.system(i2c)
    
def cpreview():
    camera.start_preview(fullscreen=False,window=(0,0,640,480))
    print("camera active")
    
def cstop():
    camera.stop_preview()
    
def capture():
    distancein=input("Input measured distance to centre of object: ")
    starttime=time.time()
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
    endtime=time.time()
    timetaken=endtime-starttime
    print("photos captured in %d seconds"%timetaken)
    
def readimages():
    starttime=time.time()
    lon1=cv.imread('lon1.jpg')
    lon2=cv.imread('lon2.jpg')
    loff1=cv.imread('loff1.jpg')
    loff2=cv.imread('loff2.jpg')
    #get x and y size
    ysize=lon1.shape[0]
    xsize=lon1.shape[1]
    #subtract laser off from laser off images
    src1=cv.subtract(lon1,loff1)
    src2=cv.subtract(lon2,loff2)
    #create grayscale image from colour(not color, we are english...) image. Originally tried only taking the red channel, but this works better.
    red1=cv.cvtColor(src1,cv.COLOR_BGR2GRAY)
    red2=cv.cvtColor(src2,cv.COLOR_BGR2GRAY)
    #blur the image to get rid of random false maximum values
    blur1=cv.GaussianBlur(red1,(radius,radius),0)
    blur2=cv.GaussianBlur(red2,(radius,radius),0)
    #find the maximum value in the whole image. Note: I'm sure there's a quicker way that doesn't also find the minimum value and their locations
    (MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(blur1)
    #create a threshold value which is a fraction of the maximum value, and remove any values below that threshold.
    threshamount1=MaxVal1*threshinput
    retval1,threshold1=cv.threshold(red1,threshamount1,255,cv.THRESH_TOZERO);
    (MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(threshold1)
    #now find the maximum values in the new thresholded image, by line.
    maxvalue1=np.argmax(threshold1,axis=0)
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(blur2)
    threshamount2=MaxVal2*threshinput
    retval2,threshold2=cv.threshold(red2,threshamount2,255,cv.THRESH_TOZERO);
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(threshold2)
    maxvalue2=np.argmax(threshold2,axis=0)
    #find the maximum value in the mid line of the camera
    maxpoint1=maxvalue1[(ysize/2)]
    maxpoint2=maxvalue2[(ysize/2)]
    #create a small array around the maximum value: Note - threshold[:,(ysize/2)] for column
    if maxpoint1<rangeinput:
        minrange1=0
    else:
        minrange1=maxpoint1-rangeinput
    if (maxpoint1+rangeinput)>(xsize-1):
        maxrange1=xsize-1
    else:
        maxrange1=maxpoint1+rangeinput
    minmaxrange1=[minrange1,maxrange1]
    newrange1=[x for x in threshold1[:,(ysize/2)] if minmaxrange1[0] <= x <= minmaxrange1[1]]
    #find index of first value that is closest to median (will probably always be exact match in our case)
    med1i=newrange1.index(np.percentile(newrange1,50,'nearest'))
    med1=np.percentile(newrange1,50,'nearest')
    #find out how many times that value actually appears
    numcount1=newrange1.count(med1)
    if numcount1>1:
        numcountadj1=(numcount1-1)/2
    else:
        numcountadj1=0
    #add them all together, and hey presto, hopefully an accurate middle of the laser line!
    medli=medli+numcountadj1+minrange1
    #a bit of a blunt way of doing it, but this should make it so if there isn't a laser line visible, we get a zero result
    if sum(newrange1)<(2.5*med1):
        med1i=0
    
    #now array 2
    if maxpoint2<rangeinput:
        minrange2=0
    else:
        minrange2=maxpoint2-rangeinput
    if (maxpoint2+rangeinput)>(xsize-1):
        maxrange2=xsize-1
    else:
        maxrange2=maxpoint2+rangeinput
    minmaxrange2=[minrange2,maxrange2]
    newrange2=[x for x in threshold2[:,(ysize/2)] if minmaxrange2[0] <= x <= minmaxrange2[1]]
    med2i=newrange2.index(np.percentile(newrange2,50,'nearest'))
    med2=np.percentile(newrange2,50,'nearest')
    numcount2=newrange2.count(med2)
    if numcount2>1:
        numcountadj2=(numcount2-1)/2
    else:
        numcountadj2=0
    med2i=med2i+numcountadj2+minrange2
    if sum(newrange2)<(2.5*med2):
        med2i=0
    file_object.write(distancein + "," + maxpoint1 + "," + med1i + "," + maxpoint2 + "'" + med2i + "\n")
    endtime=time.time()
    timetaken=endtime-starttime
    print("max point1 %d med point1 %f max point 2 %d med point 2 %f" % (maxpoint1,med1i,maxpoint2,med2i))
    print("photos read in %d seconds"%timetaken)
    
def main():
    userin=""
    while userin!='end':
        if userin=="p":
            cpreview()
        if userin=="s":
            cstop()
        if userin=="c1":
            camera1()
        if userin =="c2":
            camera2()
        if userin=="c":
            capture()
        if userin=="r":
            readimages()
        if userin=="h":
            print("p - preview cameras")
            print("s - stop preview")
            print("c1 - camera 1")
            print("c2 - camera 2")
            print("c -capture images")
            print("r - read images")
    camera.close()
    file_object.close

    
if __name__ == "__main__":
    main()