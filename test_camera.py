from picamera import PiCamera

camera = PiCamera()
camera.resolution = (2592, 1944 )
for i in range(10):

    camera.capture('/home/pi/Desktop/image%s.jpg' % i)