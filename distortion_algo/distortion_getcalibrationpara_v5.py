# -*- coding: utf-8 -*-

# =============================================================================
# reference web site
# https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
# (japanese)　https://www.qoosky.io/techs/67a3d876c4
# =============================================================================

# =============================================================================
# Date: 2021/2/11
# Outline: get camera parameters to undistort images 
# ## v1
# - save images to each folder
# ## v2
# - export re projection errors
# - Variable number of corners
# ## v3
# - cv.findChessboardCorners --> change parameters by find_flags
# - display whether program finds corners in images
# ## v4
# - written in function
# =============================================================================

# =============================================================================
#           # input
# calibration images: folder '10_calibration_img_data'
#                     chessboard, rgb, opencv sample imaged
#           # output
# calibration_parameters: calibration_parameters.npy
# chessboard images with coners: folder '11_calibration_img_data_corner'
# =============================================================================

import numpy as np
import cv2 as cv
import glob
import os

def get_camera_parameters(number_rows, number_cols, input_folder, print_params=False):
    '''
    get camera parameters to undistort images
    -output images saved in '11_calibration_img_data_corner'
    -output parameter saved in '11_calibration_img_data_corner'
    
    Parameters
    ----------
    number_rows : int
    number_cols : int
    input_folder : str
    print_params : boolean, optional
        whether to print the camera parameters

    Returns
    -------
    
    '''
    
    # Chessboard : point number of rows/columns
        
    # findChessBoard flags
    # find_flags = None
    find_flags = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FILTER_QUADS + cv.CALIB_CB_FAST_CHECK
    # cv.CALIB_CB_ADAPTIVE_THRESH : Use adaptive thresholding to convert the image to black and white
    # cv.CALIB_CB_NORMALIZE_IMAGE : Normalize the image gamma with equalizeHist() before applying fixed or adaptive thresholding.
    # cv.CALIB_CB_FILTER_QUADS : Use additional criteria (like contour area, perimeter, square-like shape) to filter out false quads extracted at the contour retrieval stage.
    # cv.CALIB_CB_FAST_CHECK : Run a fast check on the image that looks for chessboard corners, and shortcut the call if none is found
    
    
    # termination criteria      cornerSubPix の閾値
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    # ワールド座標系におけるキャリブレーションボードの各点の座標 
    objp = np.zeros((number_cols*number_rows, 3), np.float32)
    objp[:,:2] = np.mgrid[0:number_rows, 0:number_cols].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    # キャリブレーションで利用する座標
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    
    # read images
    images = glob.glob(os.path.join(input_folder, '*.jpg')) 
    for fname in images:
        img = cv.imread(fname)
        
        # convert to gray scale グレースケールで利用
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    
       
        # ## image check 
        # cv.imshow(fname, gray)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
    
        # キャリブレーションボード内の点の座標を取得
        # Find the chess board corners
        #TODO: check the original findChessboardCorners function, might need to rewrite
        ret, corners = cv.findChessboardCorners(gray, (number_rows, number_cols), find_flags)
    
        # If found, add object points, image points (after refining them)    
        # キャリブレーションのために結果を保存
        if ret == True:
            objpoints.append(objp)
            
            # improve accurcay of coodinaiton 座標の精度を上げる
            corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            
            # Draw the corners 確認のため画像を表示
            cv.drawChessboardCorners(img, (number_rows, number_cols), corners2, ret)
            # # display the corners
            # cv.imshow(fname, img)      
            
            #TODO: don't overwrite the original image
            # save images with corner point
            img_name = os.path.split(fname)        
            cv.imwrite('11_calibration_img_data_corner/'+ img_name[-1], img)
            
            # display succeed or fail to find corners
            print(fname, ': succeed to find corner')
        else:
            print(fname, ': fail')
    
    
    
    # Calibration parameters
    imageSize = gray.shape[::-1]
    err, KK, distCoeffs, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, imageSize, None, None)
    
    # Save (correct)
    parameter_arry = np.array([err, KK, distCoeffs, rvecs, tvecs])
    np.save('calibration_parameters', parameter_arry)
    
    # # Print calibaration parameters
    if print_params:
        print('err', err)
        print('KK', KK)
        print('distCoeffs', distCoeffs)
        print('rvecs', rvecs)
        print('tvecs', tvecs)
    
    # Re-projection error
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], KK, distCoeffs)
        error = cv.norm(imgpoints[i],imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    print("total error: ", mean_error/len(objpoints))
    error_list = [['mean_error', mean_error], ['len(objpoints)', len(objpoints)], ["total error: ", mean_error/len(objpoints)]]
    np.savetxt('Re_projection_error.csv', error_list, delimiter=',', fmt ='% s')
    
    return err, KK, distCoeffs, rvecs, tvecs

if __name__ == '__main__':
    get_camera_parameters(9, 6, '10_calibration_img_data', True)
