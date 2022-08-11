import numpy as np
import cv2 as cv
import set_engine as se

SYMBOL_MIN_AREA = 4000
SYMBOL_REF_PATH = "symbol_reference"

class CCardClassifier:
    """Class to classify attributes of the cards"""
    def __init__(self):
        symbols = se.possible_attributes["symbol"]
        self.symbol_reference = {}
        for symbol_name in symbols:
            self.symbol_reference[symbol_name] = \
                cv.imread(f"{SYMBOL_REF_PATH}/{symbol_name}.png")

    def determine_attributes(self, cards: list):
        """ Determines attributes of given qcards """
        for card in cards:
            self.preprocess_card_img(card)
            self.correct_white_balance(card)
            self.calc_number(card)
            self.calc_symbol(card)
            self.calc_shading(card)
            self.calc_color(card)

    def correct_white_balance(self, card):
        """Calc the mean of the outer area of the card,
        is a perfect white in reality and ajust img balance"""
        inner_mask, _, _ = cv.split(card.symbol_mask)
        white_b, white_g, white_r, _ = cv.mean(card.warp, mask=~inner_mask)

        img_b, img_g, img_r = cv.split(card.warp)

        img_b = img_b / white_b
        img_g = img_g / white_g
        img_r = img_r / white_r

        card.warp = cv.merge([img_b, img_g, img_r])

    def preprocess_card_img(self, card):
        """Preprocess flatten card image"""
        flatten = card.warp
        grey = cv.cvtColor(flatten, cv.COLOR_BGR2GRAY)
        thresh_val, thresh = cv.threshold(grey, 0, 255,
                                        cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

        # get largest contour
        contours = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        contours = contours[0] if len(contours) == 2 else contours[1]

        # draw filled contour on black background
        mask = np.zeros_like(flatten, dtype="uint8")
        contours = list(filter(lambda ctr: cv.contourArea(ctr) > SYMBOL_MIN_AREA,
                            contours))
        cv.drawContours(mask, contours, -1, (255, 255, 255), -1)

        card.symbol_contours = contours
        card.warp_thresh = thresh
        card.symbol_mask = mask


    def calc_number(self, card):
        """ Calculates number of symbols by analyzing num of symbol contours"""
        card.attributes["number"] = len(card.symbol_contours)

    def calc_symbol(self, card):
        """Determines symbol by comparing reference symbols"""
        # Extract first symbol
        x,y,w,h = cv.boundingRect(card.symbol_contours[0])
        symbol_qcard = card.symbol_mask[y:y+h, x:x+w]
        card.attributes["symbol"] = self.compare_symbol_reference(symbol_qcard)

    def calc_shading(self, card):
        pass

        # # apply mask to input image
        # masked_img = cv.bitwise_and(flatten, mask)


    def calc_color(self, card):
        inner_mask, _, _ = cv.split(card.symbol_mask)
        mean_b, mean_g, mean_r, _ = cv.mean(card.warp, mask=inner_mask)
        color_means = {
            "red" : mean_r,
            "green" : mean_g,
            "purple" : mean_b
        }
        card.attributes["color"] = max(color_means, key=color_means.get)

    def compare_symbol_reference(self, symbol_qcard):
        """Compare symbol on card with reference symbol
            return name of symbol or None"""
        similarity = {}
        for symbol_name in self.symbol_reference:
            symbol_ref = self.symbol_reference[symbol_name]
            ref_h, ref_w, _ = symbol_ref.shape
            symbol_qcard_resized = cv.resize(symbol_qcard, (ref_w, ref_h))

            errorL2 = cv.norm(symbol_qcard_resized, symbol_ref, cv.NORM_L2)
            similarity[symbol_name] = 1 - errorL2 / ( ref_h * ref_w )

        return max(similarity, key=similarity.get)

        