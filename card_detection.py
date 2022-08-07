"""Module to detect cards in image"""

import numpy as np
import cv2 as cv


# Constants
BIN_THRESHOLD = 128

CARD_MAX_AREA = 120000
CARD_MIN_AREA = 10000


class CQueryCard:
    """Structure to store information about query cards in the camera img_raw."""

    def __init__(self):
        self.contour = []  # Contour of card
        self.area = 0  # Area size of card
        self.width, self.height = 0, 0  # Width and height of card
        self.corner_pts = []  # Corner points of card
        self.center = []  # Center point of card
        self.warp = []  # 200x300, flattened img_raw


def get_qcards_from_img(raw):
    """Main Function of Module"""
    # Pre-process camera img_raw
    grey, blur, thresh = preprocess_img_raw(raw)

    # Find and sort the contours of all cards in the img_raw (query cards)
    qcards = find_cards(thresh, raw)

    # Draw center point on the img_raw.
    img_of_found_cards = draw_results(img_raw, qcards)

    return qcards, img_of_found_cards, thresh


def preprocess_img_raw(raw):
    """Returns a grayed, img_blurred and thresholded img """

    grey = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(grey, (5, 5), 0)

    _, thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    return grey, blur, thresh


def find_cards(thresh, raw):
    """Finds all card-sized contours"""

    # Find contours and sort their indices by contour size
    cnts, hier = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(
        range(len(cnts)), key=lambda i: cv.contourArea(cnts[i]), reverse=True
        )

    # If there are no contours, do nothing
    if len(cnts) == 0:
        return [], []

    # Otherwise, initialize empty sorted contour and hierarchy lists
    cnts_sort = []
    hier_sort = []

    # Fill empty lists with sorted contour and sorted hierarchy. Now,
    # the indices of the contour list still correspond with those of
    # the hierarchy list. The hierarchy array can be used to check if
    # the contours have parents or not.
    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    qcards = []
    for i, ctr in enumerate(cnts_sort):
        size = cv.contourArea(ctr)
        peri = cv.arcLength(ctr, True)
        approx = cv.approxPolyDP(ctr, 0.01*peri, True)
        # Determine which of the contours are cards by applying the
        # following criteria:
        # 1) Smaller area than the maximum card size
        # 2) bigger area than the minimum card size
        # 3) have no parents
        # 4) have four corners

        if (
            (size < CARD_MAX_AREA) and
            (size > CARD_MIN_AREA) and
            hier_sort[i][3] == -1 and
            len(approx) == 4
        ):
            # Create a card object from the contour and append it to
            # the list of cards. preprocess_card function takes the
            # card contour and contour and determines the cards
            # properties (corner points, etc). It generates a
            # flattened raw of the card
            qcards.append(preprocess_card(ctr, raw))

    return qcards


