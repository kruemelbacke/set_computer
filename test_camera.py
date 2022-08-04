from camera_stream import CameraStream
import cv2 as cv
import time


CamStream = CameraStream(res=(1280, 720), fps=10)
CamStream.start_stream()

time.sleep(3)

while True:
    img = CamStream.get()
    cv.imshow('Camera Test', img)

    key = cv.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    time.sleep(1)
