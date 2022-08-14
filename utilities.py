import cv2 as cv
import numpy as np

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

        put_text_centered(raw, f"{qcard.get_number()}", x, y-40)
        put_text_centered(raw, f"{qcard.get_symbol()}", x, y-10)
        put_text_centered(raw, f"{qcard.get_color()}", x, y+20)
        put_text_centered(raw, f"{qcard.get_shading()}", x, y+50)

    cv.putText(raw, (f"Detected Cards: {len(qcards)}"),
            (3, 24), FONT, 1, (255, 255, 0), 2, cv.LINE_AA)


def show_img_from_cards(qcards: list, img_name: str, win_name: str, size_wh: tuple):
    imgs = get_img_from_cards(qcards, img_name, size_wh)

    if len(qcards) == 1:
        cv.imshow(win_name, imgs[0])

    if len(qcards) > 1:
        cv.imshow(win_name, np.hstack(imgs))


def get_img_from_cards(qcards: list, img_name: str, size_wh: tuple):
    img_list = []
    for card in qcards:
        img_list.append(cv.resize(getattr(card, img_name), size_wh))
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
    # Draw text twice, so letters have black outline
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (0, 0, 0), 3, cv.LINE_AA)
    cv.putText(img, (text),
        (textX, textY-10), FONT, size, (0, 255, 0), 2, cv.LINE_AA)
