#!/usr/bin/python3
print ("Loading...")
from tkinter import *
import cv2 as cv
import numpy as np
import math
from nanpy import (ArduinoApi, SerialManager)
import time
import picamera
import picamera.array
import os
import sys

photographs=0
revolutions=0
camangle = (62.2/(180/math.pi))
camangled=(28.9/(180/math.pi))
Bconst = (58.9/(180/math.pi))
cosB = math.cos(Bconst)
connection = SerialManager(device='/dev/ttyACM0')
a = ArduinoApi(connection=connection)
maxvalue=[]
Waittime = 0.005
yWaittime = 0.000005
yreturn = 915
dirstp1 = 25
stpstp1 = 3
ms3stp1 = 31
ms2stp1 = 29
ms1stp1 = 27

dirstp2 = 24
stpstp2 = 2
ms3stp2 = 26
ms2stp2 = 28
ms1stp2 = 30
lsrctrl = 32
endstop = 49
ydist = []
xdist = []
zdist=[]
rpix=[]
gpix=[]
bpix=[]
numlines=[]
cam1out=[]
cam1outplusx=[]
cam1outminusx=[]
cam1outplusy=[]
cam1outminusy=[]
cam1outr=[]
cam1outg=[]
cam1outb=[]
rone=[]
rtwo=[]


a.pinMode(dirstp1, a.OUTPUT)
a.pinMode(stpstp1, a.OUTPUT)
a.pinMode(ms3stp1, a.OUTPUT)
a.pinMode(ms2stp1, a.OUTPUT)
a.pinMode(ms1stp1, a.OUTPUT)
a.pinMode(dirstp2, a.OUTPUT)
a.pinMode(stpstp2, a.OUTPUT)
a.pinMode(ms3stp2, a.OUTPUT)
a.pinMode(ms2stp2, a.OUTPUT)
a.pinMode(ms1stp2, a.OUTPUT)
a.pinMode(lsrctrl, a.OUTPUT)
a.pinMode(endstop, a.INPUT)

a.digitalWrite(ms3stp1, a.HIGH)
a.digitalWrite(ms2stp1, a.HIGH)
a.digitalWrite(ms1stp1, a.HIGH)
a.digitalWrite(ms3stp2, a.HIGH)
a.digitalWrite(ms2stp2, a.HIGH)
a.digitalWrite(ms1stp2, a.HIGH)
a.digitalWrite(dirstp1, a.LOW)

scanangle=90
scanres=1.2
xresolution=1080

