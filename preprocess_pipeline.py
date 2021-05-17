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
	
	def __init__(self,name,inspection_no,buildingID,frequency=[1,2,3],
				  handheld=True, thermal=False):
		'''
		Initiating the class by creating all the necessary folders

		Parameters
		----------
		name : building folder name
		inspection_no : str
		facade_no : int, total number of facades
		handheld : list of 2, 1st item: drone images path; 2nd item: handheld images path
		'''
		
		self.root = r'/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset'
		self.name = name
		self.inspect_no = 'inspect'+inspection_no
		self.frequency = frequency
		self.buildingID = buildingID
		self.handheld = handheld
		self.thermal = thermal
		self.input_drone = os.path.join(self.root, 'DCIM')  
		if self.handheld:
			self.input_handheld = os.path.join(self.root, 'Handheld')			
				
	def extract_timesheet(self, drone=True, timesheet=None):
		#get the facade time_in, time_out from timesheet csv
		time_data = []
		facade_list = []
		if timesheet is None:
			if drone:
				timesheet = os.path.join(self.root, 'timesheet_drone.csv')
			else:
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
		if drone:
			self.facade_list_drone = list(set(facade_list))
		else:
			self.facade_list_handheld = list(set(facade_list))
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
				
		results_sub_dirs = ['all_results', 'img_m210rtkv2_x7', 'all_results_handheld_rgb',
						  'img_handheld_rgb']
		self.result_dir = os.path.join(inspect_dir, 'results')
		create_dirs(results_sub_dirs, self.result_dir)
		
		self.facade_drone_dirs = ['facade'+str(i) for i in self.facade_list_drone]
		self.facade_dir_process = os.path.join(self.result_dir, 'img_m210rtkv2_x7')		
		self.facade_dir_raw = os.path.join(self.others_dir, 'raw')
		self.facade_result = os.path.join(self.result_dir, 'all_results')
		if self.handheld:
			self.facade_hhl_dirs = ['facade'+str(i) for i in self.facade_list_handheld]
			self.facade_dir_handheld = os.path.join(self.result_dir, 'img_handheld_rgb')
			self.facade_result_handheld = os.path.join(self.result_dir, 'all_results_handheld_rgb')
			for folder in [self.facade_dir_handheld, self.facade_result_handheld]:    
				create_dirs(self.facade_hhl_dirs, folder)
				
			for facade_dir in self.facade_hhl_dirs:
			#create folder to store filtered images inside each facade folder
				overlay_dir = os.path.join(self.facade_result_handheld, facade_dir, 'overlay')
				if not os.path.exists(overlay_dir):
					os.mkdir(overlay_dir)
				
		for folder in [self.facade_dir_process,self.facade_dir_raw,self.facade_result]:
			create_dirs(self.facade_drone_dirs, folder)
		
		for facade_dir in self.facade_drone_dirs:
			#create folder to store filtered images inside each facade folder
			overlay_dir = os.path.join(self.facade_result, facade_dir, 'overlay')
			if not os.path.exists(overlay_dir):
				os.mkdir(overlay_dir)
		
	def combine_dirs(self):
		'''
		combine multiple folders from SD card, rename the image files starting 
		from DJI_0001, only for drone images

		'''
		total_no = 1
		subdirs = [x[0] for x in os.walk(self.input_drone)][1:]

		for img_dir in sorted(subdirs):            

			img_list = sorted([os.path.join(img_dir,f) for f in os.listdir(img_dir)
							 if os.path.isfile(os.path.join(img_dir, f))])
			num = len(img_list)
			
			start_no = total_no
			for img in img_list:

				name = 'DJI_'+str(start_no).zfill(4)+os.path.splitext(img)[-1]				
				dest = os.path.join(self.others_dir, 'raw_SD', name)
				start_no += 1
				shutil.copy(img, dest)
				shutil.copystat(img, dest)
			total_no += num

	@staticmethod
	def extract_time(img):
		return Image.open(img).getexif()[36867]

