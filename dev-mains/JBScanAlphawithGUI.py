#!/usr/bin/python3
from tkinter import *
import cv2 as cv
import numpy as np
import math
from nanpy import (ArduinoApi, SerialManager)
import time
import picamera
import picamera.array

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

    def startscan(self):
        fileoutput = "Example.pts"
        fileoutput = '/media/pi/usbdrive/' + fileoutput
        fileoutputtype = "w"
        yresolution=int(xresolution/(3280/2464))
        adjforz=((yresolution/2)/(math.tan((24.4)/(180/math.pi))))
        scanresz=1
        threshinput=0.2
        radius=5
        aconst = (xresolution*(math.sin(Bconst)))/(math.sin(camangle))
        aconstsqrd = math.pow(aconst,2)
        r=0
        file_object = open(fileoutput,fileoutputtype)
        scansteps = round(scanangle/scanres)
        with picamera.PiCamera() as camera:
            camera.start_preview(fullscreen=False,window=(0,0,640,480))
            camera.resolution=(xresolution,yresolution)
            camera.meter_mode='backlit'
            camera.saturation=50
            time.sleep(2)
            print ("Scan start")
            starttime=time.time()
            for revolutions in range(scansteps):
                scanstepsstring=str(revolutions)
                expt=camera.exposure_speed
                if expt < 4000:
                    camera.shutter_speed=4000
                else:
                    camera.shutter_speed=0
                camera.awb_gains=(0,0)
                camera.capture('loff.jpg','jpeg',use_video_port=True)
                loff = cv.imread('loff.jpg')
                a.digitalWrite(lsrctrl, a.HIGH)
                camera.awb_gains=(8,0)
                camera.capture('lon.jpg','jpeg',use_video_port=True)
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
                lon = cv.imread('lon.jpg')
                a.digitalWrite(lsrctrl, a.LOW)
                src=cv.subtract(lon,loff)
                red=cv.cvtColor(src,cv.COLOR_BGR2GRAY)
                ysize = red.shape[0]
                xsize = red.shape[1]
                blur=cv.GaussianBlur(red,(radius,radius),0)
                (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur)
                threshamount = maxVal*threshinput
                retval, threshold = cv.threshold(red, threshamount, 255, cv.THRESH_TOZERO);
                (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(threshold)
                maxvalue = np.argmax(threshold,axis=1)
                yint=0
                yav=0
                xav=0
                angleav=0
                ynum=0
                hypav=0
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
                        cosC=((2*aconstsqrd)-(2*aconst*(xcolumn+1)*cosB))/((2*aconst*(math.sqrt((aconstsqrd+((xcolumn+1)*(xcolumn+1))-(2*aconst*(xcolumn+1)*cosB))))))
                        angle=math.acos(cosC)
                        totalangle=angle+camangled
                        oppcalc=400*(math.tan(totalangle))
                        hypcalc=math.hypot(oppcalc,200)
                        calc2=math.asin(oppcalc/hypcalc)
                        rrad= r/(180/math.pi)
                        rcalc = calc2 + rrad
                        if hypcalc < 10000:
                            redp=loff[yint,xcolumn,2]
                            rpix.append(redp)
                            greenp=loff[yint,xcolumn,1]
                            gpix.append(greenp)
                            bluep=loff[yint,xcolumn,0]
                            bpix.append(bluep)
                            xdistance = -(hypcalc*(math.cos(rcalc)))
                            xdistance = round(xdistance,1)
                            ydistance = hypcalc*(math.sin(rcalc))
                            ydistance = round(ydistance,1)
                            ydist.append(ydistance)
                            xdist.append(xdistance)
                            if yint > (ysize/2):
                                angle = math.atan(((yint+1)-(yresolution/2))/adjforz)
                                tancalc=-(oppcalc*(math.tan(angle)))
                            else:
                                angle = math.atan(((yresolution/2)-(yint+1))/adjforz)
                                tancalc=(oppcalc*(math.tan(angle)))
                            tancalc = round(tancalc, 1)
                            zdist.append(tancalc)
                            yav=yav+ydistance
                            xav=xav+xdistance
                            ynum=ynum+1
                            hypav=hypav+hypcalc
                            angleav=angleav+calc2
                    yint=yint+1
        
                r=r+scanres
                if ynum >0:
                    yav=yav/ynum
                    xav=xav/ynum
                    hypav=hypav/ynum
                    angleav=angleav/ynum
                    rshort=round(r,1)
                    yav=round(yav,1)
                    xav=round(xav,1)
                    hypav=round(hypav,1)
                    angleav=angleav*(180/math.pi)
                    angleav=round(angleav,1)
                else:
                    yav=0
                    xav=0
                    hypav=0
                    angleav=0
                print ('Current angle: [%f] Av Distance [%f] at angle [%f] points rec: [%d] Average X: [%f] Y: [%f]\r'%(rshort,hypav,angleav,ynum,xav,yav),end="")
        print ("Scan ended, saving")
        endtime=time.time()
        print("Completed in: %f minutes" % (int((endtime-starttime)/60)))
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
        camera.close

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


        self.startscan = Button(GoButton, text="Start Scan with applied settings", command=self.startscan)
        self.startscan.pack(side=LEFT)        
        

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
root = Tk()
app = Application(master=root)
app.mainloop()




