# Import necessary packages
import numpy as np
import cv2 as cv
import time

### Constants ###

# Adaptive threshold levels
BKG_THRESH = 60
CARD_THRESH = 30

# Width and height of card corner, where rank and suit are
CORNER_WIDTH = 32
CORNER_HEIGHT = 84

CARD_MAX_AREA = 200000
CARD_MIN_AREA = 2000


### Structures to hold query card and train card information ###

class QueryCard:
    """Structure to store information about query cards in the camera image."""

    def __init__(self):
        self.contour = [] # Contour of card
        self.width, self.height = 0, 0 # Width and height of card
        self.corner_pts = [] # Corner points of card
        self.center = [] # Center point of card
        self.warp = [] # 200x300, flattened, grayed, blurred image
        self.img_gray = [] # Thresholded, sized image of card's rank
        self.img_colo = [] # Thresholded, sized image of card's suit



def preprocess_image(image):
    """Returns a grayed, blurred and thresholded img """

    gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(5,5),0)

    _ , thresh = cv.threshold(blur,128,255,cv.THRESH_BINARY)

    return gray, blur, thresh

def find_cards(thresh_image):
    """Finds all card-sized contours"""

    # Find contours and sort their indices by contour size
    cnts,hier = cv.findContours(thresh_image,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i : cv.contourArea(cnts[i]),reverse=True)

    # If there are no contours, do nothing
    if len(cnts) == 0:
        return [], []

    # Otherwise, initialize empty sorted contour and hierarchy lists
    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts),dtype=int)

    # Fill empty lists with sorted contour and sorted hierarchy. Now,
    # the indices of the contour list still correspond with those of
    # the hierarchy list. The hierarchy array can be used to check if
    # the contours have parents or not.
    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    # Determine which of the contours are cards by applying the
    # following criteria: 1) Smaller area than the maximum card size,
    # 2), bigger area than the minimum card size, 3) have no parents,
    # and 4) have four corners

    for i, ctr in enumerate(cnts_sort):
        size = cv.contourArea(cnts_sort[i])
        peri = cv.arcLength(cnts_sort[i],True)
        approx = cv.approxPolyDP(cnts_sort[i],0.01*peri,True)
        
        if ((size < CARD_MAX_AREA) and (size > CARD_MIN_AREA) and 
            (hier_sort[i][3] == -1)): # and (len(approx) == 4)):
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card

