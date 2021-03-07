# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:07:57 2021

@author: cryst
"""

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread(r'C:/Users/cryst/Work/Facade_inspection/thermal/thermal_analysis/RGB_IR_fusion/Perspective_transformation/IRgroundtest1_2021_0303/un_distorted/undistortDJI_0942.jpg',0)
ret,thresh = cv.threshold(img,240,255,cv.THRESH_BINARY)
thresh[:950, :] = 0  #remove the top white noise
thresh[2000:, :] = 0  #remove the bottom ~
thresh[:, :1150] = 0  #remove the left ~
thresh[:, 3000:] = 0  #remove the right ~
#thresh[:, :80] = 0
#thresh[:50, :] = 0

cv.imwrite(r'C:/Users/cryst/Work/Facade_inspection/thermal/thermal_analysis/RGB_IR_fusion/Perspective_transformation/IRgroundtest1_2021_0303/un_distorted/threshold_0942.jpg',thresh)