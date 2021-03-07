# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 16:53:11 2021

@author: cryst
"""

import numpy as np
import cv2

def find_features(input_file, output_file=None, RGB=True):
    '''
    Use cv2.HoughCircles function to detect circular features in images.
    Features detected will be saved in a npy file

    Parameters
    ----------
    input_file : input image path, str
    output_file : output image path, str, optional
    RGB : whether the image is RGB or not, Boolean. The default is True.

    Returns
    -------
    features : center of each circle detected, numpy array
                saved in npy file 'rgb_features' or 'ir_features'
    '''
    img = cv2.imread(input_file)
    output = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Finds circles in a grayscale image using the Hough transform
    if RGB:
        filename = 'rgb_features.npy'
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 5, minDist=2,
                                   minRadius=2, maxRadius=100)
    else:
        filename = 'ir_features.npy'
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 7, minDist=2,
                                   minRadius=2, maxRadius=100)
    
    # Check to see if there is any detection
    if circles is not None:
        features = np.squeeze(circles[:, :, :2])
        with open(filename, 'wb') as f:
            np.save(f, features)
        
        # If there are some detections, convert radius and x,y(center) coordinates to integer
        circles_draw = np.round(circles[0, :]).astype("int")
    
        if output_file is not None:
            for (x, y, r) in circles_draw:
                # Draw the circle in the output image
                cv2.circle(output, (x, y), r, (0,255,0), 3)
                # Draw a rectangle(center) in the output image
                cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0,255,0), -1)
                cv2.putText(output, str(x), (x, y), cv2.FONT_HERSHEY_SIMPLEX,  
                   1, (255, 0, 0) , 2, cv2.LINE_AA) 
        
            #cv2.imshow("Detections",output)
            cv2.imwrite(output_file,output)
    
        return features             
    
print(find_features('IRgroundtest1_2021_0303/un_distorted/threshold_254.jpg', 
                    'IRgroundtest1_2021_0303/features/threshold_features.jpg'))

def find_homography(input_file, output_file):
    '''using findHomography (can use more than 4 reference points) to calculate 
    transformation matrix. Based on the matrix, RGB image will be mapped to the
    corresponding IR image. 

    Parameters
    ----------
    input_file : input image path, str
        The RGB image that needs to be mapped
    output_file : mapped image path, str
        resulted RGB image after mapping

    Returns
    -------
    matrix : numpy array
        Transformation matrix. Will be saved under npy file 'tranformation_matrix'
    match_ratio : float
        How many features are sucessfully matched (how accurate is the mapping)
    '''
    #using findHomography (can use more than 4 reference points)
    RANSAC_REPROJ_THRESHOLD = 3.0
    pts_ir = np.float32([[107.5, 352.5], [72.5, 52.5], [332.5, 247.5], [562.5, 357.5], [552.5, 77.5]]) 
    pts_rgb = np.float32([[1199.4, 1656.6], [1096.2, 760.2], [1853.4, 1321.8], [2519.4, 1657.8], [2490.6, 826.2]]) 
    matrix, status = cv2.findHomography(pts_rgb, pts_ir, cv2.RANSAC, RANSAC_REPROJ_THRESHOLD)
    
    #save matrix to npy file
    with open('transformation_matrix', 'wb') as f:
        np.save(f, matrix)
        
    print('%d / %d  inliers/matched' % (np.sum(status), len(status)))
    match_ratio = np.sum(status)/len(status)

    img = cv2.imread(input_file)
    output = cv2.warpPerspective(img, matrix, (627, 494)) 
    cv2.imwrite(output_file,output)
    return matrix, match_ratio

#print(find_homography('undistort_DJI_0792.jpg', 'DJI_0792_homography_undistort.jpg'))

def merge_images(rgb_dir, ir_dir, output_file):
    #merge the RGB and IR images to check if the transformation is accuracte
    rgb = cv2.imread(rgb_dir)
    ir = cv2.imread(ir_dir)
    add_img = cv2.addWeighted(rgb, 0.5, ir, 0.5, 0)
    cv2.imwrite(output_file, add_img)
    
#merge_images('DJI_0792_homography_undistort.jpg', 'undistort_DJI_0789_R_thermal_gray.JPG', 'merge_img_undistort.jpg')
#merge_images('DJI_0792_transform.jpg', 'undistort_DJI_0789_R_thermal_gray.JPG', 'merge_tranform_undistort.jpg')

def get_transformation(input_rgb, output_file):
    #using getperspectivetransform(can only use 4 reference points)
    
    # Locate points of the documents or object which you want to transform
    # with open('ir_features.npy', 'rb') as f:
    #     features = np.load(f)
       
    pts_ir = np.float32([[107.5, 352.5], [72.5, 52.5], [562.5, 357.5], [552.5, 77.5]]) 
    pts_rgb = np.float32([[1199.4, 1656.6], [1096.2, 760.2], [2519.4, 1657.8], [2490.6, 826.2]]) 
      
    # Apply Perspective Transform Algorithm 
    img = cv2.imread(input_rgb)
    matrix = cv2.getPerspectiveTransform(pts_rgb, pts_ir) 
    output = cv2.warpPerspective(img, matrix, (627, 494)) 
    cv2.imwrite(output_file,output)
    return matrix

#find_features('undistort_DJI_0792.jpg', 'undistort_rgb_features.jpg')  
    