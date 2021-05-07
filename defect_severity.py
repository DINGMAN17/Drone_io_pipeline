# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 10:25:27 2021

@author: cryst
"""

import os
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import medial_axis

def calculate_area(input_file, pixel_mm =(0.46, 0.47), critical_area=17671):
    '''
    Calculate the area of the defect based on the output of defect segmentation,
    rename the img based on defects
    '''
    img = cv2.imread(input_file,0)
    colors = np.delete(np.sort(np.unique(img)), [0])
    #rename
    defect = []
    if 38 in colors:
        defect.append('E')
    if 75 in colors:
        defect.append('M')
    if 113 in colors:
        defect.append('S')
    
    new_name = input_file.replace('SG', '_'.join(filter(None, defect)))
    os.rename(input_file, new_name)

    #unit_area = pixel_mm[0] * pixel_mm[1]  #based on pixel/mm of XT2 at distance 8m
    unit_area = 1
    all_area = [(color,unit_area*len(np.where(img==color)[0])) for color in colors]
    #check if the defect is critical, default critical - 150mm diameter
    output = [(area[0],area[1],area[1]>critical_area) for area in all_area]
    #output: [color, area, condition]
    return output, new_name


def get_crack_width(input_file, pixel_mm=0.31, draw=False):
    
    img = cv2.imread(input_file, 0)
    img_bool = img > 0
    # Compute the medial axis (skeleton) and the distance transform    
    skel, distance = medial_axis(img_bool, return_distance=True)
    # Distance to the background for pixels of the skeleton
    dist_on_skel = distance * skel
    max_width = np.max(dist_on_skel)*pixel_mm*2
    #determine if the defect is critical
    critical = False
    if max_width >= 0.3:
        critical = True
    
    if draw:
        i,j = np.unravel_index(dist_on_skel.argmax(), dist_on_skel.shape)
        fig = plt.figure(figsize = (10, 10))
        ax  = fig.add_subplot(111)
        ax.imshow(dist_on_skel, cmap='gray')
        ax.scatter(j, i, color='red')
        ax.contour(img, [0.5], colors='w')
        img_name = os.path.split(input_file)[-1].split('.')[0]+'_draw.png'
        
        plt.savefig(img_name, bbox_inches='tight')
        plt.close(fig)

    return max_width, critical

def severity_process(input_dir, crack=False, pixel_mm=(0.46, 0.47), critical_area=17671):
    '''Run defect severity process for a folder'''
    img_list = [fname for fname in os.listdir(input_dir)]
    result = {}
    
    if crack:
        l,w = pixel_mm
        pixel_mm = (l*l+w*w)**0.5
        for img in img_list:
            img = os.path.join(input_dir,img)
            output = get_crack_width(img, pixel_mm)
            result[img] = output
    else:
        for img in img_list:
            img = os.path.join(input_dir,img)
            output, new_name = calculate_area(img, pixel_mm, critical_area)
            result[new_name] = output
    
    # file = os.path.join(input_dir, 'severity.json')
    # with open(file, 'w') as f: 
    #     json.dump(result, f)
    return result 
        

if __name__ == '__main__':
    # condition = calculate_area(r'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results/defect_seg/DSC01044_SG.png')
    # print(condition)
    #width, critical = get_crack_width(r'C:/Users/cryst/Work/Facade_inspection/pipeline_design/defect_severity/DJI_0774_1mm_dilate.png',
    #                        draw=False)
    #print(width, critical)
    result = severity_process(r'C:/Users/cryst/Work/Facade_inspection/pipeline_design/Drone_io_pipeline-main/test_severity/test_folder/Inference_results/defect_seg')
    print(result)



