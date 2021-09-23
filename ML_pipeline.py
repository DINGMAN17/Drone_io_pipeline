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
import numpy as np
from tqdm import tqdm
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
        self.get_parameters()
            
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
        self.facade_list = self.ml_inputs['facade_list']
        
        if not os.path.exists(self.output_dir):
            raise Exception('Invalid output directory')
        if not os.path.exists(self.input_dir):
            raise Exception('Invalid Input directory')
        if len(self.building_ID)==0 or len(self.flight_ID)==0: 
            raise Exception('building/flight ID not specified')
            
        self.facade_input_dirs = sorted([x[0] for x in os.walk(self.input_dir)][1:])
        #print(len(self.facade_input_dirs))

            
    def semantic_seg(self, input_dir, output_dir):
        #create a folder named 'semantic' in the output directory to store results
        print(output_dir)
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
    
    def classification(self, input_dir, output_dir, facadeID=1):
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
        return output
        
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

        update_defect_list = [(os.path.split(img)[-1][:8],os.path.split(img)[-1][9:],
                        defect_output[img]) for img in img_list]
               
        for name, defect,severity in update_defect_list:
#TODO: if defect, change no_defect to False
            spalling = discoloration = rust = 'False'
            no_defect = 'True'
            if 'E' in defect:
                discoloration = 'True'
                no_defect = 'False'
            if 'S' in defect:
                spalling = 'True'
                no_defect = 'False'
            else:
                spalling = 'False'

            if 'M' in defect:
                rust = 'True'
                no_defect = 'False'
                
            if no_defect == 'False':
                update_item = next(item for item in csv_data if item["name"]==name)
                update_item['nonDefect'] = no_defect
                update_item['spalling'] = spalling
                update_item['discolouration'] = discoloration
                update_item['metalCorrosion'] = rust
        #as long as crack is detected, it's marked as require repair
        #because all the cracks that can be detected are > 0.3mm (critical)
                if update_item['crack'].lower() == 'true':
                    #print('crack true')
                    update_item['crackSeverity'] = 'Require Repair'
                for s in severity:
                    if s[0] == 38:
                        if s[2] is True:
                            update_item['efflorescenceSeverity'] = 'Require Repair'
                        else:
                            update_item['efflorescenceSeverity'] = 'Safe'
                    elif s[0] == 75:
                        if s[2] is True:
                            update_item['rustSeverity'] = 'Require Repair'
                        else:
                            update_item['rustSeverity'] = 'Safe'
                    elif s[0] == 113:
                        if s[2] is True:
                            update_item['spallingSeverity'] = 'Require Repair'
                        else:
                            update_item['spallingSeverity'] = 'Safe'

        csv_data_dict = [dict(item) for item in csv_data]
        
        header = ["name", "blistering", "blisteringLevel", "biological",
                  "biologicalLevel", "crack", "crackLevel", "delamination", 
                  "delamLevel", "discolouration", "efflorescenceLevel", "peeling", 
                  "peelingLevel", "spalling", "spallingLevel","metalCorrosion",
                  "rustLevel", "nonDefect", 'crackSeverity', 'efflorescenceSeverity',
                  'spallingSeverity', 'rustSeverity']

        with open(csv_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, header)
            dict_writer.writeheader()
            dict_writer.writerows(csv_data)
            
        #move csv to parent directory
        dst = os.path.join(output_dir, os.path.split(csv_path)[-1])
        shutil.move(csv_path, dst)

        return csv_data_dict
            