def preprocess_card(contour, raw):
    """Uses contour to find information about the query card."""

    # Initialize new Query_card object
    qcard = CQueryCard()

    qcard.contour = contour
    qcard.area = cv.contourArea(contour)

    # Find perimeter of card and use it to approximate corner points
    peri = cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, 0.01*peri, True)
    pts = np.float32(approx)
    qcard.corner_pts = pts

    # Find width and height of card's bounding rectangle
    _, _, w, h = cv.boundingRect(contour)
    qcard.width, qcard.height = w, h

    # Find center point of card by taking x and y average of the four corners.
    average = np.sum(pts, axis=0)/len(pts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    qcard.center = [cent_x, cent_y]

    # Warp card into 200x300 flattened img_raw using perspective transform
    qcard.warp = flattener(raw, pts, w, h)

    return qcard


def draw_results(raw, qcards):
    """Draw the card name, center point, and contour on the camera img_raw."""
    font = cv.FONT_HERSHEY_SIMPLEX
    
    for qcard in qcards:
        x = qcard.center[0]
        y = qcard.center[1]
        cv.circle(raw, (x, y), 5, (0, 255, 0), -1)

        # Draw text twice, so letters have black outline
        
        cv.putText(raw, (f"Size:{qcard.area}"),
                (x-60, y-10), font, 1, (0, 0, 0), 3, cv.LINE_AA)
        cv.putText(raw, (f"Size:{qcard.area}"),
                (x-60, y-10), font, 1, (50, 200, 200), 2, cv.LINE_AA)

    # Draw card contours on image (have to do contours all at once or
    # they do not show up properly for some reason)
    if len(qcards) > 0:
        temp_cnts = []
        for qcard in qcards:
            temp_cnts.append(qcard.contour)
        cv.drawContours(raw,temp_cnts, -1, (0,255,0), 2)

    cv.putText(raw, (f"Detected Cards: {len(qcards)}"),
            (3, 24), font, 1, (255, 255, 0), 2, cv.LINE_AA)

    return raw


def flattener(raw, pts, w, h):
    """Flattens an img_raw of a card into a top-down 200x300 perspective."""
    temp_rect = np.zeros((4, 2), dtype="float32")

    s = np.sum(pts, axis=2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis=-1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    # Need to create an array listing points in order of
    # [top left, top right, bottom right, bottom left]

    if w <= 0.8*h:  # If card is vertically oriented
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h:  # If card is horizontally oriented
        temp_rect[0] = bl
        temp_rect[1] = tl
        temp_rect[2] = tr
        temp_rect[3] = br

    # If the card is 'diamond' oriented, a different algorithm
    # has to be used to identify which point is top left, top right
    # bottom left, and bottom right.

    if w > 0.8*h and w < 1.2*h:  # If card is diamond oriented
        # If furthest left point is higher than furthest right point,
        # card is tilted to the left.
        if pts[1][0][1] <= pts[3][0][1]:
            # If card is titled to the left, approxPolyDP returns points
            # in this order: top right, top left, bottom left, bottom right
            temp_rect[0] = pts[1][0]  # Top left
            temp_rect[1] = pts[0][0]  # Top right
            temp_rect[2] = pts[3][0]  # Bottom right
            temp_rect[3] = pts[2][0]  # Bottom left

        # If furthest left point is lower than furthest right point,
        # card is tilted to the right
        if pts[1][0][1] > pts[3][0][1]:
            # If card is titled to the right, approxPolyDP returns points
            # in this order: top left, bottom left, bottom right, top right
            temp_rect[0] = pts[0][0]  # Top left
            temp_rect[1] = pts[3][0]  # Top right
            temp_rect[2] = pts[2][0]  # Bottom right
            temp_rect[3] = pts[1][0]  # Bottom left

    max_width = 200
    max_height = 300

    # Create destination array, calculate perspective transform matrix,
    # and warp card img_raw
    dst = np.array([[0, 0], [max_width-1, 0], [max_width-1, max_height-1],
                   [0, max_height-1]], np.float32)
    transform_m = cv.getPerspectiveTransform(temp_rect, dst)
    warp = cv.warpPerspective(raw, transform_m, (max_width, max_height))

    return warp


if __name__ == '__main__':
    from camera_stream import CCameraStream

    CamStream = CCameraStream(res=(1280, 720), fps=10)
    CamStream.run()

    while True:
        img_raw = CamStream.get()
        # img = cv.imread("C:\\Users\\Claudio-PC\\Documents\\...
        #                 set_computer\\Imgs\\2022-08-05_11-16-12.png")

        QCards, img_found_cards, img_thresh = get_qcards_from_img(img_raw)

        # Show Threshold img_raw
        cv.imshow("Threshold", cv.resize(img_thresh, (400, 240)))

        # Show Card Detection
        cv.imshow("CardDetection", cv.resize(img_found_cards, (400, 240)))

        # Show max. 5 Flatten img_raws
        for num, card in enumerate(QCards):
            if num == 0:
                img_flatten = cv.resize(card.warp, (100, 150))
            elif num < 6:
                img_flatten = np.hstack(
                    (img_flatten, cv.resize(card.warp, (100, 150))))

        cv.imshow("FlattenCards", img_flatten)

        key = cv.waitKey(1) & 0xFF

        # if `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    CamStream.stop()
