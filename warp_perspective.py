import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('C:\\Users\\Claudio-PC\\Documents\\set_computer\\Imgs\\image1.jpg')

# cv.imshow("Original Image ", img)
# cv.waitKey(0)

plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
plt.show()