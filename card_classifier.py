import numpy as np
import cv2 as cv

SYMBOL_MIN_AREA = 4000

def determine_attributes(cards):
    """ Determines attributes of given qcards """
    for card in cards:
        preprocess_card_img(card)
        calc_number(card)
        calc_symbol(card)
        calc_shading(card)
        calc_color(card)


def preprocess_card_img(card):
    """  """
    flatten = card.warp
    grey = cv.cvtColor(flatten, cv.COLOR_BGR2GRAY)
    thresh_val, thresh = cv.threshold(grey, 0, 255,
                                      cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    # get largest contour
    contours = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = contours[0] if len(contours) == 2 else contours[1]

    # draw filled contour on black background
    mask = np.zeros_like(flatten)
    contours = list(filter(lambda ctr: cv.contourArea(ctr) > SYMBOL_MIN_AREA,
                           contours))
    cv.drawContours(mask, contours, -1, (255,255,255), -1)

    # apply mask to input image
    masked_img = cv.bitwise_and(flatten, mask)

    card.symbol_contours = contours
    card.warp_thresh = thresh
    card.warp_masked = masked_img


def calc_number(card):
    """ Calculates number of symbols by analyzing num of symbol contours"""
    card.attributes["number"] = len(card.symbol_contours)


def calc_symbol(card):
    pass


def calc_shading(card):
    pass


def calc_color(card):
    pass
