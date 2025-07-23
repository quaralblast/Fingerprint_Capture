import cv2
import time
import numpy as np

start = time.perf_counter()
target = cv2.imread(r"C:\Users\LAB-PC\Downloads\download.jpg")

# Resizing if applicable
# target = inputIMG[0:1636,480:2780]
target = cv2.resize(target,(800,1000))

# Grayscale image
grayscaled = cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)

# Gaussian Blur to remove noise
grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)

# Erosion followed by dilation to further remove noise
kernel = np.ones((5,5),np.uint8)
opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)

# Contrast Limited Adaptive Histogram Equalization - sharpens image
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
cl1 = clahe.apply(opening)

_, thresh = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

thresh = cv2.bitwise_not(thresh)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

largest_contour = max(contours, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(largest_contour)

cropped = cl1[y:y+h, x:x+w]

cv2.imshow("Fingerprint", cropped)
cv2.waitKey(0)
cv2.destroyAllWindows()