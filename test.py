import cv2
import numpy
import torch

list = []

image1 = cv2.imread(r"C:\Users\LAB-PC\Documents\code\jupyter\SDIP Model\SOCOFing\Real\1__M_Left_index_finger.BMP")
image2 = cv2.imread(r"C:\Users\LAB-PC\Documents\code\jupyter\SDIP Model\SOCOFing\Real\1__M_Left_middle_finger.BMP")
print(image1.shape)
image1 = cv2.cvtColor(image1,cv2.COLOR_BGR2RGB)
list.append(image1)
list = numpy.array(list)
list = torch.tensor(list)
print(list[0])