class Application(Frame):
    def rotation_angle90(self):
        global scanangle
        scanangle=90
        self.r90["fg"]="red"
        self.r180["fg"]="black"
        self.r270["fg"]="black"
        self.r360["fg"]="black"
        
    def rotation_angle180(self):
        global scanangle
        scanangle=180
        self.r90["fg"]="black"
        self.r180["fg"]="red"
        self.r270["fg"]="black"
        self.r360["fg"]="black"

    def rotation_angle270(self):
        global scanangle
        scanangle=270
        self.r90["fg"]="black"
        self.r180["fg"]="black"
        self.r270["fg"]="red"
        self.r360["fg"]="black"

    def rotation_angle360(self):
        global scanangle
        scanangle=360
        self.r90["fg"]="black"
        self.r180["fg"]="black"
        self.r270["fg"]="black"
        self.r360["fg"]="red"
        
    def resolution03(self):
        global scanres
        scanres=0.3
        self.res03["fg"]="red"
        self.res06["fg"]="black"
        self.res12["fg"]="black"

    def resolution06(self):
        global scanres        
        scanres=0.6
        self.res03["fg"]="black"
        self.res06["fg"]="red"
        self.res12["fg"]="black"

    def resolution12(self):
        global scanres
        scanres=1.2
        self.res03["fg"]="black"
        self.res06["fg"]="black"
        self.res12["fg"]="red"

    def camresmax(self):
        global xresolution
        xresolution=3280
        self.camresmax["fg"]="red"
        self.camresmed["fg"]="black"
        self.camreslow["fg"]="black"

    def camresmed(self):
        global xresolution
        xresolution=1920
        self.camresmax["fg"]="black"
        self.camresmed["fg"]="red"
        self.camreslow["fg"]="black"

    def camreslow(self):
        global xresolution
        xresolution=1080
        self.camresmax["fg"]="black"
        self.camresmed["fg"]="black"
        self.camreslow["fg"]="red"

    def ycalibrate(self):
        a.digitalWrite(dirstp2, a.HIGH)
        endstate = a.LOW
        while endstate == a.LOW:
            endstate = a.digitalRead(endstop)
            a.digitalWrite(stpstp2, a.HIGH)
            time.sleep(0.000001)
            a.digitalWrite(stpstp2, a.LOW)
            time.sleep(0.000001)
        steps = 0
        a.digitalWrite(dirstp2, a.LOW)
        for steps in range (yreturn):
            a.digitalWrite(stpstp2, a.HIGH)
            time.sleep(0.000001)
            a.digitalWrite(stpstp2, a.LOW)
            time.sleep(0.000001)

    def startscanning(self):
        
        global yresolution
        yresolution=int(xresolution/(3280/2464))
        global adjforz
        adjforz=((yresolution/2)/(math.tan((24.4)/(180/math.pi))))
        scanresz=1
        global threshinput
        threshinput=0.2
        global radius
        radius=5
        global aconst
        aconst = (xresolution*(math.sin(Bconst)))/(math.sin(camangle))
        global aconstsqrd
        aconstsqrd = math.pow(aconst,2)
        r=0
        
        global scansteps
        scansteps = round(scanangle/scanres)
        with picamera.PiCamera() as camera:
            camera.start_preview(fullscreen=False,window=(0,0,640,480))
            camera.resolution=(xresolution,yresolution)
            camera.meter_mode='backlit'
            camera.saturation=50
            time.sleep(2)
            print ("Scan start")
            scanstarttime=time.time()
            global revolutions
            for revolutions in range(scansteps):
                scanstepsstring=str(revolutions)
                expt=camera.exposure_speed
                if expt < 4000:
                    camera.shutter_speed=4000
                else:
                    camera.shutter_speed=0
                camera.awb_gains=(0,0)
                revnumstr=str(revolutions)
                loffname='/media/pi/usbdrive/loff' + revnumstr + '.jpg'
                camera.capture(loffname,'jpeg',use_video_port=True)
                lonname='/media/pi/usbdrive/lon' + revnumstr + '.jpg'
                a.digitalWrite(lsrctrl, a.HIGH)
                camera.awb_gains=(8,0)
                camera.capture(lonname,'jpeg',use_video_port=True)
                camera.shutter_speed=0
                calcustep = (scanres/1.8)*3*16
                calcustep= int(calcustep)
                steps = 0
                for steps in range(calcustep):
                    a.digitalWrite(stpstp1, a.HIGH)
                    time.sleep(0.01)
                    a.digitalWrite(stpstp1, a.LOW)
                    time.sleep(0.01)
                    steps +=1
                a.digitalWrite(dirstp1, a.HIGH)
                a.digitalWrite(stpstp1, a.HIGH)
                time.sleep(0.01)
                a.digitalWrite(stpstp1, a.LOW)
                time.sleep(0.01)
                a.digitalWrite(dirstp1, a.LOW)
                a.digitalWrite(stpstp1, a.HIGH)
                time.sleep(0.0001)
                a.digitalWrite(stpstp1, a.LOW)
                time.sleep(0.0001)
                a.digitalWrite(lsrctrl, a.LOW)
                if revolutions != 0:
                    rone.append((revolutions)/(180/math.pi))
                else:
                    rone.append(0)
                rtwo.append(0)
        global scanendtime
        scanendtime=time.time()
        camera.close
        print("Photographic scan completed in %f seconds" % (int(scanendtime-scanstarttime)))
        self.readimages()
        
    def startscanningfull(self):
        zres=30/(180/math.pi)
        zresin=-2*zres
        global yresolution
        yresolution=int(xresolution/(3280/2464))
        global adjforz
        adjforz=((yresolution/2)/(math.tan((24.4)/(180/math.pi))))
        scanresz=1
        global threshinput
        threshinput=0.2
        global radius
        radius=5
        global aconst
        aconst = (xresolution*(math.sin(Bconst)))/(math.sin(camangle))
        global aconstsqrd
        aconstsqrd = math.pow(aconst,2)
        
        
        global scansteps
        scansteps = round((scanangle*4)/scanres)
        a.digitalWrite(dirstp2, a.LOW)
        for vertsteps in range(int((60/1.8)*3*16)):
            a.digitalWrite(stpstp2, a.HIGH)
            time.sleep(0.000001)
            a.digitalWrite(stpstp2, a.LOW)
            time.sleep(0.000001)
        a.digitalWrite(dirstp2, a.HIGH)
        
        with picamera.PiCamera() as camera:
            camera.start_preview(fullscreen=False,window=(0,0,640,480))
            camera.resolution=(xresolution,yresolution)
            camera.meter_mode='backlit'
            camera.saturation=50
            time.sleep(2)
            print ("Scan start")
            scanstarttime=time.time()
            photonum=0
            a.digitalWrite(dirstp1, a.LOW)

            for vertrev in range(4):
                for revolutions in range(round(scansteps/4)):
                    scanstepsstring=str(revolutions)
                    expt=camera.exposure_speed
                    if expt < 4000:
                        camera.shutter_speed=4000
                    else:
                        camera.shutter_speed=0
                    camera.awb_gains=(0,0)
                    revnumstr=str(photonum)
                    loffname='/media/pi/usbdrive/loff' + revnumstr + '.jpg'
                    camera.capture(loffname,'jpeg',use_video_port=True)
                    lonname='/media/pi/usbdrive/lon' + revnumstr + '.jpg'
                    a.digitalWrite(lsrctrl, a.HIGH)
                    camera.awb_gains=(8,0)
                    camera.capture(lonname,'jpeg',use_video_port=True)
                    camera.shutter_speed=0
                    calcustep = (scanres/1.8)*3*16
                    calcustep= int(calcustep)
                    steps = 0
                    for steps in range(calcustep):
                        a.digitalWrite(stpstp1, a.HIGH)
                        time.sleep(0.01)
                        a.digitalWrite(stpstp1, a.LOW)
                        time.sleep(0.01)
                        steps +=1
                    a.digitalWrite(dirstp1, a.HIGH)
                    a.digitalWrite(stpstp1, a.HIGH)
                    time.sleep(0.01)
                    a.digitalWrite(stpstp1, a.LOW)
                    time.sleep(0.01)
                    a.digitalWrite(dirstp1, a.LOW)
                    a.digitalWrite(stpstp1, a.HIGH)
                    time.sleep(0.0001)
                    a.digitalWrite(stpstp1, a.LOW)
                    time.sleep(0.0001)
                    a.digitalWrite(lsrctrl, a.LOW)
                    if revolutions != 0:
                        rone.append((revolutions)/(180/math.pi))
                    else:
                        rone.append(0)
                    rtwo.append(zresin)
                    photonum=photonum+1
                zresin=zresin+zres
                if vertrev < 4:
                    for vertsteps in range(int((30/1.8)*3*16)):
                        a.digitalWrite(stpstp2, a.HIGH)
                        time.sleep(0.000001)
                        a.digitalWrite(stpstp2, a.LOW)
                        time.sleep(0.000001)
                    if scanangle <360:
                        a.digitalWrite(dirstp1, a.HIGH)
                        for steps in range(int((scanangle/1.8)*3*16)):
                            a.digitalWrite(stpstp1, a.HIGH)
                            time.sleep(0.000001)
                            a.digitalWrite(stpstp1, a.LOW)
                            time.sleep(0.000001)
                        a.digitalWrite(dirstp1, a.LOW)
                
        global scanendtime
        scanendtime=time.time()
        camera.close
        print("Photographic scan completed in %f seconds" % (int(scanendtime-scanstarttime)))
        self.readimages()
        
    def saveoutput(self):
        fileoutput = "Example.pts"
        fileoutput = '/media/pi/usbdrive/' + fileoutput
        fileoutputtype = "w"
        file_object = open(fileoutput,fileoutputtype)

        print ("Scan ended, saving")
        exportint = len(xdist)
    
        for export in range (exportint):
            xout = str(xdist[export])
            yout = str(ydist[export])
            zout = str(zdist[export])
            rout = str(rpix[export])
            gout=str(gpix[export])
            bout=str(bpix[export])
            file_object.write(xout + " " + yout + " " + zout + " " + rout + " " + gout + " " + bout + "\n")

        file_object.close()
        
        saveendtime=time.time()
        print("File outputted in %f seconds" % (int(saveendtime-calculateendtime)))
        sys.exit()

    def readimages(self):
        #while revolutions==0:
            #time.sleep(0.001)
        #global photographs
        
        for photographs in range(scansteps):
            pnumstr=str(photographs)
            loffname='/media/pi/usbdrive/loff' + pnumstr + '.jpg'
            lonname='/media/pi/usbdrive/lon'+pnumstr + '.jpg'
            loff=cv.imread(loffname)
            lon=cv.imread(lonname)
            src=cv.subtract(lon,loff)
            red=cv.cvtColor(src,cv.COLOR_BGR2GRAY)
            blur=cv.GaussianBlur(red,(5,5),0)
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur)
            threshamount = maxVal*threshinput
            retval, threshold = cv.threshold(red, threshamount, 255, cv.THRESH_TOZERO);
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(threshold)
            maxvalue = np.argmax(threshold,axis=1)
            os.remove(loffname)
            os.remove(lonname)
            print ('Image [%d] of [%d] read\r'%(photographs,scansteps),end="")
            succesful=0
            for i in range(yresolution):
                xcolumn=maxvalue[i]
                pxminus=threshold[i,((maxvalue[i])-1)]
                if i > 0:
                    pyminus=threshold[(i-1),(maxvalue[i])]
                else:
                    pyminus=threshold[i,(maxvalue[i])]
                if i == (yresolution-1):
                    pyplus=threshold[i,(maxvalue[i])]
                else:
                    pyplus=threshold[(i+1),(maxvalue[i])]
                if xcolumn < (xresolution-1):
                    pxadd=threshold[i,((maxvalue[i])+1)]
                else:
                    pxadd=threshold[i,((maxvalue[i]))]
                if xcolumn > 0 and pxminus !=0 and pxadd !=0 and pyplus!=0 and pyminus !=0:
                    cam1out.append(xcolumn)
                    succesful=succesful+1
                    cam1outr.append(loff[i,xcolumn,2])
                    cam1outg.append(loff[i,xcolumn,1])
                    cam1outb.append(loff[i,xcolumn,0])
            numlines.append(succesful)
                
        global readimageendtime
        readimageendtime=time.time()
        print("Images read in %f seconds" % (int(readimageendtime-scanendtime)))
        self.calculatepoints()
                

    def calculatepoints(self):
        
        tlines=0
        #while photographs==0:
            #time.sleep(0.001)
        for calculations in range(scansteps):
            readlines=numlines[calculations]
            for yint in range(readlines):
                xcolumn=cam1out[yint+tlines]            
                cosC=((2*aconstsqrd)-(2*aconst*(xcolumn+1)*cosB))/((2*aconst*(math.sqrt((aconstsqrd+((xcolumn+1)*(xcolumn+1))-(2*aconst*(xcolumn+1)*cosB))))))
                angle=math.acos(cosC)
                totalangle=angle+camangled
                oppcalc=400*(math.tan(totalangle))
                hypcalc=math.hypot(oppcalc,200)
                calc2=math.asin(oppcalc/hypcalc)
                rrad= rone[calculations]
                rz=rtwo[calculations]
                rcalc = calc2 + rrad
                if hypcalc < 10000:
                    redp=cam1outr[yint+tlines]
                    rpix.append(redp)
                    greenp=cam1outg[yint+tlines]
                    gpix.append(greenp)
                    bluep=cam1outb[yint+tlines]
                    bpix.append(bluep)
                    xdistance = -(hypcalc*(math.cos(rcalc)))
                    xdistance = round(xdistance,1)
                    ydistance = hypcalc*(math.sin(rcalc))
                    ydistance = round(ydistance,1)
                    ydist.append(ydistance)
                    xdist.append(xdistance)
                    if yint > (yresolution/2):
                        angle = (math.atan(((yint+1)-(yresolution/2))/adjforz))+rz
                        tancalc=-(oppcalc*(math.tan(angle)))
                    else:
                        angle = (math.atan(((yresolution/2)-(yint+1))/adjforz))+rz
                        tancalc=(oppcalc*(math.tan(angle)))
                    tancalc = round(tancalc, 1)
                    zdist.append(tancalc)
            tlines=tlines+readlines
        global calculateendtime
        calculateendtime=time.time()
        print("Calculations complete in %f seconds" % (int(calculateendtime-readimageendtime)))
        self.saveoutput()

    def createWidgets(self):
        topLabel=Frame(root)
        topLabel.pack()
        RotButtons=Frame(root)
        RotButtons.pack(side=BOTTOM)
        ResLabel=Frame(root)
        ResLabel.pack(side=BOTTOM)
        ResButtons=Frame(root)
        ResButtons.pack(side=BOTTOM)
        CamResLabel=Frame(root)
        CamResLabel.pack(side=BOTTOM)
        CamResButtons=Frame(root)
        CamResButtons.pack(side=BOTTOM)
        CalibButton=Frame(root)
        CalibButton.pack(side=BOTTOM)
        GoButton=Frame(root)
        GoButton.pack(side=BOTTOM)

        Labelrot = Label(topLabel, text="Rotation angle")
        Labelrot.pack()
        self.r90 = Button(RotButtons, text="90", command=self.rotation_angle90)
        self.r90.pack(side=LEFT)

        self.r180 = Button(RotButtons, text="180", command=self.rotation_angle180)  
        self.r180.pack(side=LEFT)

        self.r270 = Button(RotButtons, text="270", command=self.rotation_angle270)
        self.r270.pack(side=LEFT)

        self.r360 = Button(RotButtons, text="360", command=self.rotation_angle360)
        self.r360.pack(side=LEFT)

        Labelrot = Label(ResLabel, text="Rotational Resolution")
        Labelrot.pack()
        
        self.res03 = Button(ResButtons, text="0.3 Deg", command=self.resolution03)
        self.res03.pack(side=LEFT)

        self.res06 = Button(ResButtons, text="0.6 Deg", command=self.resolution06)
        self.res06.pack(side=LEFT)

        self.res12 = Button(ResButtons, text="1.2 Deg", command=self.resolution12)
        self.res12.pack(side=LEFT)

        CamLabel = Label(CamResLabel, text="Camera Resolution")
        CamLabel.pack()

        self.camresmax = Button(CamResButtons, text="3280x2464 (Maximum)", command=self.camresmax)
        self.camresmax.pack(side=LEFT)

        self.camresmed = Button(CamResButtons, text="1920x1442 (Medium)", command=self.camresmed)
        self.camresmed.pack(side=LEFT)

        self.camreslow = Button(CamResButtons, text="1080x811 (Low)", command=self.camreslow)
        self.camreslow.pack(side=LEFT)

        self.calibbutton=Button(CalibButton, text="Calibrate Y Axis", command=self.ycalibrate)
        self.calibbutton.pack(side=LEFT)


        self.startscan = Button(GoButton, text="Start Scan with applied settings")
        self.startscan["command"] = self.startscanning
        #self.startscan["command"] = self.readimages
        #self.startscan["command"] = self.calculatepoints
        self.startscan.pack(side=LEFT)

        self.startscanfull=Button(GoButton, text="Start Full Vertical Scan with applied settings")
        self.startscanfull["command"] = self.startscanningfull
        self.startscanfull.pack(side=LEFT)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
root = Tk()
app = Application(master=root)
app.mainloop()




