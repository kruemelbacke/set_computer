import cv2 as cv
import numpy as np

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
    IMG_PATH = "Imgs/2022-08-11_14-42-08.png"
    WIN_FLATTEN_W = 200
    WIN_FLATTEN_H = 300

    WIN_BIG_W = 1280
    WIN_BIG_H = 720

FONT = cv.FONT_HERSHEY_SIMPLEX


def show_results(raw: list, qcards: list):
    """Draw the card name, center point, and contour on the camera img_raw."""

    # Draw card contours on image (have to do contours all at once or
    # they do not show up properly for some reason)
    if len(qcards) > 0:
        temp_cnts = []
        for qcard in qcards:
            temp_cnts.append(qcard.contour)
        cv.drawContours(raw,temp_cnts, -1, (0,0,0), 3)
        cv.drawContours(raw,temp_cnts, -1, (0,255,0), 2)

    for qcard in qcards:
        x = qcard.center[0]
        y = qcard.center[1]
        cv.circle(raw, (x, y), 5, (0, 255, 0), -1)

        put_text_centered(raw, f"{qcard.get_number()}", x, y-40)
        put_text_centered(raw, f"{qcard.get_symbol()}", x, y-10)
        put_text_centered(raw, f"{qcard.get_color()}", x, y+20)
        put_text_centered(raw, f"{qcard.get_shading()}", x, y+50)

    cv.putText(raw, (f"Detected Cards: {len(qcards)}"),
            (3, 24), FONT, 1, (255, 255, 0), 2, cv.LINE_AA)

    cv.imshow("CardDetection", cv.resize(img_raw, (WIN_BIG_W, WIN_BIG_H)))


def show_flatten_cards(qcards: list):
    """Draw contour and mask"""


def show_img_from_cards(qcards: list, img_name: str):
    imgs = get_img_from_cards(qcards, img_name)

    if len(qcards) == 1:
        cv.imshow(img_name, imgs[0])

    if len(qcards) > 1:
        cv.imshow(img_name, np.hstack(imgs))


def get_img_from_cards(qcards: list, img_name: str):
    img_list = []
    for card in qcards:
        img_list.append(cv.resize(getattr(card, img_name), (WIN_FLATTEN_W, WIN_FLATTEN_H)))
    return tuple(img_list)

def put_text_centered(img, text, center_x, center_y):
    """Put text into the given img centered to given x and y coordinates"""
    # get boundary of the text
    textsize = cv.getTextSize(text, FONT, 1, 2)[0]

    # get coords based on boundary
    textX = int(center_x - textsize[0] / 2)
    textY = int(center_y + textsize[1] / 2)

    # Draw text twice, so letters have black outline
    cv.putText(img, (text),
        (textX, textY-10), FONT, 1, (0, 0, 0), 3, cv.LINE_AA)
    cv.putText(img, (text),
        (textX, textY-10), FONT, 1, (50, 200, 200), 2, cv.LINE_AA)


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
        show_results(img_raw, Cards)

        show_img_from_cards(Cards, "warp_symbol_center_boxes")

        # show_img_from_cards([Cards[0]], "warp")
        # show_img_from_cards([Cards[0]], "warp_grey")
        # show_img_from_cards([Cards[0]], "warp_thresh")
        # show_img_from_cards([Cards[0]], "symbol_mask")
        # show_img_from_cards([Cards[0]], "warp_white_balanced")

        if TARGET:
            key = cv.waitKey(1) & 0xFF

            # if `q` key was pressed, break from the loop
            if key == ord("q"):
                CamStream.stop()
                break
        else:
            cv.waitKey(0)
            break

