# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 11:42:44 2021

@author: cryst
"""

import os
import re
import cv2
import glob
import shutil
import numpy as np
from matplotlib import pyplot as plt, cm
import flirimageextractor
from distortion_correction import correct_distortion
from get_transformation_matrix import apply_trans_matrix

class Thermal_pipeline():

    def __init__(self, input_dir, distance):
        self.input_dir = input_dir
        self.distance = distance

    def dir_create(self, path):

        if (os.path.exists(path)) and (os.listdir(path) != []):
            shutil.rmtree(path)
            os.makedirs(path)
        if not os.path.exists(path):
            os.makedirs(path)

    def un_distort(self):

        output_dir = correct_distortion(self.input_dir, True, None)
        return output_dir
       
    def transform(self,output_dir=None):
        
        rgb_list = [fname for fname in os.listdir(os.path.join(self.input_dir, 'undistorted'))
                    if re.match(r'DJI_[0-9]+.jpg', fname)]
        
        if output_dir is None:
            output_dir = os.path.join(self.input_dir, 'transform')

        self.dir_create(output_dir)
        
        for rgb_file in rgb_list:
            rgb_file = os.path.join(self.input_dir, 'undistorted',rgb_file)
            apply_trans_matrix(self.distance, rgb_file, output_dir)

    #TODO: finish extract_temperature_ir function (get the right temperature range)
    def extract_temperature_ir(self, min_temp=25, max_temp=32):

        flir = flirimageextractor.FlirImageExtractor(palettes=[cm.hot])
        ir_list = [fname for fname in os.listdir(self.input_dir)
                   if re.match(r'DJI_[0-9]+_R.JPG', fname)]

        output_dir = os.path.join(self.input_dir, 'array_data')
        self.dir_create(output_dir)
        
        for ir_file in ir_list:
            img_path = os.path.join(self.input_dir, ir_file)
            flir.process_image(img_path)
            thermal_arr = flir.get_thermal_np()
            result, normalized_array = flir.save_images(min_temp, max_temp)

            #save the results
            arr_filename = os.path.splitext(ir_file)[0] + '_temp.npy'
            np.save(os.path.join(output_dir, arr_filename), thermal_arr)              
            

    #TODO: add threshold to temperature array? use normalized array?
    def rgb_ir_fusion(self, overlay=True):

        rgb_list = glob.glob(os.path.join(self.input_dir, 'transform', '*mapped.jpg'))
        rgb_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
                        for x in re.findall(r'[^0-9]|[0-9]+', var)])
        
        #TODO: get the prefix of IR image
        temp_arr_list = glob.glob(os.path.join(self.input_dir, 'array_data', '*_temp.npy'))
        temp_arr_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
                            for x in re.findall(r'[^0-9]|[0-9]+', var)])

        ir_list = glob.glob(os.path.join(self.input_dir, '*hot.JPG'))
        ir_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
                        for x in re.findall(r'[^0-9]|[0-9]+', var)])

        output_dir = os.path.join(self.input_dir, 'array_data')
        
        #print(rgb_list, ir_list, temp_arr_list)
        for rgb_img, ir_img, temp_file in zip(rgb_list, ir_list, temp_arr_list):
            rgb_arr = cv2.imread(rgb_img)

            temp_arr = np.load(temp_file, allow_pickle=True)
            temp_arr = np.expand_dims(temp_arr, 2)
            rgbt_arr = np.concatenate((rgb_arr, temp_arr), 2)
            #save the results
            arr_dir = os.path.splitext(temp_file)[0][:-2] + '_rgbt.npy'
            np.save(os.path.join(output_dir, arr_dir), rgbt_arr) 

            if overlay:
                ir_arr = cv2.imread(ir_img)
                fusion_image = cv2.addWeighted(rgb_arr, 0.5, ir_arr, 0.5, 0)
                img_filename = os.path.split(rgb_img)[-1].replace('mapped', 'merge')
                cv2.imwrite(os.path.join(self.input_dir, img_filename), fusion_image)

    def run(self):
        self.un_distort()
        self.transform()
        self.extract_temperature_ir()
        self.rgb_ir_fusion()

      
if __name__ == '__main__':
    input_dir = '/home/paul/Workspaces/python/Drone_io_pipeline-main/test_thermal_pipeline/'
    distance = '6m'
    pipeline = Thermal_pipeline(input_dir, distance)
    pipeline.run()