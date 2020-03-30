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
fileoutput1=input("Enter Filename: ")
fileoutput1='/media/pi/usbdrive/' + fileoutput1 + '.csv'
fileoutputtype="w"
file_object1=open(fileoutput1,fileoutputtype)
#Threshold of maximum value to remove noise
threshinput=input("Enter Camera Threshold: ")
threshinput=float(threshinput)
rangeinput=input("Enter Gaussian range in pixels: ")
rangeinput=int(rangeinput)
frameinput=input("Enter Framerate (0 for adaptive): ")
frameinput=int(frameinput)
#diffuses the maximum value across a certain amount to get rid of anomalies
radius=5
#largest metering area available (30% of width of CCD)
camera.exposure_mode='verylong'
camera.meter_mode='backlit'
camera.framerate=frameinput
#increases colour saturation in camera.
camera.saturation=50
newrange1=[]
newrange2=[]

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
    starttime=time.time()
    camera1()
    #forces a long exposure time to get the best chance of seeing the laser line on the image, especially in the case of looking towards windows.
    expt=camera.exposure_speed
    if expt < 4000:
        camera.shutter_speed=4000
    else:
        camera.shutter_speed=0
    laser.on()
    camera.capture('/media/pi/usbdrive/lon1.jpg','jpeg')
    laser.off()
    camera.capture('/media/pi/usbdrive/loff1.jpg','jpeg')
    camera2()
    expt=camera.exposure_speed
    if expt < 4000:
        camera.shutter_speed=4000
    else:
        camera.shutter_speed=0
    camera.capture('/media/pi/usbdrive/lon2.jpg','jpeg')
    laser.off()
    camera.capture('/media/pi/usbdrive/loff2.jpg','jpeg')
    endtime=time.time()
    timetaken=endtime-starttime
    print("photos captured in %d seconds"%timetaken)
    
def readimages1():
    fileoutput=input("Enter Filename: ")
    fileoutput='/media/pi/usbdrive/' + fileoutput + '.csv'
    file_object=open(fileoutput,fileoutputtype)
    newrange1=[]
    newrange2=[]
    starttime=time.time()
    lon1=cv.imread('/media/pi/usbdrive/lon1.jpg')
    lon2=cv.imread('/media/pi/usbdrive/lon2.jpg')
    loff1=cv.imread('/media/pi/usbdrive/loff1.jpg')
    loff2=cv.imread('/media/pi/usbdrive/loff2.jpg')
    #get x and y size
    ysize=int(lon1.shape[0])
    xsize=int(lon1.shape[1])
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
    maxvalue1=np.argmax(threshold1,axis=1)
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(blur2)
    threshamount2=MaxVal2*threshinput
    retval2,threshold2=cv.threshold(red2,threshamount2,255,cv.THRESH_TOZERO);
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(threshold2)
    maxvalue2=np.argmax(threshold2,axis=1)
    
    len1=len(maxvalue1)-1
    for int1 in range(len1):
        newrange1.clear()
        if (maxvalue1[int1]) < rangeinput:
            minrange1=0
        else:
            minrange1=(maxvalue1[int1])-rangeinput
        if ((maxvalue1[int1])+rangeinput)>(xsize-1):
            maxrange1=xsize-1
        else:
            maxrange1=(maxvalue1[int1])+rangeinput
        minmaxrange1=maxrange1-minrange1
        for int2 in range(minmaxrange1):
            newrange1.append(threshold1[int1,(int2+minrange1)])
        if minrange1 !=0:
            file_object.write("cam1,")
            file_object.write(str(int1)+",")
            file_object.write(str(minrange1) + ",")
            lenapp1=len(newrange1)-1
            for int3 in range(lenapp1):
                file_object.write(str((newrange1[int3]))+",")
            file_object.write(str(maxrange1)+"\n")
        print ('Cam 1 Current int: [%d] min range [%d] max range [%d]\r'%(int1,minrange1,maxrange1),end="")

    len2=len(maxvalue2)-1
    for int4 in range(len2):
        newrange2.clear()
        if (maxvalue2[int4]) < rangeinput:
            minrange2=0
        else:
            minrange2=(maxvalue2[int4])-rangeinput
        if ((maxvalue2[int4])+rangeinput)>(xsize-1):
            maxrange2=xsize-1
        else:
            maxrange2=(maxvalue2[int4])+rangeinput
        minmaxrange2=maxrange2-minrange2
        for int5 in range(minmaxrange2):
            newrange2.append(threshold2[int4,(int5+minrange2)])
        if minrange2 !=0:
            file_object.write("cam2,")
            file_object.write(str(int4)+",")
            file_object.write(str(minrange2) + ",")
            lenapp2=len(newrange2)-1
            for int6 in range(lenapp2):
                file_object.write(str((newrange1[int6]))+",")
            file_object.write(str(maxrange2)+"\n")
        print ('Cam 2 Current int: [%d] min range [%d] max range [%d]\r'%(int4,minrange2,maxrange2),end="")

