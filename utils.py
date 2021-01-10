# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 16:21:46 2021

@author: cryst
"""
import os

def create_image_list(folder_path=None, model=None, file_type='.png'):
    '''
    create a txt file which contains the absolute path of all test images.
    the txt file will be fed into semantic/defect segmentation model.

    Parameters
    ----------
    folder : absolute path of the directory that contains all the test images, str
    file_type : type of image file, str
                The default is '.jpg'
                
    Returns
    -------
    absolute path of the txt file, str
    '''   
    #path = "C:/Users/cryst/Study/Thesis/images" #for testing
    path = folder_path 
    file_type = file_type
    filename = model + '_test_img_list.txt'            
        
    with open(filename, 'w') as file:
        file.writelines([path + '/' + f +'\n' for f in os.listdir(path) if f.endswith(file_type)])

    return os.path.abspath(filename)

def create_folder_list(dirs=None):
    '''
    create a txt file which contains the absolute path of all test image folders.
    the txt file will be fed into classification model.

    Parameters
    ----------
    dirs : TYPE, list
        directories that contain test images

    Returns
    -------
    absolute path of the txt file, str

    '''
    
    dirs = dirs

    with open('c_test_dirs.txt','w') as f:
        f.write('\n'.join(dirs))
    
    return os.path.abspath('c_test_dirs.txt')