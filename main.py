# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:52:52 2021

@author: cryst
"""
import tkinter as tk
from pipeline_UI import Setting
from utils import create_image_list, create_folder_list

class Run():
    
    def __init__(self):
        self.root = tk.Tk()
        self.setting = Setting(self.root)
        self.reset()        
        
    def reset(self):
        self.root.mainloop()
        self.get_parameters()
        
    def get_parameters(self):
        '''
        Get parameters from GUI

        '''
        self.ss_folder = self.setting.ss_dir
        self.c_dirs = self.setting.c_dirs
    
    def inference_ss(self):
        '''
        Run inference on semantic segmentation model.
        - purpose: identify strucural elements and mask windows
        '''
        ss_test_imgs = create_image_list(self.ss_folder)
        print(ss_test_imgs)
    
    def inference_c(self):
        '''
        Run inference on defect classification model. 
        - purpose: identify crack, spalling (Delamination)
        '''
        c_dirs = create_folder_list(self.c_dirs)
        print(c_dirs)
    
    def inference_ds(self):
        '''
        Run inference on defect segmentation model. 
        - purpose: identify Spalling, Efflorescence, Rust
        '''
        pass
    
    def training_ss(self):
        '''
        Run training on semantic segmentation model.
        '''
        pass
    
    def training_c(self):
        '''
        Run training on defect classification model.
        '''
        pass
    def training_ds(self):
        '''
        Run training on defect segmentation model.
        '''
        pass
    
def main():
    r = Run()
    r.inference_ss()
    r.inference_c()

if __name__ == '__main__':
    main()