# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:52:52 2021

@author: cryst
"""
import os
import sys
from subprocess import PIPE, Popen
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
        self.ss, self.dc, self.ds, self.all_model = [True if model=='Yes' else False 
                                        for model in self.setting.get_model()]

        self.ss_dir, self.dc_dirs, self.ds_dir = self.setting.ss_dir, self.setting.c_dirs, self.setting.ds_dir
        
    def training(self):
        #TODO: consider running in parallel
        if {self.ss, self.dc, self.ds, self.th} == {False}:
            print('Please choose at least one ML model')
            return 
        if self.ss:
            self.training_ss()
        if self.dc:
            self.training_dc()
        if self.ds:
            self.training_ds()
        if self.th:
            #TODO: might need to change the function once ML model is ready
            self.thermal()
    
    def inference(self):
        if {self.ss, self.dc, self.ds, self.all_model} == {False}:
            print('Please choose at least one model')
            return 

        if self.all_model:
            image_txt = create_image_list(self.ss_dir, 'all')
            if self.setting.ss_out_dir is not None:
                output_dir = self.setting.ss_out_dir
            self.inference_ss(image_txt, output_dir)
            self.inference_dc(output_dir=output_dir)
            self.inference_ds(image_txt, output_dir)
            return
        
        if self.ss:
            if self.ss_dir != None:
                self.inference_ss()
            else: 
                print('Please select the test image folder to run semantic \
                      segmentation model')
                return 
            
        if self.dc:
            if self.dc_dirs != []:
                self.inference_dc()
            else: 
                print('Please select the test image folders to run defect \
                      classification model')
                return 
            
        if self.ds:
            if self.ds_dir != None:
                self.inference_ds()
            else: 
                print('Please select the test image folder to run defect \
                      segmentation model')
                return 
    
    def inference_ss(self, input_file=None, output_dir=None):
        '''
        Run inference on semantic segmentation model.
        - purpose: identify strucural elements and mask windows
        -------------
        Output: 
            -folder containts masked window images
            -semantic segmentation images
        '''

        #create a folder named 'semantic' in the output directory to store results.
        if output_dir is not None:
            ss_out_dir = output_dir+'/semantic/'
            if not os.path.exists(ss_out_dir):
                os.mkdir(ss_out_dir)
        if self.setting.ss_out_dir is not None:
            ss_out_dir = self.setting.ss_out_dir+'/semantic/'
            if not os.path.exists(ss_out_dir):
                os.mkdir(ss_out_dir)
        if input_file != None:
            ss_txt = input_file
        else:
            ss_txt = create_image_list(self.ss_dir, 'ss')
        os.chdir('/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/')
        process = Popen(["/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/test/test_v2_ourdata.sh %s %s" %(ss_txt, ss_out_dir)], 
                stdout=PIPE, shell=True, universal_newlines=True)
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Semantic segmentation process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

        #out, err = process.communicate()
    
    def inference_dc(self, input_file=None, output_dir=None):
        '''
        Run inference on defect classification model. 
        - purpose: identify crack, spalling (Delamination)
        -----------
        Output:
            -folder named by IDs, contains crack, spalling images and folders with defect patches    
        '''
        upload, buildID, facadeID, flyID = self.setting.get_dc_details()

        if output_dir is not None:
            dc_out_dir = output_dir+'/classification/'
            if not os.path.exists(dc_out_dir):
                os.mkdir(dc_out_dir)
        if self.setting.dc_out_dir is not None:
            dc_out_dir = self.setting.dc_out_dir+'/classification/'
            if not os.path.exists(dc_out_dir):
                os.mkdir(dc_out_dir)

        if self.all_model == True:
            self.dc_dirs.append(self.ss_dir)
        dc_txt = create_folder_list(self.dc_dirs, 'dc')

        os.chdir('/home/paul/Workspaces/python/defect_classification/combine_process/')
        if upload != 'Yes': #don't upload for testing purpose
            process = Popen(["/home/paul/Workspaces/python/defect_classification/combine_process/run_check_defects.sh %s %s %s %s %s" 
                        %(dc_txt,buildID,facadeID,flyID,dc_out_dir)], stdout=PIPE, shell=True, universal_newlines=True)
        else:
            print('upload the results to cloud database')
            #process = Popen(["/home/paul/Workspaces/python/defect_classification/combine_process/run_check_defects.sh %s %s %s %s %s -uploading" 
                        #%(dc_txt,buildID,facadeID,flyID,dc_out_dir)], stdout=PIPE, shell=True, universal_newlines=True)
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Defect classification process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        #process.communicate()
        

    
    def inference_ds(self, input_file=None, output_dir=None):
        '''
        Run inference on defect segmentation model. 
        - purpose: identify Spalling, Efflorescence, Rust
        -----------
        Output:
            -defect segmentation images
        '''
        if input_file != None:
            ds_txt = input_file
        else:
            ds_txt = create_image_list(self.ds_dir, 'ds')

        if output_dir is not None:
            ds_out_dir = output_dir+'/defect_seg/'
            if not os.path.exists(ds_out_dir):
                os.mkdir(ds_out_dir)
        if self.setting.ds_out_dir is not None:
            ds_out_dir = self.setting.ds_out_dir+'/defect_seg/'
            if not os.path.exists(ds_out_dir):
                os.mkdir(ds_out_dir)
        os.chdir('/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/')
        process = Popen(["/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/test/test_v2_ourdata_ds.sh %s %s" 
                         %(ds_txt,ds_out_dir)], stdout=PIPE, shell=True, universal_newlines=True)
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Defect segmentation process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        #process.communicate()
          
    #TODO: no ML model for thermal analysis now, add inference/training once model is confirmed
    #def thermal(self):
        '''
        Run thermal analysis using IR images. 
        - purpose: 
        -----------
        Output:
            -
        '''
    
        #th_txt = create_folder_list(self.th_dirs, 'th')
        #if self.setting.th_out_dir is not None:
            #th_out_dir = self.setting.th_out_dir+'/thermal/'
            #if not os.path.exists(th_out_dir):
            #    os.mkdir(th_out_dir)
        #os.chdir('/home/paul/Workspaces/matlab/thermal')
        #process = Popen(["python3 /home/paul/Workspaces/matlab/thermal/get_all_thermal_data.py -input_file %s -out_dir %s"
        #                %(th_txt, th_out_dir)], stdout=PIPE, shell=True)
        #process.communicate()
        #print('thermal process completed')
    
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