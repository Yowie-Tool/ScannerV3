#!/usr/bin/python3
import smbus
import math
import statistics
import time
 
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
def dist(a,b):
    return math.sqrt((a*a)+(b*b))
 
def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
 
bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x69       # via i2cdetect
 
bus.write_byte_data(address, power_mgmt_1, 0)

sampleno=100

xcalib=input("input X Calibration value: ")
xcalib=float(xcalib)
ycalib=input("input Y Calibration value: ")
ycalib=float(ycalib)
timeoftest=input("Input test length (seconds): ")
timeoftest=int(timeoftest)

for inttime in range(timeoftest):
    xrot=[]
    yrot=[]

    for int in range(sampleno):
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)
        xrot.append(get_x_rotation(accel_xout, accel_yout, accel_zout))
        yrot.append(get_y_rotation(accel_xout, accel_yout, accel_zout))
 
    xrotation = statistics.median(xrot)
    xrotation = round(xrotation,2)
    xrotation=xrotation+xcalib
    yrotation = statistics.median(yrot)
    yrotation = round(yrotation,2)
    yrotation=yrotation+ycalib   
    print("X rotation %f Y Rotation %f \r"%(xrotation,yrotation),end="")
    time.sleep(1)

print("End of test")    