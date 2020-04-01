import time
import picamera
import numpy as np
import cv2
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