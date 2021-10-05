import RPi.GPIO as GPIO
import os
from picamera import PiCamera
import time
import cv2 as cv
import numpy as np
import serial
s=serial.Serial('/dev/ttyAMA0',9600, timeout = 6, writeTimeout = 20)
s.flushInput()  # Flush startup text in serial input
s.write(('\n\n').encode('utf-8'))
file_path = '/media/pi/SCANFILES/'

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
    starttime=time.time()
    GPIO.output(chan_listl,0)
    print("main capture start")
    camera.capture(file_path + "loff.jpeg",use_video_port=True)
    GPIO.output(chan_listl,1)
    camera.capture(file_path + "lon.jpeg",use_video_port=True)
    GPIO.output(chan_listl,0)
    endtime=time.time()
    print("captured in %d seconds"%(endtime-starttime))
    starttime=time.time()
    loff=cv.imread(file_path + "loff.jpeg")
    lon=cv.imread(file_path + "lon.jpeg")
    src=cv.subtract(lon,loff)
    srcone=src[:,:,0]
    threshamount = input("Enter threshold amount 1-255: ")
    threshamount = int(threshamount)
    retval, threshold_ar = cv.threshold(srcone, threshamount, 255, cv.THRESH_TOZERO);
    maxvalue = np.argmax(threshold_ar,axis=1)
    row, col = threshold_ar.shape
    rawdata_file=open(file_path+"raw data.txt","wt")
    for i in range(row):
        for i2 in range(col):
            rawdata_file.write(str(threshold_ar[i,i2]) + ",")
        rawdata_file.write("\n")
    rawdata_file.close()
    weighteddata_file=open(file_path+"weighted data.txt","wt")
    for i in range(row):
        if maxvalue[i] != 0:
            newarray=threshold_ar[i,:]
            laserctr=weighted_average(newarray)
            if laserctr != 0:
                weighteddata_file.write(str(laserctr) + "\n")
    weighteddata_file.close()            
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
        if userin =='cal':
            shutterspeedcalc()
        if userin =='calf':
            shutterspeedcalcfull()
        if userin=='h':
            print ("c1 - select camera 1")
            print ("c3 - select camera 3")
            print ("cc - Camera check")
            print ("p - Preview")
            print ("s - Stop Preview")
            print ("l = laser (on or off)")
            print ("cal = shutter speed calibration")
            print ("cap = capture")
    
    camera.close()
    GPIO.cleanup()

def shutterspeedcalc():
    global maxvalueinit
    global maxvalb
    global maxvalg
    global maxvalr
    print("Resolution for Shutter speed calculation")
    print("Resolution 1: 320,240")
    print("Resolution 2: 640,480")
    print("Resolution 3: 1280,720")
    print("Resolution 4: 1640,1232")
    print("Resolution 5: 3280:2464")
    print("Resolution 6: 500,50")
    print("Resolution 7: 1000,50")
    print("Resolution 8: 1786,50")
    resinput=input("Select Resolution: ")
    resinput=int(resinput)
    if resinput ==1:
        camera.resolution=(320,240)
    if resinput ==2:
        camera.resolution=(640,480)
    if resinput ==3:
        camera.resolution=(1280,720)
    if resinput ==4:
        camera.resolution=(1640,1232)
    if resinput ==5:
        camera.resolution=(3280,2464)
    if resinput ==6:
        camera.resolution=(500,50)
    if resinput ==7:
        camera.resolution=(1000,50)
    if resinput ==8:
        camera.resolution=(1786,50)    
    shutterspeed=1
    camera.shutter_speed=shutterspeed
    maxvalueinit=0
    GPIO.output(chan_listl,1)
    camera.exposure_mode='off'
    camera.awb_mode='off'
    camera.image_denoise=0
    camera.image_effect='none'
    camera.meter_mode='spot'
    camera.iso=100
    inputmax=input("Input cutoff threshold value (between 1 and 255: ")
    inputmax=int(inputmax)
    while maxvalueinit<inputmax:
        camera.shutter_speed=shutterspeed
        camera.capture('lcalib.jpeg',use_video_port=True)
        calib=cv.imread('lcalib.jpeg')
        calibb=calib[:,:,0]
        calibg=calib[:,:,1]
        calibr=calib[:,:,2]
        (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibb)
        maxvalb=maxVal
        (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibg)
        maxvalg=maxVal
        (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibr)
        maxvalr=maxVal
        maxvalueinit=max(maxvalb,maxvalg,maxvalr)
        shutterspeed=shutterspeed+25
        print('shutter speed [%d] max value [%d] B [%d] G [%d] R [%d]\r'%(shutterspeed,maxvalueinit,maxvalb,maxvalg,maxvalr),end="")     
    print("")
        
