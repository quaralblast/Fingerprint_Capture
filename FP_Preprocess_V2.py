import cv2
from PIL import Image
import numpy as np
import time 

def process(self, inputIMG):
    
    # Resizing if applicable
    target = inputIMG[575:1845,1465:3065] # 1465:3065,575:1845


    # Grayscale image
    grayscaled = cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)
   
    # Gaussian Blur to remove noise
    grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)

    # Erosion followed by dilation to further remove noise
    kernel = np.ones((2,2),np.uint8)
    opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)
    
    # Contrast Limited Adaptive Histogram Equalization - sharpens image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(opening)
  
    # Invert Colors
    inverted = cv2.bitwise_not(cl1)

    return inverted
    # # Save Image
    # cv2.imwrite('test_finger_out5.jpg',inverted)

    # # Change to 500 dpi
    # img = Image.open('test_finger_out5.jpg')
    # img.save("test_finger_out4.jpg", dpi=(1000, 1000))

    '''
    Additional Preprocessing if applicable (hopefully not needed)
    - segmentation
    
    ''' 

if __name__ == '__main__':
    process()