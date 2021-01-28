# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 14:43:28 2021

@author: cryst
"""
import os
import sys
import shutil
import glob
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

def rescale(filename):
    '''
    Rescale image to 640x480 (might not be useful, depends on image quality)

    Parameters
    ----------
    filename : str
        name of the image file.
    '''
    img = Image.open(filename)
    size = (640, 480)
    img.thumbnail(size, Image.ANTIALIAS)
    img.save(filename)

def crop(input_file, height, width):
    img = Image.open(input_file)
    img_width, img_height = img.size
    for i in range(img_height//height):
        for j in range(img_width//width):
            box = (j*width, i*height, (j+1)*width, (i+1)*height)
            yield img.crop(box)
            
def dir_create(path):
    '''
    creating a new directory and recursively deleting the contents of an 
    existing directory.
    '''
    if (os.path.exists(path)) and (os.listdir(path) != []):
        shutil.rmtree(path)
        os.makedirs(path)
    if not os.path.exists(path):
        os.makedirs(path)
            
def split(input_img_dir, input_label_dir, out_dir, height, width, start_num):
    image_dir = os.path.join(out_dir, 'images')
    label_dir = os.path.join(out_dir, 'labels')
    dir_create(out_dir)
    dir_create(image_dir)
    dir_create(label_dir)
    img_list = [f for f in
                os.listdir(input_img_dir)
                if os.path.isfile(os.path.join(input_img_dir, f))]
    file_num = 0
    for infile in img_list:
        infile_path = os.path.join(input_img_dir, infile)
        for k, piece in enumerate(crop(infile_path,
                                       height, width), start_num):
            img = Image.new('RGB', (width, height), 255)
            img.paste(piece)
            img_path = os.path.join(image_dir, 
                                    infile.split('.')[0]+ '_'
                                    + str(k).zfill(1) + '.png')
            img.save(img_path)
        infile_path = os.path.join(input_label_dir,
                                   infile.split('.')[0] + '.png')
        for k, piece in enumerate(crop(infile_path,
                                       height, width), start_num):
            msk = Image.new('RGB', (width, height), 255)
            msk.paste(piece)
            msk_path = os.path.join(label_dir,
                                    infile.split('.')[0] + '_'
                                    + str(k).zfill(1) + '.png')
            msk.save(msk_path)
        file_num += 1
        sys.stdout.write("\rFile %s was processed." % file_num)
        sys.stdout.flush()
        
def image_patch_plotter(images_path, offset):
    '''
    show all parts of the splitted image, the original image is divided into 9 patches

    Parameters
    ----------
    images_list : list
        list of patches to render.
    offset : int
    '''
    images_list = glob.glob(os.path.join(images_path, '*.png'))
    fig = plt.figure(figsize=(12, 10))
    columns = 3
    rows = 3
    ax = []
    for i in range(columns*rows):
        # create subplot and append to ax
        img = mpimg.imread(images_list[i+offset])
        ax.append(fig.add_subplot(rows, columns, i+1))
        ax[-1].set_title('image patch number '+ str(i+1))
        plt.imshow(img)
    plt.show() 
    
def image_label_plotter(image_path, label_path, image_number=None):
    '''
    Render the original image with its label.

    Parameters
    ----------
    image_path : str
    label_path : str
    image_number : int, optional
        if not specified, it'll render a random image from the image list
    '''
    input_images_list = glob.glob(os.path.join(image_path, '*.jpg'))
    input_labels_list = glob.glob(os.path.join(label_path, '*.png'))
    if image_number is None:
        image_number = random.randint(0, len(input_images_list)-1)
    # for i, (image_path, label_path) in enumerate(zip(input_images_list,
    #                                             input_labels_list)):
    image_path, label_path = input_images_list[image_number-1],\
                             input_labels_list[image_number-1]
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(18, 9))
    image = mpimg.imread(image_path)
    label = mpimg.imread(label_path)
    ax1.set_title('Image ' + str(image_number))
    ax1.imshow(image)
    ax2.imshow(label)
    ax2.set_title('Label ' + str(image_number))

if __name__ == '__main__':
    # image_path = r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\image'
    # label_path = r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\label'
    # image_label_plotter(image_path, label_path)
    # output_images_list = glob.glob(r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\images' + '\*.png')
    # output_labels_list = glob.glob(r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\labels' + '\*.png')  
    image_patch_plotter(r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\labels', 0)
    #image_part_plotter(output_labels_list, 0)
    # split(r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\image', 
    #       r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\label', 
    #       r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test', 480, 640, 1)
    #rescale_image('C:/Users/cryst/Work/Facade_inspection/pipeline_design/DJI_0015_org.jpg')