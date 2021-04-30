# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 16:26:07 2021

@author: cryst
"""

import os
import re
import cv2
import sys
import csv
import shutil
from subprocess import PIPE, Popen
from defect_severity import severity_process
from utils import create_image_list, create_folder_list

class Inference():
    def __init__(self, ml_inputs):
        '''
        Parameters
        ----------
        ml_inputs : dict, the output from preprocessing pipeline
        '''
        self.ml_inputs = ml_inputs
        # self.get_parameters()
            
    def get_parameters(self):
        '''
        get the parameters from the dictionary

        Raises
        ------
        Exception
            the output/input folders does not exist;
            building/flight ID not specified

        '''
        self.input_dir = self.ml_inputs['input_dir']
        self.output_dir = self.ml_inputs['output_dir']
        self.building_ID = self.ml_inputs['building']
        self.flight_ID = self.ml_inputs['flight']
        
        if not os.path.exists(self.output_dir):
            raise Exception('Invalid output directory')
        if not os.path.exists(self.input_dir):
            raise Exception('Invalid Input directory')
        if len(self.building_ID)==0 or len(self.flight_ID)==0: 
            raise Exception('building/flight ID not specified')
            
        self.facade_input_dirs = sorted([x[0] for x in os.walk(self.input_dir)][1:])
        self.facade_no = len(self.facade_input_dirs)

            
    def semantic_seg(self, input_dir, output_dir):
        #create a folder named 'semantic' in the output directory to store results

        ss_out_dir = output_dir + '/semantic/'
        if not os.path.exists(ss_out_dir):
            os.mkdir(ss_out_dir)
        
        ss_txt = create_image_list(input_dir, 'ss')
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

        return ss_out_dir+'MASKED'

        #out, err = process.communicate()
    
    def classification(self, input_dir, output_dir, facadeID):
        '''
        Run inference on defect classification model. 
        - purpose: identify crack, spalling (Delamination)
        -----------
        Output:
            -folder named by IDs, contains crack, spalling images and folders with defect patches    
        '''
        
        dc_out_dir = output_dir+'/classification/'
        if not os.path.exists(dc_out_dir):
            os.mkdir(dc_out_dir)

        dc_txt = create_folder_list([input_dir], 'dc')

        os.chdir('/home/paul/Workspaces/python/defect_classification/combine_process/')
        process = Popen(["/home/paul/Workspaces/python/defect_classification/combine_process/run_check_defects.sh %s %s %s %s %s" 
                         %(dc_txt,self.building_ID,facadeID,self.flight_ID,dc_out_dir)],
                        stdout=PIPE, shell=True, universal_newlines=True)
            
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                print('Defect classification inference process is completed')
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        #process.communicate()
        return dc_out_dir
    
    def defect_seg(self, input_dir, output_dir):
        
        ds_txt = create_image_list(input_dir, 'ds')
        ds_out_dir = output_dir+'/defect_seg/'
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

        return ds_out_dir

    def severity(self, input_dir, crack=False, pixel_mm=None, critical_area=None):
        output = severity_process(input_dir, crack, pixel_mm=(0.46, 0.47), critical_area=17671)
        print(output)
        
    def update_csv(self, defect_output, output_dir):
        '''
        update the defect segmentation results in csv;
        move the csv to parent directory
        '''
        #read the previous csv file into a list of dicts
        
        dc_dir = os.path.join(output_dir,'classification')
        csv_path = [os.path.join(dc_dir,f) for f in os.listdir(dc_dir) if
                    f.endswith('.csv')][0]

        csv_data = list(csv.DictReader(open(csv_path)))

        
        img_list = defect_output.keys()

        update_list = [(os.path.split(img)[-1][:8],os.path.split(img)[-1][9:],
                        defect_output[img]) for img in img_list]
               
        for name, defect,severity in update_list:
            spalling = discoloration = rust = no_defect = False
            if 'E' in defect:
                discoloration = no_defect = True
            if 'S' in defect:
                spalling = no_defect = True
            if 'M' in defect:
                rust = no_defect = True
            if no_defect is True:
                update_item = next(item for item in csv_data if item["Name"]==name)
                update_item['No Defect'] = no_defect
                update_item['Spalling'] = spalling
                update_item['Discoloration'] = discoloration
                update_item['Metal Corrosion'] = rust
                for s in severity:
                    if s[2] is True:
                        update_item['Severity'] = 'severe'
        
        header = ["Name", "Blistering", "Blistering Confidence Level", "Biological",
                  "Biological Confidence Level", "Crack", "Crack Confidence Level", 
                  "Delamination", "Delam Confidence Level", "Discoloration", 
                  "Discolour Confidence Level", "Peeling", "Peeling Confidence Level",
                  "Spalling", "Spalling Confidence Level", "Metal Corrosion",
                  "Metal Confidence Level", "No Defect", 'Severity']
        
        with open(csv_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, header)
            dict_writer.writeheader()
            dict_writer.writerows(csv_data)
            
        #move csv to parent directory
        dst = os.path.join(output_dir, os.path.split(csv_path)[-1])
        shutil.move(csv_path, dst)
            
            
    def overlay(self, mask_dir, patch_dir, defect_dir, output_dir):
        '''
        overlay the mask image and defet patch image
        '''

        mask_list = sorted([os.path.join(mask_dir, f) 
                           for f in os.listdir(mask_dir) if
                           os.path.isfile(os.path.join(mask_dir, f))])
        
        crack_list = sorted([os.path.join(patch_dir, f) 
                             for f in os.listdir(patch_dir) if
                             '_C' in f])

        defect_list = sorted([os.path.join(defect_dir, f) 
                             for f in os.listdir(defect_dir)])


        for raw_img, patch_img, defect_img in zip(mask_list, crack_list, defect_list):
            
            name1 = os.path.split(patch_img)[-1]
            name2 = os.path.split(defect_img)[-1]
            
            background = cv2.imread(raw_img)
            overlay_patch = cv2.imread(patch_img)
            overlay_defect = cv2.imread(defect_img)
            
            added_img_patch = cv2.addWeighted(background,0.9,overlay_patch,0.7,0)
            added_img_defect = cv2.addWeighted(background,0.9,overlay_defect,0.8,0)
            
            cv2.imwrite(os.path.join(output_dir, name1), added_img_patch)
            cv2.imwrite(os.path.join(output_dir, name2), added_img_defect)    
    
    
    def run(self):
        
        for i in range(self.facade_no):
            input_dir = self.facade_input_dirs[i]
            output_dir = self.facade_input_dirs[i].replace('img_m210rtkv2_x7', 'all_results')
            masked_dir = self.semantic_seg(input_dir, output_dir)
            patch_dir = self.classification(input_dir, output_dir, i+1)
            defect_dir = self.defect_seg(input_dir, output_dir)

            #severity based on area
            self.severity(defect_dir, crack=False, pixel_mm=None, critical_area=None)

            patch_name = "BuildingId_{}_FacadeId_{}_FlightId_{}".format(self.building_ID, i+1, self.flight_ID)
            patch_dir = os.path.join(patch_dir, patch_name)
            self.overlay(masked_dir, patch_dir, defect_dir, output_dir+'/overlay/')
            break
        return masked_dir, patch_dir, defect_dir

        
if __name__ == '__main__':
    ml_inputs = {}
    ml_inputs['input_dir'] = '/home/paul/Workspaces/python/Drone_io_pipeline-main/test_preprocess/102030_288G_bishanroad3/inspect1/results/img_m210rtkv2_x7/'
    ml_inputs['output_dir'] = '/home/paul/Workspaces/python/Drone_io_pipeline-main/test_preprocess/102030_288G_bishanroad3/inspect1/results/all_results/'
    ml_inputs['building'] = '288'
    ml_inputs['flight'] = '1'
    
    defect_output = {'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results/defect_seg\\DJI_1044_M.png': [(75, 95831, True)], 
     'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results/defect_seg\\DJI_1048_.png': [],
     'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results/defect_seg\\DJI_1053_E_R.png': [(38, 33318, True), (113, 16663, False)]}
    
    inference = Inference(ml_inputs)
    # inference = Inference(ml_inputs)
    # inference.severity('/home/paul/Workspaces/python/Drone_io_pipeline-main/test_preprocess/112233_288_G_bishan3/inspect1/results/all_results/facade1/defect_seg')
    #inference.run()
    inference.update_csv(defect_output, r'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results')
    