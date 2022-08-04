from threading import Thread
import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera

class CameraStream:
    """Camera Stream"""
    def __init__(self, res=(640,480), fps=30):
        self.camera = PiCamera()
        self.camera.resolution = res
        self.camera.framerate = fps
        self.raw_capture = PiRGBArray(self.camera,size=res)
        self.stream = self.camera.capture_continuous(
            self.raw_capture, format = "bgr", use_video_port = True)

        # Init variable to buffer camera frame
        self.recent_frame = []

        self.running = False

    def start_stream(self):
        """Start Stream as Thread"""
        self.running  = True
        Thread(target=self.__update,args=()).start()

    def __update(self):
        """Update frame buffer"""
        for frame in self.stream:
            if self.running:
                self.recent_frame = frame.array
                self.raw_capture.truncate(0)
            else:
                # Close camera resources
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()

    def get(self):
        """Return recent frame"""
        return self.recent_frame

    def stop(self):
        """Stop CameraStream"""
        self.running = False