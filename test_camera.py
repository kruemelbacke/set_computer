from camera_stream import CameraStream
import cv2 as cv


CamStream = CameraStream(res=(1280, 720), fps=10)
CamStream.start_stream()

while True:
    img = CamStream.get()
    cv.imshow(img)
