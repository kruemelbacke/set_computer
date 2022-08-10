import time
import cv2 as cv

from card_detection import CCardDetector

###########################################
TARGET = False
# Possible: True or False
# True: running on Raspberry Pi with Camera
# False:running on Host loading local image
###########################################

if TARGET:
    from camera_stream import CCameraStream
    WIN_FLATTEN_W = 50
    WIN_FLATTEN_H = 75

    WIN_BIG_W = 600
    WIN_BIG_H = 360
else:
    IMG_PATH = "Imgs/2022-08-05_11-16-12.png"
    WIN_FLATTEN_W = 200
    WIN_FLATTEN_H = 300

    WIN_BIG_W = 1280
    WIN_BIG_H = 720


if __name__ == '__main__':
    if TARGET:
        CamStream = CCameraStream(res=(1280, 720), fps=10)
        CamStream.run()

    CardDetector = CCardDetector()

    while True:
        if TARGET:
            img_raw = CamStream.get()
        else:
            img_raw = cv.imread(IMG_PATH)

        Cards = CardDetector.get_cards_from_img(img_raw)

        # Show Card Detection
        result_img = CardDetector.get_result_img()
        cv.imshow("CardDetection", cv.resize(result_img, (WIN_BIG_W, WIN_BIG_H)))

        img_flatten, img_flatten_thresh, img_symbol_mask = \
            CardDetector.get_flatten_imgs(WIN_FLATTEN_W, WIN_FLATTEN_H)

        cv.imshow("FlattenCards", img_flatten)
        cv.imshow("FlattenCards Thresh", img_flatten_thresh)
        cv.imshow("FlattenCards Masked", img_symbol_mask)

        if TARGET:
            key = cv.waitKey(1) & 0xFF

            # if `q` key was pressed, break from the loop
            if key == ord("q"):
                CamStream.stop()
                break
        else:
            cv.waitKey(0)
            break

