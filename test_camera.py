from picamera import PiCamera

camera = PiCamera()
try:
    camera.resolution = (2592, 1944 )
    for i in range(10):

        camera.capture('/home/claudipi/Bilder/image%s.jpg' % i)
finally:
    camera.close()