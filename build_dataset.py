# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:43:25 2021

@author: cryst
"""
import random
import os
import shutil
import sys

def train_val_split(input_img_dir, input_label_dir, out_dir, split_ratio=0.9):
    '''
    Split original dataset into training and validation datasets based on 
    the split ratio
    '''
    filenames = [f for f in
                    os.listdir(input_img_dir)
                    if os.path.isfile(os.path.join(input_img_dir, f))]
    filenames.sort()  # make sure that the filenames have a fixed order before shuffling
    random.seed(0)
    random.shuffle(filenames) # shuffles the ordering of filenames 
    #(deterministic given the chosen seed)
    split = int(split_ratio * len(filenames))
    train_filenames = filenames[:split]
    dev_filenames = filenames[split:]
    
    train_img_dir, train_label_dir, dev_img_dir, dev_label_dir = create_dirs(out_dir)
    
    for item in train_filenames:
        source_img = os.path.join(input_img_dir, item)
        source_label = os.path.join(input_label_dir,
                                   item.split('.')[0] + '.png')
        shutil.copy2(source_img, train_img_dir)
        shutil.copy2(source_label, train_label_dir)
        
    for file in dev_filenames:
        source_img = os.path.join(input_img_dir, file)
        source_label = os.path.join(input_label_dir,
                                   file.split('.')[0] + '.png')
        shutil.copy2(source_img, dev_img_dir)
        shutil.copy2(source_label, dev_label_dir)
        
    sys.stdout.write("Training validation datasets are ready")
    sys.stdout.flush()
        
def create_dirs(out_dir):
    '''
    create necessary directories to put train/val data
    train, test, img, labels

    '''
    train_img_dir = os.path.join(out_dir, 'train', 'img')
    train_label_dir = os.path.join(out_dir, 'train', 'labels')
    dev_img_dir = os.path.join(out_dir, 'test', 'img')
    dev_label_dir = os.path.join(out_dir, 'test', 'labels')
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    dir_create(train_img_dir)
    dir_create(train_label_dir)
    dir_create(dev_img_dir)
    dir_create(dev_label_dir)
    return train_img_dir, train_label_dir, dev_img_dir, dev_label_dir
    
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
    
    
if __name__ == '__main__':
    image_path = r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\images'
    label_path = r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\labels'
    out_path = r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test'
    train_val_split(image_path, label_path, out_path, 0.9)
    # create_dirs(r'C:\Users\cryst\Work\Facade_inspection\Test_image\Photo\test\dateset')
