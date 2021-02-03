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
from image_preprocess import crop, dir_create, split_patch, create_current_dir
from build_dataset import train_val_split, create_dirs
from utils import create_image_list, create_folder_list, create_img_label_list

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
        self.data_prep, self.split_ratio = self.setting.get_dataset_prep()
    def training(self):
        #TODO: consider running in parallel
        if {self.ss, self.dc, self.ds} == {False}:
            print('Please choose at least one ML model')
            return 
        
        if self.ss:
            if self.data_prep==1:
                new_path = self.dataset_preprocess(self.ss_dir, self.setting.ss_out_dir)
            self.training_ss()
        if self.dc:
            if self.data_prep==1:
                self.dataset_preprocess(self.dc_dirs[0], self.setting.dc_out_dir)
            self.training_dc()
        if self.ds:
            if self.data_prep==1:
                new_path = self.dataset_preprocess(self.ds_dir, self.setting.ds_out_dir)
                self.training_ds(new_path)
            else:
                self.training_ds()
        # if self.th:
        #     #TODO: might need to change the function once ML model is ready
        #     self.thermal()
    
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
        #execute ss model
        os.chdir('/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/')
        process = Popen(["/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/test/test_v2_ourdata.sh %s %s" %(ss_txt, ss_out_dir)], 
                stdout=PIPE, shell=True, universal_newlines=True)
        #print real-time output
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Semantic segmentation inference process is completed')
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
                print('Defect classification inference process is completed')
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
                print('Defect segmentation inference process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        #process.communicate()
    
    def training_ss(self):
        '''
        Run training on semantic segmentation model.
        '''
        if self.ss_dir is not None:
            train_txt = create_ss_img_label_list(self.ss_dir, 'ss')
        else:
            print('Please choose training dataset')
            return
            
        if self.setting.ss_out_dir is not None:
            val_txt = create_ss_img_label_list(self.ss_out_dir, 'ss')
        else:
            print('Please choose validation dataset')
            return
            
        #execute ss model
        os.chdir('/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/')
        process = Popen(["/home/paul/Workspaces/python/sematic_segmentation/refinenet-pytorch/train/train_v2_ourdata.sh %s %s %s %s" \
                         %(self.ss_dir, self.ss_out_dir, train_txt, val_txt)], 
                         stdout=PIPE, shell=True, universal_newlines=True)
        #print real-time output
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Semantic segmentation training process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
    
    def training_dc(self):
        '''
        Run training on defect classification model.
        '''
        pass

    def training_ds(self, new_path=None):
        '''
        Run training on defect segmentation model.
        '''
        if self.data_prep==0:
            if self.ss_dir is not None and self.setting.ss_out_dir is not None:
                train_txt = create_img_label_list(self.ss_dir, 'ds')
                val_txt = create_img_label_list(self.ss_out_dir, 'ds')
            else:
                print('Please choose training/validation dataset')
                return
        else:
            train_path = os.path.join(new_path, 'train')   
            test_path = os.path.join(new_path, 'test')
            train_txt = create_img_label_list(train_path, 'ds')
            val_txt = create_img_label_list(test_path, 'ds')
                
    def dataset_preprocess(self, input_path, output_path):
        '''
        prepare dataset ready for training.

        '''
        if input_path is not None:
        	input_path = input_path+'/'
            
        else:
        	print('Please indicate the input directory')
        	return
     
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        #output_path = output_path+'/'
        prev_path, new_path = create_current_dir(output_path)
        labelme_dir = new_path +'/labelme_output/'
        image_dir = os.path.join(new_path, 'all', '640x480_images')   
        label_dir = os.path.join(new_path, 'all', '640x480_labels')

        process = Popen(["python /Data/Research/git/labelme/examples/instance_segmentation/labelme2voc.py %s %s --labels %s" \
                         %(input_path, labelme_dir, os.path.join(input_path, 'class_names.txt'))], 
                         stdout=PIPE, shell=True, universal_newlines=True)
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
                
        image1_path = os.path.join(labelme_dir, 'JPEGImages')
        label1_path = os.path.join(labelme_dir, 'SegmentationClassPNG')
        split_patch(image1_path, label1_path, prev_path, new_path, 480, 640)
        
        if self.split_ratio != 0.0:
            train_val_split(image_dir, label_dir, new_path, self.split_ratio)
        else:
            train_val_split(image_dir, label_dir, new_path)

        return new_path
            
#TODO: no ML model for thermal analysis now, add inference/training once model is confirmed
    #def thermal(self):
        # '''
        # Run thermal analysis using IR images. 
        # - purpose: 
        # -----------
        # Output:
        #     -
        # '''
    
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