from camera_stream import CCameraStream
import cv2 as cv
import time


CamStream = CCameraStream(res=(1280, 720), fps=10)
CamStream.run()

time.sleep(3)

while True:
    img = CamStream.get()
    cv.namedWindow("window", cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty("window",
                         cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    cv.imshow("window", img)

    key = cv.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break


CamStream.stop()
