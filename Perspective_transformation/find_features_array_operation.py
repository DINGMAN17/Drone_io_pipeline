# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 20:45:26 2021

@author: DINGMAN
"""
import os
import cv2
import numpy as np
from itertools import combinations_with_replacement

def remove_noise_check(input_dir, remove_noise):
    '''
    check if the white noise has been sucessfully removed
    '''
    img = cv2.imread(input_dir,0)
    if 'thermal' in input_dir:
        ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    else:
        ret,thresh = cv2.threshold(img,240,255,cv2.THRESH_BINARY)
    
    if remove_noise is not None:
        top,bottom,left,right = remove_noise
        if top is not None:
            thresh[:top, :] = 0  #remove the top white noise
        if bottom is not None:
            thresh[bottom:, :] = 0  #remove the bottom ~
        if left is not None:
            thresh[:, :left] = 0  #remove the left ~
        if right is not None:
            thresh[:, right:] = 0  #remove the right ~
    
    filename = os.path.split(input_dir)[-1].split('.')[0]+'_threshold.jpg'
    cv2.imwrite(filename,thresh)

def find_features(input_dir, draw=False, remove_noise=(950,2000,1150,3000),
                  min_pixel=0, pts=9):
    '''
    Use array operation to find the middle point of each feature

    Parameters
    ----------
    input_dir : str
    draw : Boolean, optional
        Draw the middle points on each feature. The default is False.
    remove_noise: list, optional
        remove white noise, follow the sequence [top, bottom, left, right]
    min_pixel : int, optional
        A threshold value, below which the feature is neglected. T
    pts : int, optional
        How many features to be included(9 or 8)

    Returns
    -------
    features : numpy array
        middle points of all the features selected. Also saved in a npy file,
        filenmae follow the image file name.

    '''
    #apply thresholding
    img = cv2.imread(input_dir, 0)
    if 'thermal' in input_dir:
        ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    else:
        ret,thresh = cv2.threshold(img,240,255,cv2.THRESH_BINARY)
    #clean up the random white noise pixel
    if remove_noise is not None:
        top,bottom,left,right = remove_noise
        if top is not None:
            thresh[:top, :] = 0  #remove the top white noise
        if bottom is not None:
            thresh[bottom:, :] = 0  #remove the bottom ~
        if left is not None:
            thresh[:, :left] = 0  #remove the left ~
        if right is not None:
            thresh[:, right:] = 0  #remove the right ~
    
    #get the index of all the white pixels
    result = np.where(thresh==255)
    
    #get boundary of white pixels
    x_max, x_min = max(result[1]), min(result[1])
    y_max, y_min = max(result[0]), min(result[0])
    
    #divided into three regions based on the boundary
    x_1 = x_min + (x_max - x_min) /3
    x_2 = x_max - (x_max - x_min) /3
    y_1 = y_min + (y_max - y_min) /3
    y_2 = y_max - (y_max - y_min) /3 
    
    #create empty arrays to store middle points
    x_mid_arr = []
    y_mid_arr = []
    
    #consider the feature within each region (y)
    for (y_prev, y) in [(y_min, y_1), (y_1, y_2), (y_2, y_max)]:
        idx_x = np.where((result[0]>=y_prev) & (result[0]<=y))
        #sort the array, get the unique values
        x_arr_raw = np.unique(np.sort(result[1][idx_x]))
        x_arr_subtract1 = x_arr_raw.copy()[:-1]
        x_arr_subtract2 = x_arr_raw.copy()[1:]
        x_arr = [(x1, x2) for (x2, x1) in zip(x_arr_subtract2, x_arr_subtract1) 
                  if x2 - x1 > 1]
        x_arr.extend([x_arr_raw[0], x_arr_raw[-1]])
        #print(x_arr)
        #find middle point         
        if pts==8 and y==y_2:
            x0, x3 = x_arr[-2], x_arr[-1]
            x1, x2 = x_arr[0]
            x_mid = [x_prev+(x_next-x_prev)/2 if x_next-x_prev > min_pixel else 0
                      for (x_prev, x_next) in [(x0, x1), (x2, x3)]]
            x_mid.append(0)
            
        else:
            x0, x5 = x_arr[-2], x_arr[-1]
            x1, x2 = x_arr[0]
            x3, x4 = x_arr[1]
            #if condition to make sure the point that are too small is excluded
            x_mid = [x_prev+(x_next-x_prev)/2 if x_next-x_prev > min_pixel else 0
                      for (x_prev, x_next) in [(x0, x1), (x2, x3), (x4, x5)]]
        x_mid_arr.append(x_mid)
    #print(x_mid_arr)
              
    #consider the feature within each region (x)
    for (x_prev, x) in [(x_min, x_1), (x_1, x_2), (x_2, x_max)]:
        idx_y = np.where((result[1]>=x_prev) & (result[1]<=x))
        #sort the array, get the unique values
        y_arr_raw = np.unique(np.sort(result[0][idx_y]))
        #find the discontinuity in the white pixels
        y_arr_subtract1 = y_arr_raw.copy()[:-1]
        y_arr_subtract2 = y_arr_raw.copy()[1:]
        y_arr = [(y1, y2) for (y2, y1) in zip(y_arr_subtract2, y_arr_subtract1) 
                  if y2 - y1 > 1]
        y_arr.extend([y_arr_raw[0], y_arr_raw[-1]])
        #find middle point 
        if pts==8 and x==x_max:
            y0, y3 = y_arr[-2], y_arr[-1]
            y1, y2 = y_arr[0]
            y_mid = [y_prev+(y_next-y_prev)/2 if y_next-y_prev > min_pixel else 0
                      for (y_prev, y_next) in [(y0, y1), (y2, y3)]]
            y_mid.insert(1, 0)
        else:
            y0, y5 = y_arr[-2], y_arr[-1]
            y1, y2 = y_arr[0]
            y3, y4 = y_arr[1]
            y_mid = [y_prev+(y_next-y_prev)/2 if y_next-y_prev > min_pixel
                      else 0 for (y_prev, y_next) in [(y0, y1), (y2, y3), (y4, y5)]]
            
        y_mid_arr.append(y_mid)
    #print(y_mid_arr)
    
    #match the x, y coordinates of points
    features = []

    for (i, j) in list(combinations_with_replacement([0,1,2], 2)):        
        features.append((x_mid_arr[i][j], y_mid_arr[j][i]))
        if i != j:
            features.append((x_mid_arr[j][i], y_mid_arr[i][j]))

    #print(features)
    if draw:
        img_name = os.path.split(input_dir)[-1].split('.')[0]+'_draw.jpg'
        for (y, x) in features:
            cv2.rectangle(thresh, (int(y) - 2, int(x) - 2), (int(y) + 2, int(x) + 2), 
                          (0,255,0), -1)
            cv2.imwrite(img_name,thresh)
        #plt.imshow(thresh)
        
    #save features
    filename = os.path.split(input_dir)[-1].split('.')[0]+'.npy'
    with open(filename, 'wb') as f:
        np.save(f, features)
        print('saved', filename)
    return features


    
    
    
    
if __name__ == '__main__':
    
    # print(remove_noise_check(r'IRgroundtest1_2021_0303/un_distorted/undistortDJI_0858.jpg', 
    #                           None))
    print(find_features(r'IRgroundtest1_2021_0303/un_distorted/undistortDJI_0926.jpg', 
                        True,(950,2000,1150,3000)))


