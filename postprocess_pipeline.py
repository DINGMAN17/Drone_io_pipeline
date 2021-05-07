# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:50:56 2021

@author: cryst
"""

import os
import csv
import requests
from requests import HTTPError, Timeout

class UploadProcess:
    
    def __init__(self, upload_inputs):
        self.url = "https://abc"
        self._token = 'abc'
        self.get_parameters(upload_inputs)
        
    def get_parameters(self, inputs):
        self.buildingID = str(inputs['building'])
        self.raw_img_dir = inputs['raw_img_dir']
        self.flightID = str(inputs['flight'])
        self.result_img_dir = inputs['result_img_dir']
        self.facade_no = inputs['facade_no']

    def upload_post(self, img_path_list, facadeID, check=True):
        '''
        upload raw/layer images using POST requests
        '''
        
        headers = {'Authorization': 'Token ' + self._token}

        data = {'building': self.buildingID, 'facade': facadeID,
                'flight': self.flightID}
    
        for img_path in img_path_list:
            img_name = os.path.split(img_path)[-1]

            files = [('file', open(img_path,'rb'))]
            
            try:
                response = requests.post(self.url, headers=headers, 
                                            data = data, files = files,
                                            timeout=5)
                response.raise_for_status()
                if check:
                    print('Response code: {0}, image {1}'
                          .format(response.status_code, img_name))
                        
            except HTTPError as err:
                print('Error: {0} while uploading image {1}'.format(err, img_name))
            except Timeout as err:
                print('Request timed out: {0} while uploading image {1}'
                      .format(err, img_name))
        
    
    def upload_patch(self, img_path_list, facadeID, csv_data, check=False):
        '''
        upload masked images and update the defect information in csv
        using PATCH request
        '''
        #get request to locate the info in the database
        headers = {'Authorization': 'Token ' + self._token}  
        payload_get = {}
        filepath=[]
        
        try:
            url_get = "https://abc=" + \
                self.buildingID  + "&facade=" + str(facadeID) + '&original=true'
            
            response_get = requests.get(url_get, headers=headers,
                                        data=payload_get, timeout=2)
            data_json = response_get.json()
            response_get.raise_for_status()
            if check:
                print('Matching items Result code: {0}'.format(response_get.status_code))
                        
        except HTTPError as err:
            print('Error: {0}'.format(err))
        except Timeout as err:
            print('Request timed out: {0}'.format(err))
            
        # Storing the data into an array 
        for item in data_json:
            filepath.append(item)
                
        #looping through the masked image paths
        for path in img_path_list:
            #remove 'MASK' from the image file name
            filename = os.path.split(path)[-1].rsplit('_', maxsplit=1)[0]
            
            for img in filepath:
                if (str(img['flight']) == self.flightID) and (str(img['facade']) == facadeID) \
                    and (str(img['name']) == str(filename)) \
                        and (img['original'] == True):

                    url_patch = self.url + str(img['id']) + '/'
                    
                    payload_patch = self.get_payload_patch(csv_data, filename)
                    #print(payload_patch)
                    files = [
                              ('file', open(path,'rb'))
                            ]
            
                    try:
                        response_patch = requests.patch(url_patch, headers=headers, 
                                                data=payload_patch, files=files,
                                                timeout=2)
                        response_patch.raise_for_status()
                        if check:
                            print('Patch Result code: {0}'.format(response_patch.status_code))
                                    
                    except HTTPError as err:
                        print('Error: {0} while updating image {1} via PATCH'
                              .format(err, filename))
                    except Timeout as err:
                        print('Request timed out: {0} while updating image {1} via PATCH' 
                              .format(err, filename))
                    
        
    def get_payload_patch(self, csv_data, name):
        '''
        locate the corresponding item in the csv file to be uploaded to the database
        '''
        
        update_item = next(item for item in csv_data if item["name"]==name)
        filter1 = {k: v for k, v in update_item.items() if len(v) != 0 
                         and v != '0'}
        filter2 = {k: (v.capitalize() if v=='FALSE' or v=='TRUE' else v) 
                         for k, v in filter1.items()}

        for key in filter1.keys():
            if key in ["crackLevel", "spallingLevel"]:
                del filter2[key]

        filter2['building'] = self.buildingID
        #filter2['crackLevel'] = float(filter1['crackLevel'])
        return filter2
    
    def run_patch(self, csv_data, check_status=False):
        '''
        facilitate the execution of uploading masked image and csv data
        '''
        #img_dir follows 'facade1', 'facade2'...
        facade_sub_dirs = [os.path.join(self.result_img_dir, 'facade'+str(i)) for i in range(1, self.facade_no+1)]

        for img_dir in facade_sub_dirs:
            csv_path = [os.path.join(img_dir,f) for f in os.listdir(img_dir) if
                        f.endswith('.csv')][0]
            csv_data = list(csv.DictReader(open(csv_path)))
            facadeID = img_dir[-1]
            mask_dir = os.path.join(img_dir, 'semantic', 'MASKED')
            mask_img_list = [os.path.join(mask_dir,f) for f in os.listdir(mask_dir)]
            self.upload_patch(mask_img_list, facadeID, csv_data, check_status)
            break
        print('Updating masked image and ML outputs completed')
        
        return csv_data
    
    def run_post_raw(self, check_status=False):
        '''
        facilitate the execution of uploading raw image/overlay image
        - for raw image, the img_dir should be the parent dir containing all the 
        facade subdirs, i.e. 'results/img_m210rtkv2_x7'
        '''
        facade_input_dirs = sorted([x[0] for x in os.walk(self.raw_img_dir)][1:])
        
        for facade_dir in facade_input_dirs:
            facadeID = facade_dir[-1]
            raw_img_list = [os.path.join(facade_dir,f) for f in os.listdir(facade_dir)]
            self.upload_post(raw_img_list, facadeID)
            break
        print("Uploading raw images using post request is completed!")
        
    def run_post_overlay(self, check_status=False):

        facade_sub_dirs = [os.path.join(self.result_img_dir, 'facade'+str(i)) for i in range(1, self.facade_no+1)]

        for img_dir in facade_sub_dirs:
            overlay_dir = os.path.join(img_dir, 'overlay')
            facadeID = img_dir[-1]
            overlaid_img_list = [os.path.join(overlay_dir,f) for f in
                                 os.listdir(overlay_dir)]
            self.upload_post(overlaid_img_list, facadeID)
            break
        print("Uploading overlaid images using post request is completed!")

if __name__ == '__main__':
    inputs = {}
    inputs['building'] = 5
    inputs['flight'] = 1
    inputs['raw_img_dir'] = ''
    inputs['result_img_dir'] = ''
    upload = UploadProcess(inputs)
    #upload.run_post_raw(True)
    #upload.run_post_overlay('')
    
    upload.run_patch(True)
    
    
    

    
    
