#!/usr/bin/python3
print ("Loading...")
from tkinter import *
from gpiozero import LED
import cv2 as cv
import numpy as np
import math
import time
from picamera import PiCamera
import os
import sys
import serial
ser=serial.Serial('/dev/ttyS0',9600)#
ser.flushInput()
global strrotate
global strenable
global strmicrosteps
global strencoderres
global strencoderread
strenable='e1'
strmicrosteps='m8'
strencoderres='z'
strencoderread='n'


photographs=0
revolutions=0
camangle1 = (25.72/(180/math.pi))
camangled1=(56.81/(180/math.pi))
Bconst1 = (77.14/(180/math.pi))
cosB1 = math.cos(Bconst1)
camangle2 = (79.06/(180/math.pi))
camangled2=(8.36/(180/math.pi))
Bconst2 = (85.82/(180/math.pi))
cosB2 = math.cos(Bconst2)
cselect=LED(24)
cenable1=LED(23)
cenable2=LED(18)
laser=LED(13)
i2c='i2cset -y 1 0x70 0x00 0x04'
os.system(i2c)
cselect.off()
cenable1.off()
cenable2.on()
laser.off()
camera=PiCamera()
camera.resolution=(3280,2464)

maxvalue=[]

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
cam2out=[]
cam2outplusx=[]
cam2outminusx=[]
cam2outplusy=[]
cam2outminusy=[]
rone=[]
rtwo=[]


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
        scanres=1
        self.res03["fg"]="red"
        self.res06["fg"]="black"
        self.res12["fg"]="black"

    def resolution06(self):
        global scanres        
        scanres=0.5
        self.res03["fg"]="black"
        self.res06["fg"]="red"
        self.res12["fg"]="black"

    def resolution12(self):
        global scanres
        scanres=0.25
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

    def startscanning(self):
        ser.write(strenable.encode('utf-8'))
        ser.write(strencoderres.encode('utf-8'))
        
        global yresolution
        yresolution=int(xresolution/(3280/2464))
        global adjforz1
        adjforz1=((yresolution/2)/(math.tan((19.43/2)/(180/math.pi))))
        global adjforz2
        adjforz2=((yresolution/2)/(math.tan((6.278/2)/(180/math.pi))))
        scanresz=1
        global threshinput
        threshinput=0.2
        global radius
        radius=5
        global aconst1
        aconst1 = (xresolution*(math.sin(Bconst1)))/(math.sin(camangle1))
        global aconstsqrd1
        aconstsqrd1 = math.pow(aconst1,2)
        global aconst2
        aconst2 = (xresolution*(math.sin(Bconst2)))/(math.sin(camangle2))
        global aconstsqrd2
        aconstsqrd2 = math.pow(aconst2,2)
        r=0
        
        global scansteps
        scansteps = round((scanangle/6.28)/scanres)
        with PiCamera() as camera:
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
                cselect.off()
                cenable1.off()
                cenable2.on()
                i2c='i2cset -y 1 0x70 0x00 0x04'
                os.system(i2c)
                expt=camera.exposure_speed
                if expt < 4000:
                    camera.shutter_speed=4000
                else:
                    camera.shutter_speed=0
                camera.awb_gains=(0,0)
                revnumstr=str(revolutions)
                loffname='1loff' + revnumstr + '.jpg'
                camera.capture(loffname,'jpeg',use_video_port=True)
                lonname='1lon' + revnumstr + '.jpg'
                laser.on()
                camera.awb_gains=(8,0)
                camera.capture(lonname,'jpeg',use_video_port=True)
                camera.shutter_speed=0
                laser.off()
                cselect.off()
                cenable1.on()
                cenable2.off()
                i2c='i2cset -y 1 0x70 0x00 0x06'
                os.system(i2c)
                expt=camera.exposure_speed
                if expt < 4000:
                    camera.shutter_speed=4000
                else:
                    camera.shutter_speed=0
                camera.awb_gains=(0,0)
                revnumstr=str(revolutions)
                loffname='2loff' + revnumstr + '.jpg'
                camera.capture(loffname,'jpeg',use_video_port=True)
                lonname='2lon' + revnumstr + '.jpg'
                laser.on()
                camera.awb_gains=(8,0)
                camera.capture(lonname,'jpeg',use_video_port=True)
                camera.shutter_speed=0
                laser.off()
                strrotate='c'+ (6.28*scanres)
                ser.write(strrotate.encode('utf-8'))
                time.sleep(1)
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
        
    
        
    def saveoutput(self):
        fileoutput = "Example.pts"
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
            loffname1='1loff' + pnumstr + '.jpg'
            lonname1='1lon'+pnumstr + '.jpg'
            loffname2='2loff' + pnumstr + '.jpg'
            lonname2='2lon'+pnumstr + '.jpg'
            loff1=cv.imread(loffname1)
            lon1=cv.imread(lonname1)
            src1=cv.subtract(lon1,loff1)
            loff2=cv.imread(loffname2)
            lon2=cv.imread(lonname2)
            src2=cv.subtract(lon2,loff2)
            red1=cv.cvtColor(src1,cv.COLOR_BGR2GRAY)
            blur1=cv.GaussianBlur(red1,(5,5),0)
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur1)
            threshamount = maxVal*threshinput
            retval, threshold = cv.threshold(red1, threshamount, 255, cv.THRESH_TOZERO);
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(threshold)
            maxvalue1 = np.argmax(threshold,axis=1)
            os.remove(loffname1)
            os.remove(lonname1)
            succesful=0
            for i in range(yresolution):
                xcolumn=maxvalue1[i]
                pxminus=threshold[i,((maxvalue1[i])-1)]
                if i > 0:
                    pyminus=threshold[(i-1),(maxvalue1[i])]
                else:
                    pyminus=threshold[i,(maxvalue1[i])]
                if i == (yresolution-1):
                    pyplus=threshold[i,(maxvalue1[i])]
                else:
                    pyplus=threshold[(i+1),(maxvalue1[i])]
                if xcolumn < (xresolution-1):
                    pxadd=threshold[i,((maxvalue1[i])+1)]
                else:
                    pxadd=threshold[i,((maxvalue1[i]))]
                if xcolumn > 0 and pxminus !=0 and pxadd !=0 and pyplus!=0 and pyminus !=0:
                    cam1out.append(xcolumn)
                    succesful=succesful+1
                    
            numlines.append(succesful)
            red2=cv.cvtColor(src2,cv.COLOR_BGR2GRAY)
            blur2=cv.GaussianBlur(red2,(5,5),0)
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur2)
            threshamount = maxVal*threshinput
            retval, threshold = cv.threshold(red2, threshamount, 255, cv.THRESH_TOZERO);
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(threshold)
            maxvalue2 = np.argmax(threshold,axis=1)
            os.remove(loffname2)
            os.remove(lonname2)
            succesful=0
            for i in range(yresolution):
                xcolumn=maxvalue2[i]
                pxminus=threshold[i,((maxvalue2[i])-1)]
                if i > 0:
                    pyminus=threshold[(i-1),(maxvalue2[i])]
                else:
                    pyminus=threshold[i,(maxvalue2[i])]
                if i == (yresolution-1):
                    pyplus=threshold[i,(maxvalue2[i])]
                else:
                    pyplus=threshold[(i+1),(maxvalue2[i])]
                if xcolumn < (xresolution-1):
                    pxadd=threshold[i,((maxvalue2[i])+1)]
                else:
                    pxadd=threshold[i,((maxvalue2[i]))]
                if xcolumn > 0 and pxminus !=0 and pxadd !=0 and pyplus!=0 and pyminus !=0:
                    cam2out.append(xcolumn)
                    succesful=succesful+1
                    
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
                cosC=((2*aconstsqrd)-(2*aconst*(xcolumn+1)*cosB1))/((2*aconst*(math.sqrt((aconstsqrd+((xcolumn+1)*(xcolumn+1))-(2*aconst*(xcolumn+1)*cosB1))))))
                angle=math.acos(cosC)
                totalangle=angle+camangled1
                oppcalc=327*(math.tan(totalangle))
                hypcalc=math.hypot(oppcalc,200)
                calc2=math.asin(oppcalc/hypcalc)
                rrad= rone[calculations]
                rz=rtwo[calculations]
                rcalc = calc2 + rrad
                if hypcalc < 10000:
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
        
        self.res03 = Button(ResButtons, text="1 Pass", command=self.resolution03)
        self.res03.pack(side=LEFT)

        self.res06 = Button(ResButtons, text="2 Pass", command=self.resolution06)
        self.res06.pack(side=LEFT)

        self.res12 = Button(ResButtons, text="3 Pass", command=self.resolution12)
        self.res12.pack(side=LEFT)

        CamLabel = Label(CamResLabel, text="Camera Resolution")
        CamLabel.pack()

        self.camresmax = Button(CamResButtons, text="3280x2464 (Maximum)", command=self.camresmax)
        self.camresmax.pack(side=LEFT)

        self.camresmed = Button(CamResButtons, text="1920x1442 (Medium)", command=self.camresmed)
        self.camresmed.pack(side=LEFT)

        self.camreslow = Button(CamResButtons, text="1080x811 (Low)", command=self.camreslow)
        self.camreslow.pack(side=LEFT)

        self.startscan = Button(GoButton, text="Start Scan with applied settings")
        self.startscan["command"] = self.startscanning
        #self.startscan["command"] = self.readimages
        #self.startscan["command"] = self.calculatepoints
        self.startscan.pack(side=LEFT)


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
root = Tk()
app = Application(master=root)
app.mainloop()