#TODO: decide where to put the timesheet csv & input folder
	def allocate_imgs(self, time_data, facade_list, folder=None, drone=True):
		'''
		allocate images to the respective facade folder, based on timesheet
		'''
		if folder is None:
			if drone:
				folder = os.path.join(self.others_dir, 'raw_SD')
			else:
				folder = self.input_handheld
		
		#extract modified data of the images
		img_list = [os.path.join(folder,f) for f in os.listdir(folder)
					if os.path.isfile(os.path.join(folder, f))]
		
		img_list.sort()
		time_modify_list = []

		for img in img_list:
			time = Preprocess.extract_time(img)
			time_modify_list.append(time.split()[1])
		
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
			if drone:
				dest = os.path.join(self.facade_dir_raw, idx_list[i][0], name)	
				#dest = os.path.join('/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/288G_1/inspect1/img_m210rtkv2_x7_others/raw', \
				#		 idx_list[i][0], name)	
			else:
				dest = os.path.join(self.facade_dir_handheld, idx_list[i][0], name)
			shutil.copy(img_list[i], dest)
			shutil.copystat(img_list[i], dest)

			
	def rename_facade_dirs(self, drone=True):
		'''
		rename images for all the facade folders
		'''
		if drone:
			for facade in self.facade_drone_dirs:
				facade_dir = os.path.join(self.facade_dir_raw, facade)
				rename_dir(facade_dir)
		else:
			for facade in self.facade_hhl_dirs:
				facade_dir = os.path.join(self.facade_dir_handheld, facade)
				rename_dir(facade_dir, drone=False)
			
	def filter_overlap(self):
		'''
		filter out overlapped images based on the frequency defined
		Parameters
		----------
		frequency : list, optional
			DESCRIPTION. The default is 3.

		'''
		idx = 0
		if len(self.frequency)==1:
			self.frequency = self.frequency * len(self.facade_drone_dirs)
		for facade_dir in self.facade_drone_dirs:
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
							
	def process_ready(self, drone=True):
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
		ml_inputs['input_dir_drone'] = upload_inputs['raw_drone_dir'] = self.facade_dir_process
		ml_inputs['output_drone_dir'] = upload_inputs['result_drone_dir'] = os.path.join(self.result_dir,'all_results')
		upload_inputs['facade_no_drone'] = self.facade_drone_dirs
		upload_inputs['facade_no_hhl'] = self.facade_hhl_dirs

		return ml_inputs, upload_inputs

				 
	def run(self):      
		
		time_data_drone, facade_list_drone = self.extract_timesheet(True)
		if self.handheld:
			time_data_handheld, facade_list_handheld = self.extract_timesheet(False)
		self.create_standard_dirs()
		self.combine_dirs()
		self.allocate_imgs(time_data_drone, facade_list_drone)
		self.rename_facade_dirs()
		if self.handheld:
			self.allocate_imgs(time_data_handheld, facade_list_handheld, drone=False)
			self.rename_facade_dirs(False)		
		self.filter_overlap()
		#ml_inputs, upload_inputs = self.process_ready()
		#return ml_inputs, upload_inputs
				 
				
if __name__ == '__main__':
	preprocess = Preprocess('288G_1', '1', '5', [2], handheld=True)
	#timesheet = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/timesheet_handheld.csv'
	preprocess.run()
	#time_data, facade_list = preprocess.extract_timesheet(True)
	#print(time_data)
	#preprocess.allocate_imgs(time_data, facade_list, folder='/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/handheld/inspect1/img_m210rtkv2_x7_others/raw_SD')
	#preprocess.rename_facade_dirs()

	#folder = '/home/paul/Workspaces/python/Drone_io_pipeline-main/real_dataset/handheld/inspect1/img_m210rtkv2_x7_others/janine/facade'
	#for i in [1, 3,4,8,9,10,11,13,14]:
#		rename_dir(folder+str(i))

	#print(ml_inputs, upload_inputs)
	

	

