#!/usr/bin/python3

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
#
ser=serial.Serial('/dev/ttyAMA0',9600)
#Maybe we should add in some extra lines here to clear it as we found it didn't communicate immediately
ser.flushInput()
ser.write(('e1/n').encode('utf-8')) #Enables the stepper motor driver, turns out the program light.
ser.write(('z/n').encode('utf-8')) #Zeroes the encoder in the stepper

photographs=0
revolutions=0
camangle1 = (25.72/(180/math.pi)) #camera 1 Horizontal field of view
camangled1=(56.81/(180/math.pi)) #camera 1 mounting angle (mounting angle - 1/2 horizontal field of view)
Bconst1 = (77.14/(180/math.pi)) #ABC triangle constant value, 180 - camera horizontal field of view / 2
cosB1 = math.cos(Bconst1)
camangle2 = (79.06/(180/math.pi)) #as above
camangled2=(8.36/(180/math.pi))
Bconst2 = (85.82/(180/math.pi))
cosB2 = math.cos(Bconst2)
cselect=LED(24) #select pin on arducam camera switcher
cenable1=LED(23) #enable pin 1 on arducam camera switcher
cenable2=LED(18) #enable pin 2 on arducam camera switcher
laser=LED(13) #temporary laser pin - doesn't currently work?
i2c='i2cset -y 1 0x70 0x00 0x04' #camera 1 i2c address on arducam camera switcher
os.system(i2c) #writes it
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
    #Tkinter existing GUI. clunky and nasty looking, but does the job.
    #Scan angle buttons will remain in new version.
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
        #This and the camera resolution will be incorporated into the new GUI - scanres would be the overscan/passes, resolution being the camera resoltuion
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
        
    def camera1():
        #arducam camera switching
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

    def startscanning(self):
        
        global yresolution
        #calculates camera y resoltuion based on xresolution from GUI selection. 
        yresolution=int(xresolution/(3280/2464))
        global adjforz1
        #camera 1 vertical FOV
        adjforz1=((yresolution/2)/(math.tan((19.43/2)/(180/math.pi))))
        global adjforz2
        adjforz2=((yresolution/2)/(math.tan((6.278/2)/(180/math.pi))))
        scanresz=1
        global threshinput
        #threshold is up to 1, which is proportion of maximum value in array, to get rid of random points
        threshinput=0.2
        global radius
        #averages maximum value over 5 pixels, to stop maximum value being an anomaly
        radius=5
        global aconst1
        #constant value in abc triangle where c is xresolution
        aconst1 = (xresolution*(math.sin(Bconst1)))/(math.sin(camangle1))
        global aconstsqrd1
        #aconst squared
        aconstsqrd1 = math.pow(aconst1,2)
        global aconst2
        aconst2 = (xresolution*(math.sin(Bconst2)))/(math.sin(camangle2))
        global aconstsqrd2
        aconstsqrd2 = math.pow(aconst2,2)
        r=0
        
        global scansteps
        scansteps = round((scanangle/6.28)/scanres)
        #calculates number of photo sets, 6.28 being the horizontal field of view of the second camera.
        with PiCamera() as camera:
            camera.start_preview(fullscreen=False,window=(200,80,600,400))
            #"wakes up" the camera currently selected and displays a window overlay of the live image
            camera.resolution=(xresolution,yresolution)
            #sets camera resolution (NOT the same as the preview window)
            camera.meter_mode='backlit'
            #wide light metering for the camera
            camera.saturation=50
            #upping the saturation of the image - might not need to do with the IR Laser.
            time.sleep(2)
            #pause for 2 seconds to allow the camera to adjust
            print ("Scan start")
            scanstarttime=time.time()
            global revolutions
            for revolutions in range(scansteps):
                self.camera1()
                #select camera1
                scanstepsstring=str(revolutions)
                expt=camera.exposure_speed
                #query exposure speed from camera
                if expt < 4000:
                    camera.shutter_speed=4000
                    #sets shutter speed to maximum (minimum speed)
                else:
                    camera.shutter_speed=0
                    #doesn't override
                camera.awb_gains=(0,0)
                #sets white balance to normal - may change this as we are not interested in the RGB values in 2D scanning
                revnumstr=str(revolutions)
                loffname='1loff' + revnumstr + '.jpg'
                #names the image files saved to the SD card so they can be read in sequence
                camera.capture(loffname,'jpeg',use_video_port=True)
                lonname='1lon' + revnumstr + '.jpg'
                laser.on()
                #turn laser on....
                camera.awb_gains=(8,0)
                #sets white balance to enhance red - may alter this as IR appears to be in the blue channel
                camera.capture(lonname,'jpeg',use_video_port=True)
                #takes a photo
                camera.shutter_speed=0
                #returns the camera to being able to choose it's own shutter speed, the idea being both images are taken at the same shutter speeds
                self.camera2()
                #same as before, but for camera 2
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
                #now rotate the unit - 30 is the gear ratio
                strrotate='c'+ (6.28*scanres*30)+'\n'
                ser.write(strrotate.encode('utf-8'))
                time.sleep(1)
                #assuming the rotation will take about 1 second... eventually we want it to just wait for a signal from the stepper that it's fully moved
                if revolutions != 0:
                    rone.append((revolutions)/(180/math.pi))
                else:
                    rone.append(0)
                #makes an array of how far we've moved each time, to use in the calculations later
                rtwo.append(0)
                #think we don't need this, this is for the 3d scan, will double check.
        global scanendtime
        scanendtime=time.time()
        camera.close
        #shuts the camera off
        print("Photographic scan completed in %f seconds" % (int(scanendtime-scanstarttime)))
        self.readimages()
        
    
        
    def saveoutput(self):
        fileoutput = "RoomReaderScan.pts"
        #currently only one file name. 
        fileoutputtype = "w"
        file_object = open(fileoutput,fileoutputtype)

        print ("Scan ended, saving")
        exportint = len(xdist)
        #currently based on length of x array. Will change to a 2D or 3D array at some point to make the array smaller, as won't have to include 0 values.
    
        for export in range (exportint):
            #I've deleted Z and RGB from this now. exports just a text file with X,Y coordinates
            xout = str(xdist[export])
            yout = str(ydist[export])
            file_object.write(xout + " " + yout + "\n")

        file_object.close()
        
        saveendtime=time.time()
        print("File outputted in %f seconds" % (int(saveendtime-calculateendtime)))
        sys.exit()

    def readimages(self):
        
        for photographs in range(scansteps):
            pnumstr=str(photographs)
            loffname1='1loff' + pnumstr + '.jpg'
            lonname1='1lon'+pnumstr + '.jpg'
            loffname2='2loff' + pnumstr + '.jpg'
            lonname2='2lon'+pnumstr + '.jpg'
            #There is a way of taking photo's directly into opencv as an array, but previous attempts at this have been unsuccesful, it seems this only works at low resolutions.
            loff1=cv.imread(loffname1)
            lon1=cv.imread(lonname1)
            src1=cv.subtract(lon1,loff1)
            #subtract the laser on image from the laser off image. In theory, when we lock down the camera settings between the two photos, we should end up with just the laser line left. In practice, there is extra interference involved. 
            loff2=cv.imread(loffname2)
            lon2=cv.imread(lonname2)
            src2=cv.subtract(lon2,loff2)
            red1=cv.cvtColor(src1,cv.COLOR_BGR2GRAY)
            #extract just the red array, used with the visible laser. When we switch to IR, we might change to another channel.
            blur1=cv.GaussianBlur(red1,(5,5),0)
            #create a blurred image to find the maximum value from. This means that any anomalies are removed
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(blur1)
            #find the location of minimum and maximum values in the image
            threshamount = maxVal*threshinput
            #create a value that will remove any values below that, which is a proportion of the maximum value
            retval, threshold = cv.threshold(red1, threshamount, 255, cv.THRESH_TOZERO);
            #this then removes those from the image
            (minVal, maxVal, MinLoc, maxLoc) = cv.minMaxLoc(threshold)
            #find the maximum value of the non blurred image
            maxvalue1 = np.argmax(threshold,axis=1)
            #Now find the maximum value in each column. We will change this to the mean value of the gaussian curve, to try and get the best fit for the laser line, which has gaussian distribution
            os.remove(loffname1)
            os.remove(lonname1)
            #Delete the image files, to save space
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
                    #This checks that where the maximum value is, there are other bright pixels around it, which we can hopefully get rid of when we move to the alternative method of laser line centre calculation
                    cam1out.append(xcolumn)
                    succesful=succesful+1
                    
            numlines.append(succesful)
            #This is just for the users benefit, shows how many points the unit has captured succefully
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
            #And then do it all again for camera 2
                
        global readimageendtime
        readimageendtime=time.time()
        print("Images read in %f seconds" % (int(readimageendtime-scanendtime)))
        self.calculatepoints()
                

    def calculatepoints(self):
        #Ok, this bit needs updating, it's currently for the 3d version which rotated around an axis which was between the camera and the laser
        tlines=0
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




