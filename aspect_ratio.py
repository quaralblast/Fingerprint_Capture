import cv2
import numpy as np
from rembg import remove
from rembg.bg import new_session


# pic = cv2.imread(r'C:\Users\LAB-PC\Documents\code\python\Fingerprint\Fingerprint_Data\_raw.png')

# # Grayscale image
# target = pic[575:1845,1465:3065]
# rembg_session = new_session("u2net")
# bg_removed = remove(target, session=rembg_session)
# grayscaled = cv2.cvtColor(bg_removed,cv2.COLOR_BGR2GRAY)

# # Gaussian Blur to remove noise
# grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)

# # Erosion followed by dilation to further remove noise
# kernel = np.ones((2,2),np.uint8)
# opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)

# # Contrast Limited Adaptive Histogram Equalization - sharpens image
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
# cl1 = clahe.apply(opening)

# _, threshold = cv2.threshold(cl1, thresh=100, maxval=255, type=cv2.THRESH_TOZERO)

# # Invert Colors
# # inverted = cv2.bitwise_not(cl1)


# ### QUALITY CHECK ###

# # Check for motion blur
# blur_threshold = 100
# laplacian_var = cv2.Laplacian(cl1, cv2.CV_64F).var()
# print(f'Motion Blur: {laplacian_var}')
# motion_blur = laplacian_var > blur_threshold
# print(f'Motion Blur: {laplacian_var > blur_threshold}') 

# # Check background removal
# bg_removal_threshold = 0.1
# non_black = cv2.countNonZero(threshold)
# total = cl1.shape[0] * cl1.shape[1]
# print(f'Bg removal: {(non_black / total)}')
# bg_removal = (non_black / total) > bg_removal_threshold
# print(f'Bg removal: {(non_black / total) > bg_removal_threshold}')


# # Check ridge contrast
# min_range = 30
# print(f'Ridge Contrast: {(cl1.max() - cl1.min())}')
# ridge_contrast = (cl1.max() - cl1.min()) > min_range
# print(f'Ridge Contrast: {(cl1.max() - cl1.min()) > min_range}') 

# # Checks for good fingerprint coverage
# min_area_ratio = 0.2
# _, thresh = cv2.threshold(cl1, 10, 255, cv2.THRESH_BINARY)
# contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# if contours:
#     largest_contour = max(contours, key=cv2.contourArea)
#     area = cv2.contourArea(largest_contour)
#     total_area = cl1.shape[0] * cl1.shape[1]
#     print(f'Coverage: {(area / total_area)}')
#     coverage = (area / total_area) > min_area_ratio
#     print(f'Coverage: {(area / total_area) > min_area_ratio}')
# else:
#     print('Coverage: False')

# #print(threshold[0])

# # # Save Image
# # img = cv2.GaussianBlur(inverted,(3,3),1)
# # kernel = np.ones((2,2),np.uint8)
# # opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
# # Final = cv2.adaptiveThreshold(opening,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
# #              cv2.THRESH_BINARY,17,1)




# cv2.imwrite('RAW_PREPROCESS_TEST.jpg',thresh)

# # edges = cv2.Canny(Final, 0,200)


# # cv2.imshow('edges',inverted)
# # cv2.waitKey(0)

# # cv2.destroyAllWindows()

# index = 0
# arr = []
# while True:
#     cap = cv2.VideoCapture(index)
#     if not cap.read()[0]:
#         break
#     else:
#         arr.append(index)
#     cap.release()
#     index += 1
# print(arr)

        # Set Camera to 4k to take picture
        # cap_s = time.perf_counter()
        # # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, PICTURE_RES[0]) 
        # # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PICTURE_RES[1]) 
        # cap_e = time.perf_counter()
        # print(f'capture: {cap_e - cap_s}')

# import tkinter as tk
# from tkinter import filedialog

# def select_file():
#     file_path = filedialog.askopenfilename()
#     if file_path:  # Check if a file was selected
#         print(f"Selected file: {file_path}")

# root = tk.Tk()
# root.withdraw()  # Hide the main Tkinter window

# select_button = tk.Button(root, text="Select File", command=select_file)
# select_button.pack()

# root.mainloop()

import os, sys

print(os.listdir(os.path.join(sys._MEIPASS, ".u2net")))
