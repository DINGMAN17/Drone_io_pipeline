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
    circles : center and radius of each circle detected, numpy array
    '''
    img = cv2.imread(input_file)
    output = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Finds circles in a grayscale image using the Hough transform
    if RGB:
        filename = 'rgb_features.npy'
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, minDist=10,
                                   minRadius=10, maxRadius=60)
    else:
        filename = 'ir_features.npy'
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 5, minDist=2,
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
    
    return circles

#find_features('DJI_0789_R_thermal_gray.jpg', None, False)               

def get_transformation(input_rgb, output_file):
    #using getperspectivetransform(can only use 4 reference points)
    
    # Locate points of the documents or object which you want to transform
    # with open('ir_features.npy', 'rb') as f:
    #     features = np.load(f)
       
    pts_ir = np.float32([[77.5, 57.5], [557.5, 82.5], [567.5, 367.5], [117.5, 362.5]]) 
    pts_rgb = np.float32([[1122.6, 849.0], [2763.0, 924.6], [2797.8, 1907.4], [1229.4, 1902.6]]) 
      
    # Apply Perspective Transform Algorithm 
    img = cv2.imread(input_rgb)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    matrix = cv2.getPerspectiveTransform(pts_rgb, pts_ir) 
    output = cv2.warpPerspective(img, matrix, (640, 512)) 
    cv2.imwrite(output_file,output)
    return matrix
    
print(get_transformation('DJI_0792.jpg', 'DJI_0792_transform.jpg'))

def find_homography(input_file, output_file):
    #using findHomography (can use more than 4 reference points)
    RANSAC_REPROJ_THRESHOLD = 3.0
    pts_ir = np.float32([[77.5, 57.5], [557.5, 82.5], [567.5, 367.5], [117.5, 362.5], [337.5, 257.5]]) 
    pts_rgb = np.float32([[1122.6, 849.0], [2763.0, 924.6], [2797.8, 1907.4], [1229.4, 1902.6], [2011.8, 1511.4]]) 
    matrix, _ = cv2.findHomography(pts_rgb, pts_ir, cv2.RANSAC, RANSAC_REPROJ_THRESHOLD)
    
    img = cv2.imread(input_file)
    output = cv2.warpPerspective(img, matrix, (640, 512)) 
    cv2.imwrite(output_file,output)
    return matrix

#print(find_homography('DJI_0792.jpg', 'DJI_0792_homography.jpg'))

def merge_images(rgb_dir, ir_dir, output_file):
    #merge the RGB and IR images to check if the transformation is accuracte
    rgb = cv2.imread(rgb_dir)
    ir = cv2.imread(ir_dir)
    add_img = cv2.addWeighted(rgb, 0.4, ir, 0.6, 0)
    cv2.imwrite(output_file, add_img)
    
#merge_images('DJI_0792_homography.jpg', 'DJI_0789_R_thermal_gray.JPG', 'merge_img.jpg')
#merge_images('DJI_0792_transform.jpg', 'DJI_0789_R_thermal_gray.JPG', 'merge_tranform.jpg')

    