def shutterspeedcalcfull():
    s.write(('e1\n').encode('utf-8')) #Enables the stepper motor driver, turns out the program light.
    s.write(('z\n').encode('utf-8')) #Zeroes the encoder in the stepper
    global maxvalueinit
    global maxvalb
    global maxvalg
    global maxvalr
    fullres=input("Full resolution?(y/n): ")
    if fullres !="y":
        resstart=2
    else:
        resstart=1
    shutterout=[]
    GPIO.output(chan_listl,1)
    camera.exposure_mode='off'
    camera.awb_mode='off'
    camera.image_denoise=0
    camera.image_effect='none'
    camera.meter_mode='spot'
    camera.iso=100
    inputmax=input("Input cutoff threshold value (between 1 and 255: ")
    inputmax=int(inputmax)
    for rotation in range(8):
        resinput=resstart
        shutteroutline=[]
        while resinput<6:
            if resinput ==1:
                camera.resolution=(3280,2464)
            if resinput ==2:
                camera.resolution=(1280,720)
            if resinput ==3:
                camera.resolution=(1640,1232)
            if resinput ==4:
                camera.resolution=(1000,50)
            if resinput ==5:
                camera.resolution=(1786,50)   
            shutterspeed=200
            camera.shutter_speed=shutterspeed
            time.sleep(1)
            maxvalueinit=0
            
            while maxvalueinit<inputmax:
                camera.shutter_speed=shutterspeed
                camera.capture('lcalib.jpeg',use_video_port=True)
                calib=cv.imread('lcalib.jpeg')
                calibb=calib[:,:,0]
                calibg=calib[:,:,1]
                calibr=calib[:,:,2]
                (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibb)
                maxvalb=maxVal
                (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibg)
                maxvalg=maxVal
                (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(calibr)
                maxvalr=maxVal
                maxvalueinit=max(maxvalb,maxvalg,maxvalr)
                shutterspeed=shutterspeed+25
                print('resolution {%d] shutter speed [%d] max value [%d] B [%d] G [%d] R [%d] rotation [%d]             \r'%(resinput,shutterspeed,maxvalueinit,maxvalb,maxvalg,maxvalr,rotation),end="")     
            shutteroutline.append(shutterspeed)
            resinput=resinput+1
        s.write(('a450\n').encode('utf-8'))
        time.sleep(5)
        shutterout.append(shutteroutline)
    print("")
    #print("Shutter speeds in order: ", shutterout)
    shutmin=np.nanmin(shutterout,axis=0)
    shutmean=np.mean(shutterout,axis=0)
    shutmax=np.nanmax(shutterout,axis=0)
    print("min of shutter speeds by resolution: ",shutmin)
    print("mean of shutter speeds by resolution: ",shutmean)
    print("max of shutter speeds by resolution: ",shutmax)
    if resstart==1:
        print("3/4 of slice photo1 min: ",((shutmin[3])*0.75))
        print("3/4 of slice photo1 mean: ",((shutmean[3])*0.75))
        print("3/4 of slice photo1 max: ",((shutmax[3])*0.75))
    else:
        print("3/4 of slice photo1 min: ",((shutmin[2])*0.75))
        print("3/4 of slice photo1 mean: ",((shutmean[2])*0.75))
        print("3/4 of slice photo1 max: ",((shutmax[2])*0.75))
        
    s.write(('e0\n').encode('utf-8')) #Enables the stepper motor driver, turns out the program light.   
    
def weighted_average(t):
    t = t.flatten()
    tmax=max(t) # highest intensity value in row
    maxvalue=np.argmax(t) # position of value
    length=t.size #length of array, should be equal to Y resolution....
    numerator=sum(([t]*i) for i in range(length))
    denominator=sum(i for i in range(length))
    weighted=round(numerator/denominator,2)            
    return(weighted)
      
if __name__ == "__main__":
    main()