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
        self.mode = self.setting.get_mode() #training/inference
        self.ss, self.dc, self.ds = [True if model=='Yes' else False 
                                     for model in self.setting.get_model()]
        self.ss_folder = self.setting.ss_dir
        self.dc_dirs = self.setting.c_dirs
        self.ds_folder = self.setting.ds_dir
        
    def training(self):
        #TODO: consider running in parallel
        if {self.ss, self.dc, self.ds} == {False}:
            print('Please choose at least one ML model')
            return None
        if self.ss:
            self.training_ss()
        if self.dc:
            self.training_dc()
        if self.ds:
            self.training_ds()
    
    def inference(self):
        #TODO: consider running in parallel
        if {self.ss, self.dc, self.ds} == {False}:
            print('Please choose at least one ML model')
            return None
        
        if self.ss:
            if self.ss_folder != None:
                self.inference_ss()
            else: 
                print('Please select the test image folder to run semantic segmentation model')
                return None
            
        if self.dc:
            if self.dc_dirs != []:
                self.inference_dc()
            else: 
                print('Please select the test image folders to run defect classification model')
                return None
            
        if self.ds:
            if self.ds_folder != None:
                self.inference_ds()
            else: 
                print('Please select the test image folder to run defect segmentation model')
                return None
    
    def inference_ss(self):
        '''
        Run inference on semantic segmentation model.
        - purpose: identify strucural elements and mask windows
        '''
        ss_txt = create_image_list(self.ss_folder, 'ss')
        #print(ss_txt)
    
    def inference_dc(self):
        '''
        Run inference on defect classification model. 
        - purpose: identify crack, spalling (Delamination)
        '''
        dc_txt = create_folder_list(self.dc_dirs)
        #print(dc_txt)
    
    def inference_ds(self):
        '''
        Run inference on defect segmentation model. 
        - purpose: identify Spalling, Efflorescence, Rust
        '''
        ds_txt = create_image_list(self.ds_folder, 'ds')
        #print(ds_txt)
    
    def training_ss(self):
        '''
        Run training on semantic segmentation model.
        '''
        pass
    
    def training_dc(self):
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
    if r.mode == "Training" :
        r.training()
        
    elif r.mode == 'Inference':
        r.inference()
        
    else:
        print('Please select training or inference')

if __name__ == '__main__':
    main()