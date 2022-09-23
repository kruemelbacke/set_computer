import cv2 as cv
from playsound import playsound

import set_engine
from card_detection import CCardDetector
from utilities import draw_card_contours, draw_attributes, draw_num_of_cards, show_img_from_cards

###########################################
TARGET = True
GAMEMODE = True
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

    COUNTER_CERTAINTY = 2
else:
    # IMG_PATH = "Imgs/2022-08-14_12-16-12.png" # purple is rather black
    IMG_PATH = "Imgs/2022-08-11_14-42-06.png" # wrong card on field
    # IMG_PATH = "Imgs/2022-08-10_18-33-38.png" # strong warm and cold light
    # IMG_PATH = "Imgs/Original.png"

    WIN_FLATTEN_W = 200
    WIN_FLATTEN_H = 300

    WIN_BIG_W = 1280
    WIN_BIG_H = 720

    COUNTER_CERTAINTY = 1

if GAMEMODE:
    WIN_FLATTEN_W = 100
    WIN_FLATTEN_H = 150

    WIN_BIG_W = 800
    WIN_BIG_H = 480

exit_request = False


def exit_programm(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        global exit_request
        exit_request = True


if __name__ == '__main__':
    if TARGET:
        CamStream = CCameraStream(res=(1920, 1080), fps=10)
        CamStream.run()
    try:
        CardDetector = CCardDetector()

        if GAMEMODE:
            cv.namedWindow("CardDetection", cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty("CardDetection",cv.WND_PROP_FULLSCREEN,cv.WINDOW_FULLSCREEN)
            cv.setMouseCallback("CardDetection", exit_programm)

        set_counter = 0
        while True:
            if TARGET:
                img_raw = CamStream.get()
            else:
                img_raw = cv.imread(IMG_PATH)

            Cards = CardDetector.get_cards_from_img(img_raw)
            draw_card_contours(img_raw, Cards, (0, 0, 255))

            set_cards = set_engine.find_set_primitive_loop(Cards)

            if len(set_cards) == 3:
                set_counter += 1
                if set_counter == COUNTER_CERTAINTY:
                    # SET found!
                    playsound("set_audio_sample.wav")

                if set_counter >= COUNTER_CERTAINTY:
                    draw_card_contours(img_raw, set_cards, (0, 255, 0))
                    show_img_from_cards(set_cards, "warp_white_balanced", \
                        "Found SET", (WIN_FLATTEN_W, WIN_FLATTEN_H))
            else:
                if set_counter >= COUNTER_CERTAINTY:
                    cv.destroyWindow("Found SET")
                set_counter = 0

            draw_attributes(img_raw, Cards)
            draw_num_of_cards(img_raw, Cards)

            if GAMEMODE:
                cv.imshow("CardDetection", cv.resize(img_raw, (WIN_BIG_W, WIN_BIG_H)))
            else:
                cv.imshow("CardDetection", cv.resize(img_raw, (WIN_BIG_W, WIN_BIG_H)))

                # show_img_from_cards(Cards, "warp_symbol_center_boxes", "Shading Detection", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                # show_img_from_cards([Cards[2], Cards[3], Cards[7], Cards[10]], "warp_color_detection", "Color Detection", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                # show_img_from_cards(Cards, "warp", "Flatten", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                # show_img_from_cards([Cards[7]], "warp_grey", "Flatten grey", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                # show_img_from_cards([Cards[7]], "warp_thresh", "Flatten threshold", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                # show_img_from_cards([Cards[7]], "symbol_mask", "Symbol mask", \
                #     (WIN_FLATTEN_W, WIN_FLATTEN_H))
                show_img_from_cards(Cards, "warp_white_balanced", "White balanced", \
                    (WIN_FLATTEN_W, WIN_FLATTEN_H))

            if TARGET:
                key = cv.waitKey(1) & 0xFF

                # if `q` key was pressed, break from the loop
                if key == ord("q") or exit_request is True:
                    break

            else:
                cv.waitKey(0)
                break
    finally:
        cv.destroyAllWindows()
        if TARGET:
            CamStream.stop()
