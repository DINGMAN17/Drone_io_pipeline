# -*- coding: utf-8 -*-

# =============================================================================
# reference web site
# https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
# (japanese)　https://www.qoosky.io/techs/67a3d876c4
# =============================================================================

# =============================================================================
# Date: 2021/2/11
# Outline: rectify original images to undistorted images 
# =============================================================================

# =============================================================================
#           # input
# calibration_parameters: calibration_parameters.npy
# original images to undistortion: folder '01_org_img'
#           # output
# output undistorted images: folder '02_undis_img'
# output undistorted images: folder '03_undis_img_roi'
# =============================================================================

import numpy as np
import cv2 as cv
import glob
import os

# load parameters
parameter_arry = np.load('calibration_parameters.npy', allow_pickle=True)
err, KK, distCoeffs, rvecs, tvecs = parameter_arry[:]

## check calibaration parameters
# print('err', err)
# print('KK', KK)
# print('distCoeffs', distCoeffs)
# print('rvecs', rvecs)
# print('tvecs', tvecs)

# read images
images = glob.glob('01_org_img/*.jpg')
for fname in images: 
    targetImage = cv.imread(fname)
    
    # camera array
    targetImageSize = targetImage.shape[:2][::-1]
    alpha = 1  # 1:black
    newKK, roiSize = cv.getOptimalNewCameraMatrix(KK, distCoeffs, targetImageSize, alpha, targetImageSize)
    
    # distotion correct map
    mapX, mapY = cv.initUndistortRectifyMap(KK, distCoeffs, None, newKK, targetImageSize, cv.CV_32FC1)
    
    # distortion
    undistortedImage1 = cv.remap(targetImage, mapX, mapY, cv.INTER_LINEAR)
    
    # remove black parts
    x, y, w, h = roiSize
    undistortedImage2 = undistortedImage1[y:y+h, x:x+w]
    
    # save images
    img_name = os.path.split(fname)
    cv.imwrite('02_undis_img/'+ img_name[-1], undistortedImage1)
    cv.imwrite('03_undis_img_roi/'+ img_name[-1], undistortedImage2)
    
    # # show results
    # cv.imshow('undistortedImage1', undistortedImage1)
    # cv.imshow('undistortedImage2', undistortedImage2)
    # cv.waitKey()
    
    # display the result
    print(fname + ': undistorted and cropped')

cv.destroyAllWindows()