"""Module to detect cards in image"""

import numpy as np
import cv2 as cv
import set_engine
from card_classifier import CCardClassifier


class CQueryCard(set_engine.CCard):
    """Structure to store information about query cards in the camera img_raw."""

    def __init__(self, contour, raw, pts):
        """Uses contour to create a qCard"""
        # Init parent class from set_engine
        super().__init__()

        self.contour = contour  # Contour of card
        self.area = cv.contourArea(contour)  # Area size of card
        _, _, self.width, self.height = cv.boundingRect(contour)  # Width and height of card
        self.corner_pts = pts  # Corner points of card

        # Find center point of card by taking x and y average of the four corners.
        average = np.sum(pts, axis=0)/len(pts)
        cent_x = int(average[0][0])
        cent_y = int(average[0][1])
        self.center = [cent_x, cent_y]

        self.warp = self.flattener(raw, pts, self.width, self.height)
        self.warp_thresh = [] # 200x300, flattened thresholded img of card
        self.symbol_contours = [] # list of contours of the card symbols
        self.symbol_mask = [] # symbols as white on black background

    def flattener(self, raw, pts, w, h):
        """Flattens an img_raw of a card into a top-down 200x300 perspective."""
        FLATTEN_WIDTH = 200
        FLATTEN_HEIGHT = 300

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

        # Create destination array, calculate perspective transform matrix,
        # and warp card img_raw
        dst = np.array([[0, 0], [FLATTEN_WIDTH-1, 0], [FLATTEN_WIDTH-1, FLATTEN_HEIGHT-1],
                    [0, FLATTEN_HEIGHT-1]], np.float32)
        transform_m = cv.getPerspectiveTransform(temp_rect, dst)
        warp = cv.warpPerspective(raw, transform_m, (FLATTEN_WIDTH, FLATTEN_HEIGHT))

        return warp


class CCardDetector:
    """Class to detect cards on game field"""
    def __init__(self):
        self.font = cv.FONT_HERSHEY_SIMPLEX

        self.CARD_MAX_AREA = 120000
        self.CARD_MIN_AREA = 10000

        self.raw = [] # raw image of game field
        self.thresh = [] # thresholded img of game field
        self.qcards = [] # list of detected cards on game field

        self.CardClassifier = CCardClassifier()

    def get_cards_from_img(self, raw):
        """Main Function of Module"""
        self.raw = raw
        # Pre-process raw image of game field
        _, _, self.thresh = self.__preprocess_img_raw(raw)

        # Find the contours of all cards in the img_raw (query cards)
        self.qcards = self.__find_cards(self.thresh, raw)

        # Calc attributes of cards on game field
        self.CardClassifier.determine_attributes(self.qcards)

        return self.qcards


    def __preprocess_img_raw(self, raw):
        """Returns a grayed, img_blurred and thresholded img """

        grey = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(grey, (3, 3), 0)

        thresh_val, thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        # Detect edges using Canny
        # thresh = cv.Canny(thresh, thresh_val, thresh_val * 2)

        return grey, blur, thresh


    def __find_cards(self, thresh, raw):
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
            approx = cv.approxPolyDP(ctr, 0.1*peri, True)

            # Determine which of the contours are cards by applying the
            # following criteria:
            # 1) Smaller area than the maximum card size
            # 2) bigger area than the minimum card size
            # 3) have no parents
            # 4) have four corners

            if (
                (size < self.CARD_MAX_AREA) and
                (size > self.CARD_MIN_AREA) and
                hier_sort[i][3] == -1 and
                len(approx) == 4
            ):
                # Create a card object from the contour and append it to
                # the list of cards. preprocess_card function takes the
                # card contour and contour and determines the cards
                # properties (corner points, etc). It generates a
                # flattened raw of the card
                qcards.append(CQueryCard(ctr, raw, np.float32(approx)))

        return qcards

    def get_result_img(self):
        """Draw the card name, center point, and contour on the camera img_raw."""

        # Draw card contours on image (have to do contours all at once or
        # they do not show up properly for some reason)
        if len(self.qcards) > 0:
            temp_cnts = []
            for qcard in self.qcards:
                temp_cnts.append(qcard.contour)
            cv.drawContours(self.raw,temp_cnts, -1, (0,255,0), 3)

        for qcard in self.qcards:
            x = qcard.center[0]
            y = qcard.center[1]
            cv.circle(self.raw, (x, y), 5, (0, 255, 0), -1)

            self.put_text_centered(self.raw, f"{qcard.get_number()}", x, y-40)
            self.put_text_centered(self.raw, f"{qcard.get_symbol()}", x, y-10)
            self.put_text_centered(self.raw, f"{qcard.get_color()}", x, y+20)

        cv.putText(self.raw, (f"Detected Cards: {len(self.qcards)}"),
                (3, 24), self.font, 1, (255, 255, 0), 2, cv.LINE_AA)

        return self.raw

    def get_flatten_imgs(self, win_flatten_w, win_flatten_h):
        """Draw contour and mask"""
        if len(self.qcards) > 0:
            img_flatten = cv.resize(self.qcards[0].warp, (win_flatten_w, win_flatten_h))
            img_flatten_thresh = cv.resize(self.qcards[0].warp_thresh, (win_flatten_w, win_flatten_h))
            img_symbol_mask = cv.resize(self.qcards[0].symbol_mask, (win_flatten_w, win_flatten_h))

            if len(self.qcards) > 1:
                for card in self.qcards[1:]:
                    # cv.drawContours(
                    #     card.warp, card.symbol_contours, -1, (0, 0, 0), 1)
                    img_flatten = np.hstack((
                        img_flatten, cv.resize(
                            card.warp, (win_flatten_w, win_flatten_h))))

                    img_flatten_thresh = np.hstack((
                        img_flatten_thresh, cv.resize(
                            card.warp_thresh, (win_flatten_w, win_flatten_h))))

                    img_symbol_mask = np.hstack((
                        img_symbol_mask, cv.resize(
                            card.symbol_mask, (win_flatten_w, win_flatten_h))))

        return img_flatten, img_flatten_thresh, img_symbol_mask

    def put_text_centered(self, img, text, center_x, center_y):
        """Put text into the given img centered to given x and y coordinates"""
        # get boundary of the text
        textsize = cv.getTextSize(text, self.font, 1, 2)[0]

        # get coords based on boundary
        textX = int(center_x - textsize[0] / 2)
        textY = int(center_y + textsize[1] / 2)

        # Draw text twice, so letters have black outline
        cv.putText(img, (text),
            (textX, textY-10), self.font, 1, (0, 0, 0), 3, cv.LINE_AA)
        cv.putText(img, (text),
            (textX, textY-10), self.font, 1, (50, 200, 200), 2, cv.LINE_AA)