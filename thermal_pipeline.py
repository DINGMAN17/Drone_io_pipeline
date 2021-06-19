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
import tqdm
import flirimageextractor
import metpy.calc as mpcalc
from distortion_correction import correct_distortion
from get_transformation_matrix import apply_trans_matrix

class Thermal_pipeline():

    def __init__(self, input_dir, distance, output_dir, facade_list=None):
        self.input_dir = input_dir
        self.distance = distance
        self.output_dir = output_dir
        self.facade_list = facade_list

    def dir_create(self, path):

        if (os.path.exists(path)) and (os.listdir(path) != []):
            shutil.rmtree(path)
            os.makedirs(path)
        if not os.path.exists(path):
            os.makedirs(path)

    def un_distort(self, input_dir=None, output_dir=None):
        if input_dir is None:
            input_dir = self.input_dir
        output_dir = correct_distortion(input_dir, True, output_dir)
        return output_dir
       
    def transform(self,input_dir=None, output_dir=None):

        if input_dir is None:
            input_dir = os.path.join(self.output_dir, 'undistorted')
        
        rgb_list = [fname for fname in os.listdir(input_dir)
                    if re.match(r'DJI_[0-9]+.jpg', fname)]
        
        for rgb_file in rgb_list:
            rgb_file = os.path.join(input_dir, rgb_file)
            apply_trans_matrix(self.distance, rgb_file, output_dir)

    def extract_temperature_ir(self, min_temp=25, max_temp=35, input_dir=None, output_dir=None):
        #get temperature plot from IR images
        if input_dir is None:
            input_dir = self.input_dir

        flir = flirimageextractor.FlirImageExtractor(palettes=[cm.hot])
        ir_list = [fname for fname in os.listdir(input_dir)
                   if re.match(r'DJI_[0-9]+_R.JPG', fname)]
        
        for ir_file in ir_list:
            img_path = os.path.join(input_dir, ir_file)
            flir.process_image(img_path)
            thermal_arr = flir.get_thermal_np()
            result = flir.save_images(min_temp, max_temp)

            #save the results
            arr_filename = os.path.splitext(ir_file)[0] + '_temp.npy'
            np.save(os.path.join(output_dir, arr_filename), thermal_arr)              
            
    #TODO: add threshold to temperature array? use normalized array?
    def rgb_ir_fusion(self, overlay=True, input_ir=None, input_rgb=None, output_dir=None):
        
        if input_rgb is None:
            input_rgb = os.path.join(self.output_dir, 'mapped')
        rgb_list = glob.glob(os.path.join(input_rgb, '*mapped.jpg'))
        rgb_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
                        for x in re.findall(r'[^0-9]|[0-9]+', var)])

        #TODO: get the prefix of IR image
        #temp_arr_list = glob.glob(os.path.join(self.output_dir, 'array_data', '*_temp.npy'))
        #temp_arr_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
        #                    for x in re.findall(r'[^0-9]|[0-9]+', var)])

        if input_ir is None:
            input_ir = self.input_dir
        ir_list = glob.glob(os.path.join(input_ir, '*hot.JPG'))
        ir_list.sort(key=lambda var:[int(x) if x.isdigit() else x 
                        for x in re.findall(r'[^0-9]|[0-9]+', var)])
        #output_dir = os.path.join(self.output_dir, 'array_data')
        
        #print(rgb_list, ir_list, temp_arr_list)
        #for rgb_img, ir_img, temp_file in zip(rgb_list, ir_list, temp_arr_list):
        for rgb_img, ir_img in zip(rgb_list, ir_list):
            rgb_arr = cv2.imread(rgb_img)
            #save rgbt data
            #temp_arr = np.load(temp_file, allow_pickle=True)
            #temp_arr = np.expand_dims(temp_arr, 2)
            #rgbt_arr = np.concatenate((rgb_arr, temp_arr), 2)
            #save the results
            #arr_dir = os.path.splitext(temp_file)[0][:-2] + '_rgbt.npy'
            #np.save(os.path.join(output_dir, arr_dir), rgbt_arr) 
            if overlay:
                ir_arr = cv2.imread(ir_img)
                fusion_image = cv2.addWeighted(rgb_arr, 0.4, ir_arr, 0.6, 0)
                img_filename = os.path.split(rgb_img)[-1].replace('mapped', 'merge')
                cv2.imwrite(os.path.join(output_dir, img_filename), fusion_image)

    def thermal_gradient(self, temp_arr_file):
        #read temperature array data
        temp_arr = np.load(temp_arr_file, allow_pickle=True)
        #get the thermal graident, grad: 2D array
        x_delta = 1
        y_delta = 1    
        grad = mpcalc.gradient(temp_arr, deltas=(y_delta, x_delta))
        #plot the gradient 
        fig, ax = plt.subplots()
        im2 = ax.imshow(np.array(grad[0]), cmap='RdGy', vmin=-0.5, vmax=0.5)
        im1 = ax.imshow(np.array(grad[1]), cmap='RdGy', interpolation='nearest', 
                         alpha=.4, vmin=-0.5, vmax=0.5)
        #save the plot
        fig.colorbar(im1)
        fname = os.path.split(temp_arr_file)[1].replace('npy', 'png')
        fig.savefig(fname)
        if os.path.exists(fname):
            print(os.path.abspath(fname))
        else:
            print("file not found")
        plt.close("all")

    def run(self):        
        #create folders
        self.dir_create(self.output_dir)
        undistort_dir = os.path.join(self.output_dir, 'undistorted')
        self.dir_create(undistort_dir)
        mapped_dir = os.path.join(self.output_dir, 'mapped')
        array_dir = os.path.join(self.output_dir, 'array_data')
        overlay_dir = os.path.join(self.output_dir, 'overlay_IR')
        for folder in [mapped_dir, array_dir, overlay_dir]:
            self.dir_create(folder)

        self.un_distort(output_dir=undistort_dir)
        self.transform(output_dir=mapped_dir)
        self.extract_temperature_ir(output_dir=array_dir)
        self.rgb_ir_fusion(output_dir=overlay_dir)

    def run_preprocess(self):
        #take inputs from the preprocess pipeline
        for facade_no in tqdm.tqdm(facade_list):

            input_rgb = os.path.join(self.input_dir, 'img_drone_rgb', facade_no)
            input_ir = os.path.join(self.input_dir, 'img_drone_ir', facade_no)
            mapped_dir = os.path.join(self.output_dir, facade_no, 'mapped')
            array_dir = os.path.join(self.output_dir, facade_no, 'array_data')
            overlay_dir = os.path.join(self.output_dir, facade_no, 'overlay_IR')
            for folder in [mapped_dir, array_dir, overlay_dir]:
                self.dir_create(folder)

            self.transform(input_dir=input_rgb, output_dir=mapped_dir)
            self.extract_temperature_ir(input_dir=input_ir, output_dir=array_dir)
            self.rgb_ir_fusion(input_ir=input_ir, input_rgb=mapped_dir, output_dir=overlay_dir)
            
      
if __name__ == '__main__':
    #input_dir = '/home/paul/Workspaces/python/Drone_io_pipeline-main/test_thermal_pipeline/'
    #input_dir = '/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal_defects'
    #output_dir = '/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal_defects_results'
    thermal_inputs = {'input_dir': '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/test_thermal_preprocess/bishan/inspect1/results',
      'output_dir': '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/test_thermal_preprocess/bishan/inspect1/results/all_results_drone_ir', 
      'facade_no': ['facade5', 'facade4', 'facade2', 'facade3', 'facade6']}
    distance = '6m'
    input_dir = thermal_inputs['input_dir']
    output_dir = thermal_inputs['output_dir']
    facade_list = thermal_inputs['facade_no']
    thermal = Thermal_pipeline(input_dir, distance, output_dir, facade_list)

    thermal.run_preprocess()