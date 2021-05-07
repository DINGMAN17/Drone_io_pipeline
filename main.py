# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 15:39:46 2021

@author: cryst
"""


from preprocess_pipeline import Preprocess
from ML_pipeline import Inference
from postprocess_pipeline import UploadProcess
import threading
#TODO: parallel execution, upload & ML models

def main(inputs):
   preprocess = Preprocess(inputs['building_name'], inputs['inspection_no'], 
                           inputs['buildingID'], inputs['frequency'])
   ml_inputs, upload_inputs = preprocess.run()
   print('ml_inputs: ', ml_inputs)
   print('---------------------------')
   print('upload_inputs: ', upload_inputs)
   inference = Inference(ml_inputs)
   csv_data = inference.run()
   upload = UploadProcess(upload_inputs)
   upload.run_post_raw(True)
   upload.run_patch(csv_data, True)
   upload.run_post_overlay(True)
    
    
if __name__ == '__main__':
    inputs = {}
    inputs['building_name'] = input('Building name: ')
    inputs['buildingID'] = input('building ID(database): ')
    inputs['inspection_no'] = input('Inspection number: ')
    inputs['frequency'] =list((input('Filtering frquency: ')))
    
    main(inputs)