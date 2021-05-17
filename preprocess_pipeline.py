# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 17:36:57 2021

@author: cryst
"""

import os
import csv
import time
import shutil
from tqdm import tqdm
from PIL import Image
from utils import create_dirs, rename_dir

#TODO: add IR & RGB folders under each facade folder

class Preprocess:
#name,inspection_no,facade_no, 
	
	def __init__(self,name,inspection_no,buildingID, frequency=[1,2,3],input_dir=None):
		'''
		Initiating the class by creating all the necessary folders

		Parameters
		----------
		name : building folder name
		inspection_no : str
		facade_no : int, total number of facades
		input_dir : str, folder containing folders from SD card
		'''
		
		self.root = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/'
		self.name = name
		self.inspect_no = 'inspect'+inspection_no
		self.frequency = frequency
		self.buildingID = buildingID
		if input_dir is not None:
			self.input_dir = input_dir
		else:
			self.input_dir = os.path.join(self.root, 'Hdb')        
		
	def extract_timesheet(self, timesheet=None):
		#get the facade time_in, time_out from timesheet csv
		time_data = []
		facade_list = []
		if timesheet is None:
			timesheet = os.path.join(self.root, 'timesheet_handheld.csv')
		with open (timesheet,'r',newline='') as f:   
			lines = csv.reader(f)
			header = next(lines)
			for row in lines: 
				facade_time = [int(t.split(':')[0])*3600+int(t.split(':')[1])*60 \
							   +int(t.split(':')[2].split()[0])
								for t in row[1:3]]
				facade_no = row[0]
				facade_list.append(facade_no)
				time_data.append(facade_time)
		f.close()
		self.facade_no = len(set(facade_list))
		#print(time_data)
		return time_data, facade_list

	def create_standard_dirs(self):
		'''
		create all the necessary folders for one inspection
		'''
		building_dir = os.path.join(self.root, self.name)
		if not os.path.exists(building_dir):
			os.mkdir(building_dir)
		
		dir_list = ['3drecon', self.inspect_no, 'misc', 'reports']
		create_dirs(dir_list, building_dir)
				
		inspect_sub_dirs = ['flightlog', 'img_handheld_ir', 'img_handheld_rgb', 
						'img_handheld_survey', 'img_m210rtkv2_x7_others', 'results']  
		inspect_dir = os.path.join(building_dir, self.inspect_no)
		create_dirs(inspect_sub_dirs, inspect_dir)
		
		self.others_dir = os.path.join(inspect_dir, 'img_m210rtkv2_x7_others')
		others_sub_dirs = ['raw', 'raw_SD'] #may add more sub folders later on
		create_dirs(others_sub_dirs, self.others_dir)
				
		results_sub_dirs = ['all_results', 'img_m210rtkv2_x7']
		self.result_dir = os.path.join(inspect_dir, 'results')
		create_dirs(results_sub_dirs, self.result_dir)
		
		self.facade_sub_dirs = ['facade'+str(i) for i in range(1, self.facade_no+1)]
		self.facade_dir_process = os.path.join(self.result_dir, 'img_m210rtkv2_x7')
		self.facade_dir_raw = os.path.join(self.others_dir, 'raw')
		self.facade_result = os.path.join(self.result_dir, 'all_results')
		create_dirs(self.facade_sub_dirs, self.facade_dir_process)
		create_dirs(self.facade_sub_dirs, self.facade_dir_raw)
		create_dirs(self.facade_sub_dirs, self.facade_result)
		for facade_dir in self.facade_sub_dirs:
			#create folder to store filtered images inside each facade folder
			overlay_dir = os.path.join(self.facade_result, facade_dir, 'overlay')
			if not os.path.exists(overlay_dir):
				os.mkdir(overlay_dir)
		
	def combine_dirs(self):
		'''
		combine multiple folders from SD card, rename the image files starting 
		from DJI_0001

		'''
		total_no = 1
		subdirs = [x[0] for x in os.walk(self.input_dir)][1:]

		for img_dir in sorted(subdirs):            

			img_list = sorted([os.path.join(img_dir,f) for f in os.listdir(img_dir)
					if os.path.isfile(os.path.join(img_dir, f))])
			num = len(img_list)
			
			start_no = total_no
			for img in img_list:

				name = 'HHL_'+str(start_no).zfill(4)+os.path.splitext(img)[-1]				
				dest = os.path.join(self.others_dir, 'raw_SD', name)
				start_no += 1
				shutil.copy(img, dest)
				shutil.copystat(img, dest)
			total_no += num

	@staticmethod
	def extract_time(img):
		return Image.open(img).getexif()[36867]

#TODO: decide where to put the timesheet csv & input folder
	def allocate_imgs(self, time_data, facade_list, folder=None):
		'''
		allocate images to the respective facade folder, based on timesheet
		'''
		if folder is None:
			folder = os.path.join(self.others_dir, 'raw_SD')
		
		#extract modified data of the images
		img_list = [os.path.join(folder,f) for f in os.listdir(folder)
					if os.path.isfile(os.path.join(folder, f))]
		
		img_list.sort()
		time_modify_list = []

		for img in img_list:
			time = Preprocess.extract_time(img)
			time_modify_list.append(time.split()[1])

		#print(time_modify_list)
		
		time_modify_list = [int(t[:2])*3600+int(t[3:5])*60+int(t[6:8])
							for t in time_modify_list]
		
		#print(time_modify_list)
		
		#determine which facade the images belong
		idx_list = []
		for i in range(1, len(time_data)+1):
			t_range = time_data[i-1]
			facade_no = facade_list[i-1]
			for j in range(len(time_modify_list)):  
				t_modify = time_modify_list[j]
				if t_modify in range(t_range[0]-1, t_range[1]+1):
					idx_list.append(('facade'+str(facade_no),j))
		
		#copy imgs to the corresponding facade no.
		
		#print(idx_list)
		
		for i in tqdm(range(len(idx_list))):
			name = os.path.split(img_list[i])[-1]
			#dest = os.path.join(self.facade_dir_raw, idx_list[i][0], name)
			dest = os.path.join('/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/handheld/inspect1/img_m210rtkv2_x7_others/raw', idx_list[i][0], name)
			
			shutil.copy(img_list[i], dest)
			shutil.copystat(img_list[i], dest)

			
	def rename_facade_dirs(self):
		'''
		rename images for all the facade folders
		'''
		for facade in self.facade_sub_dirs:
			facade_dir = os.path.join(self.facade_dir_raw, facade)
			rename_dir(facade_dir)
			
	def filter_overlap(self):
#TODO: set the frequency based on images/minute,
		'''
		filter out overlapped images based on the frequency defined
		Parameters
		----------
		frequency : list, optional
			DESCRIPTION. The default is 3.

		'''
		idx = 0
		if len(self.frequency)==1:
			self.frequency = self.frequency * self.facade_no
		for facade_dir in self.facade_sub_dirs:
			#create folder to store filtered images inside each facade folder
			facade_dir = os.path.join(self.facade_dir_raw, facade_dir)
			filtered_dir = os.path.join(self.facade_dir_raw, facade_dir, 'filtered')
			if not os.path.exists(filtered_dir):
				os.mkdir(filtered_dir)
			
			if int(self.frequency[idx]) > 1:
				img_list = sorted([os.path.join(facade_dir, f) 
								   for f in os.listdir(facade_dir) if
								   os.path.isfile(os.path.join(facade_dir, f))])
				#start filtering
				counter = 0
				for img in img_list:
					img_name = os.path.splitext(img)
					#print(img_name)
					if img_name[-1].lower() in ['.png', '.jpg', '.jpeg']:
						counter += 1
						if counter % int(self.frequency[idx]) == 0:
							dest = os.path.join(filtered_dir, os.path.split(img)[-1])
							#print(dest)
							shutil.move(img, dest)
			idx += 1

	
			
	def extract_distance(self):
		pass
							
	def process_ready(self):
		'''
		get ready to feed images to inference pipeline
		- copy image to the folder that is ready for processing
		- prepare inputs for ML models
		'''
		#copy image to the folder
		for facade_dir in self.facade_sub_dirs:
			  facade_raw_dir = os.path.join(self.facade_dir_raw, facade_dir)
			  facade_new_dir = os.path.join(self.facade_dir_process, facade_dir)
			 
			  img_list = [os.path.join(facade_raw_dir, f) for f in os.listdir(facade_raw_dir) 
						  if os.path.isfile(os.path.join(facade_raw_dir, f))]
			  for img in img_list:
				  dest = os.path.join(facade_new_dir, os.path.split(img)[-1])
				  shutil.copy(img, dest)
				  shutil.copystat(img, dest)
		#get inputs for ML models
		ml_inputs = {}
		upload_inputs = {}
		
		ml_inputs['building'] = upload_inputs['building'] = self.buildingID
		ml_inputs['flight'] = upload_inputs['flight'] = self.inspect_no[7:]
		ml_inputs['input_dir'] = upload_inputs['raw_img_dir'] = self.facade_dir_process
		ml_inputs['output_dir'] = upload_inputs['result_img_dir'] = os.path.join(self.result_dir,'all_results')
		upload_inputs['facade_no'] = self.facade_no

		return ml_inputs, upload_inputs

				 
	def run(self):        
		time_data, facade_list = self.extract_timesheet()
		self.create_standard_dirs()
		#self.combine_dirs()
		#self.allocate_imgs(time_data, facade_list)
		#self.rename_facade_dirs()
		#self.filter_overlap()
		#ml_inputs, upload_inputs = self.process_ready()
		#return ml_inputs, upload_inputs
				 
				
if __name__ == '__main__':
	#preprocess = Preprocess('handheld', '1', '5', [1])
	#timesheet = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/timesheet_handheld.csv'
	#preprocess.run()
	#time_data, facade_list = preprocess.extract_timesheet(timesheet)
	#print(preprocess.facade_no)
	#print(time_data)
	#preprocess.allocate_imgs(time_data, facade_list, folder='/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/handheld/inspect1/img_m210rtkv2_x7_others/raw_SD')
	#preprocess.rename_facade_dirs()

	folder = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/handheld/inspect1/img_m210rtkv2_x7_others/janine/facade'
	for i in [1, 3,4,8,9,10,11,13,14]:
		rename_dir(folder+str(i))

	#print(ml_inputs, upload_inputs)
	

	

