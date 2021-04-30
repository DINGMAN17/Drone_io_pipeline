# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 15:39:46 2021

@author: cryst
"""


from preprocess_pipeline import Preprocess
from ML_pipeline import Inference
#from upload import Upload_database


def main(inputs):
   preprocess = Preprocess(inputs['building_name'], inputs['inspection_no'], inputs['frequency'])
   ml_inputs = preprocess.run()
   inference = Inference(ml_inputs)
   inference.run()
   
    
    
if __name__ == '__main__':
    inputs = {}
    inputs['building_name'] = input('Building name: ')
    inputs['inspection_no'] = input('Inspection number: ')
    inputs['frequency'] =list((input('Filtering frquency: ')))
    
    main(inputs)