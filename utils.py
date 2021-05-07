# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 16:21:46 2021

@author: cryst
"""
import os

def create_image_list(folder_path=None, model=None, file_type='.JPG'):
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

def create_folder_list(dirs=None, model=None):
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
    #if model == 'th':
    #    filename = '/home/paul/Workspaces/matlab/thermal/input_thermal.txt'
    #else:
    #    filename = model + '_test_dirs.txt'
    filename = model + '_test_dirs.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(dirs))
    
    return os.path.abspath(filename)

def create_ss_img_label_list(folder_path=None, model=None):
    '''
    create a txt file which contains the absolute path of all image and its corresponding label.
    the txt file will be fed into semantic segmantation model for training/validation.

    Parameters
    ----------
    folder_path : TYPE, str 
    model : TYPE, str
    
    Returns
    -------
    path of the txt file

    '''
    
    img_path = os.path.join(folder_path, 'img')
    label_path = os.path.join(folder_path, 'labels')
    txt_file = model + '_img_label_list.txt'
    filename = os.path.join(folder_path, txt_file)
    with open(filename, 'w') as f:
        f.writelines([os.path.join(img_path, img) +'\t'+ os.path.join(label_path, label)+'\n'
                      for img,label in zip(os.listdir(img_path), os.listdir(label_path))])
    
    return os.path.abspath(filename)

def create_dirs(dir_list, parent_dir):
    '''
    create a list of sub-folders under parent folder

    '''
    for folder in dir_list:
            folder = os.path.join(parent_dir, folder)
            if not os.path.exists(folder):
                os.mkdir(folder)

def rename_dir(folder, start_no=1):
    '''
    rename the images in each facade folder, starting from DJI_0001.JPG

    '''
    img_list = [os.path.splitext(f) for f in os.listdir(folder)
				    if os.path.isfile(os.path.join(folder, f))]

    num_img = len(img_list)-1
    rename_image_num = start_no + num_img
    
    for img in sorted(img_list, reverse=True):
        if img[1].lower() in ['.png', '.jpg', '.jpeg']:
            img_path = os.path.join(folder, 
								'DJI_'+str(rename_image_num).zfill(4)+img[1])

            rename_image_num -= 1
            os.rename(os.path.join(folder, img[0]+img[1]), img_path)
            
    return len(img_list)
    
if __name__ == '__main__':
    #txt = create_ss_img_label_list(r"C:\Users\cryst\Work\pipeline_design\Drone_io_pipeline-main\training", 'ss')
    rename_dir(r'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/DCIM/test_rename', 58)
