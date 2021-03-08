# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:55:36 2021

@author: cryst
"""
import os
import numpy as np
import cv2

def find_homography(rgb_dir, ir_dir, draw=False):
    '''
    using findHomography (can use more than 4 reference points)
    make sure npy files and image files are in the same directory

    Parameters
    ----------
    rgb_dir : str
    ir_dir : str
    draw: boolean, optional
        Merge mapped RGB and IR to visualize the mapping. The default is False.

    Returns
    -------
    matrix : numpy array
        Transformation matrix. Will be saved under npy file, follow the name of 
        RGB image
    match_ratio : float
        How many features are sucessfully matched (how accurate is the mapping)
    '''
    
    #get filename
    rgb_features_dir = os.path.splitext(rgb_dir)[0] + '.npy'
    ir_features_dir = os.path.splitext(ir_dir)[0] + '.npy'
    #Locate points of the documents or object which you want to transform
    with open(rgb_features_dir, 'rb') as f_rgb:
        features_rgb = np.load(f_rgb)
    
    with open(ir_features_dir, 'rb') as f_ir:
        features_ir = np.load(f_ir)

    #delete the features in both RGB & IR features if there's zero in either x or y
    for i in reversed(range(9)):
        if 0 in features_rgb[i] or 0 in features_ir[i]:
            features_rgb = np.delete(features_rgb, i, axis=0)
            features_ir = np.delete(features_ir, i, axis=0)

    RANSAC_REPROJ_THRESHOLD = 3.0
    matrix, status = cv2.findHomography(features_rgb, features_ir, cv2.RANSAC, 
                                        RANSAC_REPROJ_THRESHOLD)
    
    #save matrix to npy file
    matrix_dir = os.path.splitext(rgb_dir)[0] + '_matrix.npy'
    with open(matrix_dir, 'wb') as f:
        np.save(f, matrix)
        
    print('%d / %d  inliers/matched' % (np.sum(status), len(status)))
    match_ratio = np.sum(status)/len(status)

    img_rgb = cv2.imread(rgb_dir)
    ir_size = tuple(reversed(cv2.imread(ir_dir, 0).shape))

    output = cv2.warpPerspective(img_rgb, matrix, ir_size) 
    output_dir = os.path.splitext(rgb_dir)[0] + '_mapped.jpg'
    cv2.imwrite(output_dir,output)
    
    #merge the two images to visualize the mapping of RGB image
    if draw:
        ir = cv2.imread(ir_dir)
        add_img = cv2.addWeighted(output, 0.5, ir, 0.5, 0)
        merge_dir = os.path.splitext(rgb_dir)[0] + '_merge.jpg'
        cv2.imwrite(merge_dir, add_img)
    return matrix, match_ratio

def save_all_matrix(folder):
    
    file_list = os.listdir(folder)
    matrix_dict = {}
    for matrix_dir in file_list:        
        key = matrix_dir[:2]
        with open(os.path.join(folder, matrix_dir), 'rb') as f:
            matrix = np.load(f)
        matrix_dict[key] = matrix
    #print(matrix_dict)
    np.save(os.path.join(folder, 'all_matrix.npy'), matrix_dict) 
    
def load_all_matrix(file):
    # Load
    matrix_dict = np.load(file, allow_pickle='TRUE').item()
    return matrix_dict

if __name__ == '__main__':
    # print(find_homography('IRgroundtest1_2021_0303/un_distorted/undistortDJI_0942.jpg',
    #                       'IRgroundtest1_2021_0303/un_distorted/undistortDJI_0941_R_thermal_gray.jpg',
    #                       True))
    #save_all_matrix(r'C:/Users/DINGMAN/Desktop/matrix')
    print(load_all_matrix(r'C:/Users/DINGMAN/Desktop/matrix/all_matrix.npy'))