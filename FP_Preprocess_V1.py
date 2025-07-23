import cv2
import numpy as np
import time
from scipy.ndimage import convolve
import math
import matplotlib.pyplot as plt
import sys
from PIL import Image
from skimage.morphology import skeletonize

def process():
    start = time.perf_counter()
    inputIMG = cv2.imread(r"C:\Users\LAB-PC\Documents\code\python\Fingerprint\raspireader_rawftir.png")

    # TODO: Somehow change to dynamic resizing ? 
    # target = inputIMG[0:1636,480:2780]
    # target = cv2.resize(target,(500,500))

    grayscaled = cv2.cvtColor(inputIMG,cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(grayscaled)
    inverted = cv2.bitwise_not(cl1)
    img = cv2.GaussianBlur(inverted,(3,3),1)
    Final = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    cv2.THRESH_BINARY,17,1)
    cv2.imwrite('lol.jpg',Final)
    Final = Final // 255
    thinned = skeletonize(Final).astype(np.uint8) * 255
    inverted2 = cv2.bitwise_not(thinned)
    cv2.imwrite('test.jpg',inverted2)
    end = time.perf_counter()
    print(end - start)


if __name__ == '__main__':
    process()








# target = cv2.imread("raspireader_rawftir.png")
# assert target is not None, "file not read"
# # target = inputIMG[0:1636,480:2780]
# # target = cv2.resize(target,(500,500))
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
# cl1 = clahe.apply(target)
 
# cv2.imwrite('clahe_2.jpg',cl1)
# hsv = cv2.cvtColor(target,cv2.COLOR_BGR2HSV)

