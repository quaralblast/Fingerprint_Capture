import cv2
#from rembg import remove 
#from rembg.bg import new_session
from time import sleep
import numpy as np
import os
from skimage.metrics import structural_similarity

def process():
    count = 0

    inputImg = cv2.imread(r'C:\Users\LAB-PC\Desktop\Jonathan King SDIP 2025\Processed_Raw.jpg')
    #clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    #! Opens image and crop + resize
    targetImage = inputImg[0:1636,480:2780]
    targetImage = cv2.resize(targetImage,(500,500))

    cv2.imwrite(f'output_img{count}.jpg',targetImage)
    count += 1

    #! Removing the background from the given Image 
    #targetImage = remove(targetImage,session=new_session("u2netp")) 

    #! Grayscale the fucker
    GrayImage = cv2.cvtColor(targetImage, cv2.COLOR_BGR2GRAY)

    cv2.imwrite(f'output_img{count}.jpg',GrayImage)
    count += 1

    #! Bitwise not to flip colors
    resized_image = cv2.bitwise_not(GrayImage)

    cv2.imwrite(f'output_img{count}.jpg',resized_image)
    count += 1

    img = cv2.GaussianBlur(resized_image,(3,3),1)

    cv2.imwrite(f'output_img{count}.jpg',img)
    count += 1

    Final = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    cv2.THRESH_BINARY,17,1)
    kernel = np.ones((1, 2), np.uint8)

    cv2.imwrite(f'output_img{count}.jpg',Final)
    count += 1

    dilated_image = cv2.dilate(Final, kernel, iterations=2)

    cv2.imwrite(f'output_img{count}.jpg',dilated_image)
    count += 1

    final_eroded_image = cv2.erode(dilated_image, kernel, iterations=2)

    cv2.imwrite(f'output_img{count}.jpg',final_eroded_image)
    count += 1

def ssim():
    img1 = cv2.imread(r'C:\Users\LAB-PC\Documents\code\output_img4.jpg')
    img2 = cv2.imread(r'C:\Users\LAB-PC\Documents\code\output_img5.jpg')
    img3 = cv2.imread(r'C:\Users\LAB-PC\Documents\code\output_img6.jpg')

    print(img1.shape)
    for i in [img2,img3]:
        score, diff = structural_similarity(img1,i,full=True,channel_axis=2)
        print(score)
        diff = (diff * 255).astype('uint8')
        cv2.imshow('ssim difference', diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    query = input('1 or 2: ')
    if query == '1':
        process()
    elif query == '2':
        ssim()