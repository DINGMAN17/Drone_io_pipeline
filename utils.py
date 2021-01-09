# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 16:21:46 2021

@author: cryst
"""
import os

def create_image_list(folder_path, file_type='.png'):
    '''
    create a txt file which contains the absolute path of all test images.
    the txt file will be fed into semantic/defect segmentation model.

    Parameters
    ----------
    folder : absolute path of the directory that contains all the test images
    file_type : type of image file
                The default is '.jpg'
    '''   
    #path = "C:/Users/cryst/Study/Thesis/images" #for testing
    path = folder_path 
    file_type = file_type            
        
    with open('ss_test_img_list.txt', 'w') as file:
        file.writelines([os.path.abspath(f)+'\n' for f in os.listdir(path) if f.endswith(file_type)])

    return os.path.abspath('ss_test_img_list.txt')

