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

    def determine_attributes(self, card):
        """ Determines attributes of given qcard """
        if card.warp is None:
            return card
        self.preprocess_card_img(card)
        if len(card.symbol_contours) > 0:

            self.calc_number(card)
            self.calc_symbol(card)
            self.calc_color(card)
            self.calc_shading(card)

        return card

    def correct_white_balance(self, card):
        """Calc the mean of the outer area of the card,
        is a perfect white in reality and ajust img balance"""
        inner_mask, _, _ = cv.split(card.symbol_mask)
        white_b, white_g, white_r, _ = cv.mean(card.warp, mask=~inner_mask)


        img_b, img_g, img_r = cv.split(card.warp)

        img_b = img_b / white_b
        img_g = img_g / white_g
        img_r = img_r / white_r

        card.warp_white_balanced = np.clip(cv.merge([img_b, img_g, img_r]),0,1)

    def preprocess_card_img(self, card):
        """Preprocess flatten card image"""
        flatten = card.warp
        grey = cv.cvtColor(flatten, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(grey, (3, 3), 0)
        thresh_val, thresh = cv.threshold(blur, 0, 255,
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
        card.warp_grey = blur
        card.warp_thresh = thresh
        card.symbol_mask = mask

        self.correct_white_balance(card)


    def calc_number(self, card):
        """ Calculates number of symbols by analyzing num of symbol contours"""
        if len(card.symbol_contours) <= 3 and len(card.symbol_contours) > 0:
            card.attributes["number"] = len(card.symbol_contours)

    def calc_symbol(self, card):
        """Determines symbol by comparing reference symbols"""
        # Extract first symbol
        x,y,w,h = cv.boundingRect(card.symbol_contours[0])
        symbol_qcard = card.symbol_mask[y:y+h, x:x+w]
        card.attributes["symbol"] = self.compare_symbol_reference(symbol_qcard)

    def calc_shading(self, card):
        img = card.warp_white_balanced
        # Extract first symbol
        x,y,w,h = cv.boundingRect(card.symbol_contours[0])

        card.warp_symbol_center_boxes = card.warp_white_balanced.copy()

        # Pick only small part of symbol center
        center_box = img[
            int(y+0.4*h):int(y+0.6*h),
            int(x+0.4*w):int(x+0.6*w)
        ]

        # Draw small part of smbol into img
        cv.rectangle(card.warp_symbol_center_boxes,
            (int(x+0.4*w),int(y+0.4*h)),(int(x+0.6*w),int(y+0.6*h)),(0,0,0), 2)
        cv.rectangle(card.warp_symbol_center_boxes,
            (int(x+0.4*w),int(y+0.4*h)),(int(x+0.6*w),int(y+0.6*h)),(0,255,255), 1)

        center_box_hsv = cv.cvtColor(np.float32(center_box), cv.COLOR_BGR2HSV)
        saturation_hsv = center_box_hsv[:, :, 1].mean()
        cv.putText(card.warp_symbol_center_boxes, f"Sat: {saturation_hsv:0.2f}", (5, 20), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

        center_box_hls = cv.cvtColor(np.float32(center_box), cv.COLOR_BGR2HLS)
        lightness_hls = center_box_hls[:, :, 1].mean()
        cv.putText(card.warp_symbol_center_boxes, f"Lig: {lightness_hls:0.2f}", (5, 40), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
        if saturation_hsv > 0.5:
            card.attributes["shading"] = "solid"
        elif lightness_hls > 0.9 and saturation_hsv < 0.1:
            card.attributes["shading"] = "empty"
        else:
            card.attributes["shading"] = "hatched"

        cv.putText(card.warp_symbol_center_boxes, card.get_shading(), (5, 60), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)


    def calc_color(self, card):
        # convert 3-channel to 1-channel
        inner_mask, _, _ = cv.split(card.symbol_mask)
        
        # calc mean of each color channel inside the symbol contour
        mean_b, mean_g, mean_r, _ = cv.mean(card.warp_white_balanced, mask=inner_mask)
        color_means = {
            "red" : mean_r,
            "green" : mean_g,
            "purple" : mean_b
        }
        max_color = max(color_means, key=color_means.get)

        warp_hsv = cv.cvtColor(np.float32(card.warp_white_balanced),\
             cv.COLOR_BGR2HSV)

        min_value = np.amin(warp_hsv[:, :, 2])

        if min_value < 0.15:
            card.attributes["color"] = "purple"
        else:
            card.attributes["color"] = max_color

        card.warp_color_detection = card.warp_white_balanced.copy()
        cv.putText(card.warp_color_detection, f"Mean B: {mean_b:0.3f}", (5, 20), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
        cv.putText(card.warp_color_detection, f"Mean G: {mean_g:0.3f}", (5, 40), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
        cv.putText(card.warp_color_detection, f"Mean R: {mean_r:0.3f}", (5, 60), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
        cv.putText(card.warp_color_detection, f"Min Val: {min_value:0.2f}", (5, 80), \
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)


    def compare_symbol_reference(self, symbol_qcard):
        """Compare symbol on card with reference symbol
            return name of symbol or ''"""
        similarity = {}
        for symbol_name in self.symbol_reference:
            symbol_size_h, symbol_size_w, _ = symbol_qcard.shape
            if (
                symbol_size_h < 50 or symbol_size_h > 80 
                or symbol_size_w < 120 or symbol_size_w > 160
            ):
                return ""

            symbol_ref = self.symbol_reference[symbol_name]
            ref_h, ref_w, _ = symbol_ref.shape
            symbol_qcard_resized = cv.resize(symbol_qcard, (ref_w, ref_h))

            errorL2 = cv.norm(symbol_qcard_resized, symbol_ref, cv.NORM_L2)
            similarity[symbol_name] = 1 - errorL2 / ( ref_h * ref_w )
        return max(similarity, key=similarity.get)

        