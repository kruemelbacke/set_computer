import cv2 as cv
import numpy as np
import set_engine

from card_detection import CCardDetector

###########################################
TARGET = True
FULLSCREEN = True
GAMEMODE = False
# Possible: True or False
# True: running on Raspberry Pi with Camera
# False:running on Host loading local image
###########################################

if TARGET:
    from camera_stream import CCameraStream
    WIN_FLATTEN_W = 80
    WIN_FLATTEN_H = 120

    WIN_BIG_W = 600
    WIN_BIG_H = 360
else:
    IMG_PATH = "Imgs/2022-08-11_14-42-08.png"
    WIN_FLATTEN_W = 200
    WIN_FLATTEN_H = 300

    WIN_BIG_W = 1280
    WIN_BIG_H = 720

if FULLSCREEN:
    WIN_FLATTEN_W = 100
    WIN_FLATTEN_H = 150

    WIN_BIG_W = 800
    WIN_BIG_H = 480


FONT = cv.FONT_HERSHEY_SIMPLEX

def draw_card_contours(raw: list, qcards: list, color: tuple):
    # Draw card contours on image (have to do contours all at once or
    # they do not show up properly for some reason)
    if len(qcards) > 0:
        temp_cnts = []
        for qcard in qcards:
            temp_cnts.append(qcard.contour)
        cv.drawContours(raw,temp_cnts, -1, (0,0,0), 3)
        cv.drawContours(raw,temp_cnts, -1, color, 2)

def draw_num_of_cards(raw, qcards):
    cv.putText(raw, (f"Detected Cards: {len(qcards)}"),
            (3, 24), FONT, 1, (255, 255, 0), 2, cv.LINE_AA)


def draw_attributes(raw: list, qcards: list):
    """Draw the card name, center point, and contour on the camera img_raw."""

    for qcard in qcards:
        x = qcard.center[0]
        y = qcard.center[1]

    #     cv.circle(raw, (x, y), 5, (0, 255, 0), -1)

        put_text_centered(raw, f"{qcard.get_number()}", x, y-40)
        put_text_centered(raw, f"{qcard.get_symbol()}", x, y-10)
        put_text_centered(raw, f"{qcard.get_color()}", x, y+20)
        put_text_centered(raw, f"{qcard.get_shading()}", x, y+50)

    cv.putText(raw, (f"Detected Cards: {len(qcards)}"),
            (3, 24), FONT, 1, (255, 255, 0), 2, cv.LINE_AA)


def show_img_from_cards(qcards: list, img_name: str, win_name: str):
    imgs = get_img_from_cards(qcards, img_name)

    if len(qcards) == 1:
        cv.imshow(win_name, imgs[0])

    if len(qcards) > 1:
        cv.imshow(win_name, np.hstack(imgs))


def get_img_from_cards(qcards: list, img_name: str):
    img_list = []
    for card in qcards:
        img_list.append(cv.resize(getattr(card, img_name), (WIN_FLATTEN_W, WIN_FLATTEN_H)))
    return tuple(img_list)


def put_text_centered(img, text, center_x, center_y, size=1):
    """Put text into the given img centered to given x and y coordinates"""
    # get boundary of the text
    textsize = cv.getTextSize(text, FONT, 1, 2)[0]

    # get coords based on boundary
    textX = int(center_x - textsize[0] / 2)
    textY = int(center_y + textsize[1] / 2)

    # Draw text twice, so letters have black outline
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (0, 0, 0), 3, cv.LINE_AA)
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (50, 200, 200), 2, cv.LINE_AA)


def put_text(img, text, textX, textY, size=1):
    """Put text into the given img centered to given x and y coordinates"""
    # get boundary of the text
    textsize = cv.getTextSize(text, FONT, 1, 2)[0]

    # Draw text twice, so letters have black outline
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (0, 0, 0), 3, cv.LINE_AA)
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (0, 255, 0), 2, cv.LINE_AA)


if __name__ == '__main__':
    if TARGET:
        CamStream = CCameraStream(res=(1280, 720), fps=10)
        CamStream.run()

    CardDetector = CCardDetector()

    set_counter = 0
    while True:
        if TARGET:
            img_raw = CamStream.get()
        else:
            img_raw = cv.imread(IMG_PATH)

        Cards = CardDetector.get_cards_from_img(img_raw)
        draw_card_contours(img_raw, Cards, (0, 0, 255))
        draw_attributes(img_raw, Cards)

        set_cards = set_engine.find_set_primitive_loop(Cards)

        if len(set_cards) == 3:
            set_counter += 1
            if set_counter > 2:
                # SET found!
                draw_card_contours(img_raw, set_cards, (0, 255, 0))
                if GAMEMODE:
                    put_text(img_raw, "SET! (press Space to continue)",\
                        150, WIN_BIG_W-80, 2)
                show_img_from_cards(set_cards, "warp_white_balanced", "Found SET")
        else:
            set_counter = 0


        draw_num_of_cards(img_raw, Cards)

        if FULLSCREEN:
            cv.namedWindow("CardDetection", cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty("CardDetection",cv.WND_PROP_FULLSCREEN,cv.WINDOW_FULLSCREEN)
            cv.imshow("CardDetection", cv.resize(img_raw, (WIN_BIG_W, WIN_BIG_H)))
        else:
            cv.imshow("CardDetection", cv.resize(img_raw, (WIN_BIG_W, WIN_BIG_H)))

        # show_img_from_cards(Cards, "warp_symbol_center_boxes", "Shading detection")
        # show_img_from_cards([Cards[0]], "warp", "Flatten")
        # show_img_from_cards([Cards[0]], "warp_grey", "Flatten grey")
        # show_img_from_cards([Cards[0]], "warp_thresh", "Flatten threshold")
        # show_img_from_cards([Cards[0]], "symbol_mask", "Symbol mask")
        # show_img_from_cards([Cards[0]], "warp_white_balanced", "White balanced")

        if TARGET:
            key = cv.waitKey(1) & 0xFF

            if set_counter > 2 and GAMEMODE:
                while key != ord(" "):
                    key = cv.waitKey(1) & 0xFF
                    set_counter = 0

                    # if `q` key was pressed, break from the loop
                    if key == ord("q"):
                        break
                cv.destroyWindow("Found SET")

            # if `q` key was pressed, break from the loop
            if key == ord("q"):
                CamStream.stop()
                break

                
        else:
            cv.waitKey(0)
            break


