import time
import picamera
import numpy as np
import cv2
from gpiozero import LED
import os
cselect=LED(4)
cenable1=LED(17)
cenable2=LED(18)
laser=LED(20)
i2c='i2cset -y 1 0x70 0x00 0x04'
os.system(i2c)
cselect.off()
cenable1.off()
cenable2.on()
with picamera.PiCamera() as camera:
    camera.resolution = (3280,2464)
    camera.framerate = 24
    time.sleep(2)
    image = np.empty((2464 * 3280 * 3,), dtype=np.uint8)
    starttime=time.time()
    camera.capture(image, 'bgr')
    image = image.reshape((2464, 3280, 3))
    endtime=time.time()
    cv2.imwrite("cvwrite.jpg",image)
    timetaken=endtime-starttime
    print ("time taken to capture image %d seconds"%timetaken)