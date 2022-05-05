from time import sleep
from picamera import PiCamera

camera = PiCamera()
try:
    camera.resolution = (2592, 1944 )
    sleep(1)
    for i in range(10):

        camera.capture_continuous('/home/claudipi/Bilder/image%s.jpg' % i)
finally:
    camera.close()