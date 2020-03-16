import cv2 as cv
import numpy as np
import time
fileoutput=input("Enter Filename: ")
fileoutput='/media/pi/usbdrive/' + fileoutput + '.csv'
fileoutputtype="w"
file_object=open(fileoutput,fileoutputtype)
#Threshold of maximum value to remove noise
threshinput=input("Enter Camera Threshold: ")
threshinput=float(threshinput)
rangeinput=input("Enter Gaussian range in pixels: ")
rangeinput=int(rangeinput)
#diffuses the maximum value across a certain amount to get rid of anomalies
radius=5
newrange1=[]
starttime=time.time()
lon1=cv.imread('lon1.jpg')
loff1=cv.imread('loff1.jpg')
#get x and y size
ysize=int(lon1.shape[0])
xsize=int(lon1.shape[1])
#subtract laser off from laser off images
src1=cv.subtract(lon1,loff1)
#create grayscale image from colour(not color, we are english...) image. Originally tried only taking the red channel, but this works better.
red1=cv.cvtColor(src1,cv.COLOR_BGR2GRAY)
#blur the image to get rid of random false maximum values
blur1=cv.GaussianBlur(red1,(radius,radius),0)
#find the maximum value in the whole image. Note: I'm sure there's a quicker way that doesn't also find the minimum value and their locations
(MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(blur1)
#create a threshold value which is a fraction of the maximum value, and remove any values below that threshold.
threshamount1=MaxVal1*threshinput
retval1,threshold1=cv.threshold(red1,threshamount1,255,cv.THRESH_TOZERO);
(MinVal1,MaxVal1,MinLoc1,MaxLoc1)=cv.minMaxLoc(threshold1)
#now find the maximum values in the new thresholded image, by line.
maxvalue1=np.argmax(threshold1,axis=0)

len1=len(maxvalue1)
for int1 in range(len1):
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
        newrange1.append(threshold1[int1,int2])
    file_object.write(minrange1 + ",")
    lenapp1=len(newrange1)
    for int3 in range(lenapp1):
        file_object.write((newrange1[int3])+",")
    file_object.write(maxrange1+"\n")
file_object.close


endtime=time.time()
timetaken=endtime-starttime
print("photos read in %d seconds"%timetaken)