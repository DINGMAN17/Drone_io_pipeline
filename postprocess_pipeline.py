# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:50:56 2021

@author: cryst
"""

import os
import re
import csv
import requests
import numpy as np
from requests import HTTPError, Timeout

class UploadProcess:
	
	def __init__(self, upload_inputs):
		self.url = "https://www.wingspect.net/api/images/"
		self._token = '4557b2472a8b6713fa831e070e7030b97ad142d9'
		self.get_parameters(upload_inputs)
		
	def get_parameters(self, inputs):
		self.buildingID = str(inputs['building'])
		self.raw_img_dir = inputs['raw_img_dir']
		self.flightID = str(inputs['flight'])
		self.result_img_dir = inputs['result_img_dir']
		self.facade_no_list = inputs['facade_no'].split(',')
		self.get_facade_dirs()

	def get_facade_dirs(self):

		if len(self.facade_no_list) == 1:
			self.facade_input_dirs = [os.path.join(self.raw_img_dir, 'facade'+str(i)) 
										for i in range(1, int(self.facade_no_list[0])+1)]
			self.facade_sub_dirs = [os.path.join(self.result_img_dir, 'facade'+str(i)) 
										for i in range(1, int(self.facade_no_list[0])+1)]
		else:			
			try:
				self.facade_input_dirs = [os.path.join(self.raw_img_dir, 'facade'+str(num)) for num in self.facade_no_list]
				self.facade_sub_dirs = [os.path.join(self.result_img_dir, 'facade'+str(num)) for num in self.facade_no_list]

			except TypeError:
				print('Please make sure facade_no is of form 1,3,4')

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
											timeout=10)
				response.raise_for_status()
				if check:
					print('Response code: {0}, image {1}'
						  .format(response.status_code, img_name))
						
			except HTTPError as err:
				print('Error: {0} while uploading image {1}'.format(err, img_name))
			except Timeout as err:
				print('Request timed out: {0} while uploading image {1}'
					  .format(err, img_name))
		
	
	def upload_patch(self, img_path_list, facadeID, csv_data=None, check=False):
		'''
		upload masked images and update the defect information in csv
		using PATCH request
		'''
		#get request to locate the info in the database
		headers = {'Authorization': 'Token ' + self._token}  
		payload_get = {}
		filepath=[]
		
		try:
			url_get = "https://www.wingspect.net/api/images/?building=" + \
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
					files = [
							  ('file', open(path,'rb'))
							]
			
					try:
						response_patch = requests.patch(url_patch, headers=headers, 
												data=payload_patch, files=files,
												timeout=2)
						#response_patch = requests.patch(url_patch, headers=headers, 
						#							data=payload_patch, timeout=2)
						response_patch.raise_for_status()
						if check:
							print('Patch Result code: {0}'.format(response_patch.status_code))
									
					except HTTPError as err:
						print('Error: {0} while updating image {1} via PATCH'
							  .format(err, filename))
					except Timeout as err:
						print('Request timed out: {0} while updating image {1} via PATCH' 
							  .format(err, filename))
	
	@staticmethod
	def read_csv(folder):

		csv_path = [os.path.join(folder,f) for f in os.listdir(folder) if f.endswith('.csv')][0]
		csv_data = list(csv.DictReader(open(csv_path)))
		return csv_data
		
	def get_payload_patch(self, csv_data, name):
		'''
		locate the corresponding item in the csv file to be uploaded to the database
		'''

		update_item = next(item for item in csv_data if item["name"]==name)
		if update_item['crack'].lower() == 'true':
			#print('crack true')
			update_item['crackSeverity'] = 'Require Repair'

		update_item['spallingLevel'] = '0.0'
		if len(update_item['spallingSeverity']) < 2: 
			update_item['spalling'] = 'False'
		if update_item['spalling'].lower()==update_item['crack'].lower() \
			==update_item['discolouration'].lower()==update_item['metalCorrosion'].lower()=='false':

			update_item['nonDefect'] = 'True'

		filter1 = {k: v for k, v in update_item.items() if len(v) != 0 
						 and v != '0'}
		filter2 = {k: (v.capitalize() if v=='FALSE' or v=='TRUE' else v) 
						 for k, v in filter1.items()}

		if 'crackLevel' in filter2.keys():
			filter2['crackLevel'] = self.float_convert(filter2['crackLevel'])

		filter2['building'] = self.buildingID
		return filter2


	@staticmethod
	def get_facadeID(path):
		regex = re.compile(r'(\d+)$')
		facadeID = regex.findall(path)
		return facadeID[0]
	
	def run_patch(self, check_status=False):
		'''
		facilitate the execution of uploading masked image and csv data
		'''
		#img_dir follows 'facade1', 'facade2'...

		for img_dir in self.facade_sub_dirs:
			facadeID = UploadProcess.get_facadeID(img_dir)
			csv_data = UploadProcess.read_csv(img_dir)
			mask_dir = os.path.join(img_dir, 'semantic', 'MASKED')
			mask_img_list = sorted([os.path.join(mask_dir,f) for f in os.listdir(mask_dir)])
			self.upload_patch(mask_img_list, facadeID, csv_data, check_status)
			
		print('Updating masked image and ML outputs completed')
		
		return csv_data

	def float_convert(self, crackLevel):
		new_crackLevel = np.float32(crackLevel)
		return new_crackLevel
	
	def run_post_raw(self, check_status=False):
		'''
		facilitate the execution of uploading raw image/overlay image
		- for raw image, the img_dir should be the parent dir containing all the 
		facade subdirs, i.e. 'results/img_m210rtkv2_x7'
		'''
		#facade_input_dirs = sorted([x[0] for x in os.walk(self.raw_img_dir)]ssss[1:])
		
		for facade_dir in self.facade_input_dirs:
			facadeID = UploadProcess.get_facadeID(facade_dir)
			print(facadeID, facade_dir)
			raw_img_list = sorted([os.path.join(facade_dir,f) for f in os.listdir(facade_dir)])
			#print(raw_img_list)
			self.upload_post(raw_img_list, facadeID)
			
		print("Uploading raw images using post request is completed!")
		
	def run_post_other(self, overlay=True, check_status=False):

		for facade_dir in self.facade_sub_dirs:
			facadeID = UploadProcess.get_facadeID(facade_dir)
			print(facadeID, facade_dir)
			if overlay:
				upload_dir = os.path.join(facade_dir, 'overlay')

			else:
				upload_dir = os.path.join(facade_dir, 'semantic')
			
			img_list = sorted([os.path.join(upload_dir,f) for f in
						os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))])
			self.upload_post(img_list, facadeID)

		if overlay:
			print("Uploading overlaid images using post request is completed!")
		else:
			print("Uploading semantic images using post request is completed!")

if __name__ == '__main__':
	inputs = {}
	inputs['building'] = 11
	inputs['flight'] = 1
	inputs['raw_img_dir'] = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/demo/raw'
	inputs['result_img_dir'] = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/demo/results'
	#inputs['facade_no'] = '2,3,4,5,6,7,8,9,10,11,12,13,14'
	inputs['facade_no'] = '1'
	upload = UploadProcess(inputs)
	#upload.run_post_raw(True)
	#upload.run_post_other(False, True)
	#upload.run_post_other(True, True)
	upload.run_patch(True)

	#for i in range(1, 15):
#		print('uploading facade'+str(i))
#		facade_dir = os.path.join(inputs['raw_img_dir'], 'facade'+str(i))
#		mask_dir = os.path.join(facade_dir, 'semantic', 'MASKED')
#		csv_data = UploadProcess.read_csv(facade_dir)

#		mask_img_list = sorted([os.path.join(mask_dir,f) for f in os.listdir(mask_dir)])
#		upload.upload_patch(mask_img_list, str(i), csv_data, True)
		
	
	
	
	

	
	