def readimages2():
    distancein=input("Input distance: ")
    materialin=input("Input material at centre of line: ")
    starttime=time.time()
    lon1=cv.imread('/media/pi/usbdrive/lon1.jpg')
    lon2=cv.imread('/media/pi/usbdrive/lon2.jpg')
    loff1=cv.imread('/media/pi/usbdrive/loff1.jpg')
    loff2=cv.imread('/media/pi/usbdrive/loff2.jpg')
    #get x and y size
    ysize=int(lon1.shape[0])
    xsize=int(lon1.shape[1])
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
    maxvalue1=np.argmax(threshold1,axis=1)
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(blur2)
    threshamount2=MaxVal2*threshinput
    retval2,threshold2=cv.threshold(red2,threshamount2,255,cv.THRESH_TOZERO);
    (MinVal2,MaxVal2,MinLoc2,MaxLoc2)=cv.minMaxLoc(threshold2)
    maxvalue2=np.argmax(threshold2,axis=1)
    #find the maximum value in the mid line of the camera
    maxpoint1=maxvalue1[(int(ysize/2))]
    maxpoint2=maxvalue2[(int(ysize/2))]
    #create a small array around the maximum value: Note - threshold[:,(ysize/2)] for column
    if maxpoint1<rangeinput:
        minrange1=0
    else:
        minrange1=maxpoint1-rangeinput
    if (maxpoint1+rangeinput)>(xsize-1):
        maxrange1=xsize-1
    else:
        maxrange1=maxpoint1+rangeinput
    minmaxrange1=maxrange1-minrange1
    
    if maxpoint2<rangeinput:
        minrange2=0
    else:
        minrange2=maxpoint2-rangeinput
    if (maxpoint2+rangeinput)>(xsize-1):
        maxrange2=xsize-1
    else:
        maxrange2=maxpoint2+rangeinput
    minmaxrange2=maxrange2-minrange2
    
    if minrange1 !=0:
        file_object1.write("cam1,")
        file_object1.write(distancein + "," + materialin + ",")
        file_object1.write(str(minrange1) + ",")
        for int7 in range(minmaxrange1):
            file_object1.write(str(threshold1[(int(ysize/2)),(int7+minrange1)])+",")
        file_object1.write(str(maxrange1)+"\n")
        
    if minrange2 !=0:
        file_object1.write("cam2,")
        file_object1.write(distancein + "," + materialin + ",")
        file_object1.write(str(minrange2) + ",")
        for int8 in range(minmaxrange2):
            file_object1.write(str(threshold2[(int(ysize/2)),(int8+minrange2)])+",")
        file_object1.write(str(maxrange2)+"\n")

    
def main():
    userin=""
    while userin!='end':
        userin=input("Command: ")
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
        if userin=="r1":
            readimages1()
        if userin=="r2":
            readimages2()
        if userin=="h":
            print("p - preview cameras")
            print("s - stop preview")
            print("c1 - camera 1")
            print("c2 - camera 2")
            print("c -capture images")
            print("r1 - read images - all lines")
            print("r2 - read images - single line with dim and material")
    file_object.close
    camera.close()

    
if __name__ == "__main__":
    main()