def preprocess_card(contour, image):
    """Uses contour to find information about the query card.."""

    # Initialize new Query_card object
    qCard = QueryCard()

    qCard.contour = contour

    # Find perimeter of card and use it to approximate corner points
    peri = cv.arcLength(contour,True)
    approx = cv.approxPolyDP(contour,0.01*peri,True)
    pts = np.float32(approx)
    qCard.corner_pts = pts

    # Find width and height of card's bounding rectangle
    _,_,w,h = cv.boundingRect(contour)
    qCard.width, qCard.height = w, h

    # Find center point of card by taking x and y average of the four corners.
    average = np.sum(pts, axis=0)/len(pts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    qCard.center = [cent_x, cent_y]

    # Warp card into 200x300 flattened image using perspective transform
    qCard.warp = flattener(image, pts, w, h)

    return qCard

def draw_results(image, qCard):
    """Draw the card name, center point, and contour on the camera image."""

    x = qCard.center[0]
    y = qCard.center[1]
    cv.circle(image,(x,y),5,(255,0,0),-1)

    return image

def flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective."""
    temp_rect = np.zeros((4,2), dtype = "float32")

    s = np.sum(pts, axis = 2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    # Need to create an array listing points in order of
    # [top left, top right, bottom right, bottom left]

    if w <= 0.8*h: # If card is vertically oriented
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h: # If card is horizontally oriented
        temp_rect[0] = bl
        temp_rect[1] = tl
        temp_rect[2] = tr
        temp_rect[3] = br

    # If the card is 'diamond' oriented, a different algorithm
    # has to be used to identify which point is top left, top right
    # bottom left, and bottom right.

    if w > 0.8*h and w < 1.2*h: #If card is diamond oriented
        # If furthest left point is higher than furthest right point,
        # card is tilted to the left.
        if pts[1][0][1] <= pts[3][0][1]:
            # If card is titled to the left, approxPolyDP returns points
            # in this order: top right, top left, bottom left, bottom right
            temp_rect[0] = pts[1][0] # Top left
            temp_rect[1] = pts[0][0] # Top right
            temp_rect[2] = pts[3][0] # Bottom right
            temp_rect[3] = pts[2][0] # Bottom left

        # If furthest left point is lower than furthest right point,
        # card is tilted to the right
        if pts[1][0][1] > pts[3][0][1]:
            # If card is titled to the right, approxPolyDP returns points
            # in this order: top left, bottom left, bottom right, top right
            temp_rect[0] = pts[0][0] # Top left
            temp_rect[1] = pts[3][0] # Top right
            temp_rect[2] = pts[2][0] # Bottom right
            temp_rect[3] = pts[1][0] # Bottom left

    max_width = 200
    max_height = 300

    # Create destination array, calculate perspective transform matrix,
    # and warp card image
    dst = np.array([[0,0],[max_width-1,0],[max_width-1,max_height-1],[0, max_height-1]], np.float32)
    m = cv.getPerspectiveTransform(temp_rect,dst)
    warp = cv.warpPerspective(image, m, (max_width, max_height))

    return warp

if __name__ == '__main__':
    from camera_stream import CameraStream
    import cv2 as cv
    import time
    import numpy as np

    CamStream = CameraStream(res=(1280, 720), fps=10)
    CamStream.run()

    time.sleep(2)

    while True:
        img = CamStream.get()
        # img = cv.imread("C:\\Users\\Claudio-PC\\Documents\\set_computer\\Imgs\\2022-08-05_11-16-12.png")
        # Pre-process camera image (gray, blur, and threshold it)
        grey, blur, pre_proc = preprocess_image(img)

        # Find and sort the contours of all cards in the image (query cards)
        cnts_sort, cnt_is_card = find_cards(pre_proc)

        # If there are no contours, do nothing
        if len(cnts_sort) != 0:

            # Initialize a new "cards" list to assign the card objects.
            # k indexes the newly made array of cards.
            cards = []
            k = 0

            # For each contour detected:
            for i, _ in enumerate(cnts_sort):
                if (cnt_is_card[i] == 1):

                    # Create a card object from the contour and append it to the list of cards.
                    # preprocess_card function takes the card contour and contour and
                    # determines the cards properties (corner points, etc). It generates a
                    # flattened 200x300 image of the card, and isolates the card's
                    # suit and rank from the image.
                    cards.append(preprocess_card(cnts_sort[i],img))

                    # Draw center point on the image.
                    img = draw_results(img, cards[k])
                    k+=1

            # Draw card contours on image (have to do contours all at once or
            # they do not show up properly for some reason)
            if len(cards) != 0:
                temp_cnts = []
                for j,_ in enumerate(cards):
                    temp_cnts.append(cards[j].contour)
                cv.drawContours(img,temp_cnts, -1, (255,0,0), 2)

        # Show in FullScreen Window
        cv.namedWindow("window", cv.WND_PROP_FULLSCREEN)
        cv.setWindowProperty("window",cv.WND_PROP_FULLSCREEN,cv.WINDOW_FULLSCREEN)
        row1 = np.hstack((cv.cvtColor(grey, cv.COLOR_GRAY2BGR), cv.cvtColor(blur, cv.COLOR_GRAY2BGR)))
        row2 = np.hstack((cv.cvtColor(pre_proc, cv.COLOR_GRAY2BGR), img))
        img_matrix = np.vstack((row1, row2))
        img_matrix = cv.resize(img_matrix, (800, 480))
        cv.imshow("window", img_matrix)

        key = cv.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    CamStream.stop()
