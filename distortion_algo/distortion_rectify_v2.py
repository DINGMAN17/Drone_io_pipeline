# -*- coding: utf-8 -*-

# =============================================================================
# reference web site
# https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
# =============================================================================

# =============================================================================
# Date: 2021/2/11
# Outline: rectify original images to undistorted images 
# =============================================================================

import numpy as np
import cv2 as cv
import glob
import os

def correct_distortion(input_path, rgb=True, output_path=None):
    # create output path
    if output_path is not None:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    
    # load parameters
    if rgb:
        parameter_arry = np.load('calibration_parameters_rgb.npy', allow_pickle=True)
        prefix = '*.jpg'

    else:
        parameter_arry = np.load('calibration_parameters_ir.npy', allow_pickle=True)
        prefix = '*.JPG'
    
    err, KK, distCoeffs, rvecs, tvecs = parameter_arry[:]

    # read images
    images = glob.glob(os.path.join(input_path, prefix))
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
        img_type = os.path.split(fname)
        img_name1 = 'undistort' + img_type[-1]
        img_name2 = 'undistort_remove' + img_type[-1]
        if output_path is not None:
            output_dir = output_path
        else:
            output_dir = input_path

        cv.imwrite(os.path.join(output_dir, img_name1), undistortedImage1)
        cv.imwrite(os.path.join(output_dir, img_name2), undistortedImage2)
        
        # # show results
        # cv.imshow('undistortedImage1', undistortedImage1)
        # cv.imshow('undistortedImage2', undistortedImage2)
        # cv.waitKey()
        
        # display the result
        print(fname + ': undistorted and cropped')

correct_distortion('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/RGB_IR_overlay/thermal_analysis/calibration_rgb_raw/', True, 
                    '/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/RGB_IR_overlay/thermal_analysis/calibration_rgb_undistort/')