#TODO: reduce overlay file size!!            
    def overlay(self, mask_dir, patch_dir, defect_dir, output_dir, merge=False):
        '''
        overlay the mask image and defet patch image
        '''
        
        crack_list = sorted([os.path.join(patch_dir, f) 
                             for f in os.listdir(patch_dir) if
                             '_C' in f])

        defect_list = sorted([os.path.join(defect_dir, f) 
                             for f in os.listdir(defect_dir)])

        if merge:
            mask_list = sorted([os.path.join(mask_dir, f) 
                           for f in os.listdir(mask_dir) if
                           os.path.isfile(os.path.join(mask_dir, f))])

            for raw_img, patch_img, defect_img in tqdm(zip(mask_list, crack_list, defect_list), total=len(mask_list)):
                
                name1 = os.path.split(patch_img)[-1].replace('png', 'JPG')
                name2 = os.path.split(defect_img)[-1].replace('png', 'JPG')
                #print(name1, name2)
                
                background = cv2.imread(raw_img)
                overlay_patch = cv2.imread(patch_img)
                overlay_defect = cv2.imread(defect_img)
                
                if np.count_nonzero(overlay_patch) != 0:
                    added_img_patch = cv2.addWeighted(background,0.9,overlay_patch,0.7,0)
                    cv2.imwrite(os.path.join(output_dir, name1), added_img_patch)
                if np.count_nonzero(overlay_defect) != 0:
                    added_img_defect = cv2.addWeighted(background,0.9,overlay_defect,0.8,0)
                    cv2.imwrite(os.path.join(output_dir, name2), added_img_defect) 
        else:
            for patch_img, defect_img in zip(crack_list, defect_list):
                
                name1 = os.path.split(patch_img)[-1]
                name2 = os.path.split(defect_img)[-1]
                #print(name1, name2)
                overlay_patch = cv2.imread(patch_img)
                overlay_defect = cv2.imread(defect_img)
                
                if np.count_nonzero(overlay_patch) != 0:
                    dest1 = os.path.join(output_dir, name1)
                    cv2.imwrite(dest1, overlay_patch)
                if np.count_nonzero(overlay_defect) != 0:
                    dest2 = os.path.join(output_dir, name2)
                    cv2.imwrite(dest2, overlay_defect)
                

    @staticmethod
    def get_facadeID(path):
        regex = re.compile(r'(\d+)$')
        facadeID = regex.findall(path)
        return facadeID[0]
               
    def report(self, csv_path=None):

        if csv_path is None:
            csv_path = os.path.join(self.output_dir, 'report.csv')
        csv_data_w = []
        total_raw=total_C=total_R=total_S=total_E=total_severe=0

        for facade_no in self.facade_list:

            folder = os.path.join(self.output_dir, 'facade'+facade_no)
            r_csv_path = [os.path.join(folder,f) for f in os.listdir(folder) if f.endswith('.csv')][0]
            csv_data = list(csv.DictReader(open(r_csv_path)))
            raw_imgs = len(csv_data)
            defect_imgs = []
            for defect in ['crack', 'spalling', 'discolouration', 'metalCorrosion']:
                no_imgs = len([item['name'] for item in csv_data if item[defect].lower()=='true'])
                defect_imgs.append(no_imgs)

            severe_list = [[(k,v) for k,v in item.items() if k.endswith('Severity') and item[k]=='Require Repair'] \
                            for item in csv_data]
            severe_imgs = sum(len(item)>0 for item in severe_list)

            row_data = {'facade_no': facade_no, 'raw images': raw_imgs, 'images with crack':defect_imgs[0], 'images with spalling':defect_imgs[1], 
                        'images with efflorescence':defect_imgs[2], 'images with rust':defect_imgs[3], 'images with severe defects': severe_imgs}
            
            csv_data_w.append(row_data)

            total_raw += raw_imgs
            total_C += defect_imgs[0]
            total_E += defect_imgs[1]
            total_S += defect_imgs[2]
            total_R += defect_imgs[3]     
            total_severe += severe_imgs   
            
        csv_data_w.append({'facade_no': 'Total', 'raw images': total_raw, 'images with crack':total_C, 
                        'images with spalling':total_S, 'images with efflorescence':total_E, 
                        'images with rust':total_R, 'images with severe defects': total_severe})

        header = ['facade_no', 'raw images', 'images with crack', 'images with spalling', 
                    'images with efflorescence', 'images with rust', 'images with severe defects']

        with open(csv_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, header)
            dict_writer.writeheader()
            dict_writer.writerows(csv_data_w)
    
    def run(self):

        for facade_no in self.facade_list:
            output_dir = os.path.join(self.output_dir, 'facade'+facade_no)
            input_dir = os.path.join(self.input_dir, 'facade'+facade_no)
            masked_dir = self.semantic_seg(input_dir, output_dir)
            patch_dir = self.classification(input_dir, output_dir, int(facade_no))
            defect_dir = self.defect_seg(input_dir, output_dir)

            #get defect severity
            defect_output = self.severity(defect_dir, crack=False, pixel_mm=None, critical_area=None)
            patch_name = "BuildingId_{}_FacadeId_{}_FlightId_{}".format(self.building_ID, int(facade_no), self.flight_ID)
            #overlay masked image and model outputs
            patch_dir = os.path.join(patch_dir, patch_name)
            self.overlay(masked_dir, patch_dir, defect_dir, output_dir+'/overlay/', merge=True)
            csv_data = self.update_csv(defect_output, output_dir)
        self.report()

        return csv_data

if __name__ == '__main__':
    facade_list = ["13"]
    #facade_list = [str(i) for i in range(1, 15)]
    ml_inputs = {'building': '10', 'flight': '1', 'input_dir': '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/CE5807/raw/', 
    'output_dir': "/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/CE5807/results/", 
    'facade_list':facade_list}
    inference = Inference(ml_inputs)
    inference.run()

    #mask_dir = ""
    #result_dir = "/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/demo/results/"
    #for facade_no in range(2,15):
    #    facade_dir = os.path.join(result_dir, "facade"+str(facade_no))
    #    patch_name = "BuildingId_{}_FacadeId_{}_FlightId_{}".format(10,facade_no,1)
    #    patch_dir = os.path.join(facade_dir, "classification", patch_name)
    #    defect_dir = os.path.join(facade_dir, "defect_seg")
    #    output_dir = os.path.join(facade_dir, "overlay")
    #    shutil.rmtree(output_dir)
    #    os.mkdir(output_dir)
    #    inference.overlay(mask_dir, patch_dir, defect_dir, output_dir, merge=False)

        
