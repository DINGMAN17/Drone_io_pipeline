# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 17:36:57 2021

@author: cryst
"""

import os
import csv
import shutil
from tqdm import tqdm
from PIL import Image
from utils import create_dirs, rename_dir
from thermal_pipeline import Thermal_pipeline

#TODO: check and add handheld thermal images
class Preprocess:
#name,inspection_no,facade_no, 
	
	def __init__(self,name,inspection_no,buildingID,root=None, frequency=[3],
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
		self.root = root
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
				
		results_sub_dirs = ['all_results_drone_rgb', 'img_drone_rgb', 'all_results_handheld_rgb',
						  'img_handheld_rgb']
		self.result_dir = os.path.join(inspect_dir, 'results')
		create_dirs(results_sub_dirs, self.result_dir)
		
		self.facade_drone_dirs = ['facade'+str(i) for i in self.facade_list_drone]
		self.facade_dir_process = os.path.join(self.result_dir, 'img_drone_rgb')		
		self.facade_dir_raw = os.path.join(self.others_dir, 'raw')
		self.facade_result = os.path.join(self.result_dir, 'all_results_drone_rgb')
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

		if not self.thermal:
			thermal_dirs = ['rgb']
		else:
			thermal_dirs = ['ir', 'rgb']

		for facade_dir in self.facade_drone_dirs:
			parent_dir = os.path.join(self.facade_dir_raw, facade_dir)
			raw_dir = os.path.join(self.others_dir, 'raw_SD')
			create_dirs(thermal_dirs, parent_dir)
			create_dirs(thermal_dirs, raw_dir)
	
		if self.thermal:
			result_dirs = ['all_results_handheld_ir', 'all_results_drone_ir', 
						  'img_drone_ir', 'img_handheld_ir']
			create_dirs(result_dirs, self.result_dir)
			for name in ['all_results_drone_ir', 'img_drone_ir']:
				folder = os.path.join(self.result_dir, name)
				create_dirs(self.facade_drone_dirs, folder)
			
		
	def combine_dirs(self, thermal=False):
		'''
		combine multiple folders from SD card, rename the image files starting 
		from DJI_0001, only for drone images

		'''
		total_no = 1
		subdirs = [x[0] for x in os.walk(self.input_drone)][1:]

		for img_dir in sorted(subdirs):            
			if not thermal:
				img_list = sorted([os.path.join(img_dir,f) for f in os.listdir(img_dir)
							 if 'R' not in f])
			else:
				img_list = sorted([os.path.join(img_dir,f) for f in os.listdir(img_dir)
							 if 'R' in f])
			num = len(img_list)
			
			start_no = total_no
			for img in img_list:
				if not thermal:
					name = 'DJI_'+str(start_no).zfill(4)+os.path.splitext(img)[-1]				
					dest = os.path.join(self.others_dir, 'raw_SD', 'rgb', name)
				else:
					name = 'DJI_'+str(start_no).zfill(4)+'_R'+os.path.splitext(img)[-1]
					dest = os.path.join(self.others_dir, 'raw_SD', 'ir', name)
				start_no += 1
				shutil.copy(img, dest)
				shutil.copystat(img, dest)
			total_no += num

	@staticmethod
	def extract_time(img):
		return Image.open(img).getexif()[36867]

#TODO: decide where to put the timesheet csv & input folder
	def allocate_imgs(self, time_data, facade_list, folder=None, drone=True,
				   thermal=False):
		'''
		allocate images to the respective facade folder, based on timesheet
		'''

		if folder is None:
			if drone:
				if not thermal:
					folder = os.path.join(self.others_dir, 'raw_SD', 'rgb')
				else:
					folder = os.path.join(self.others_dir, 'raw_SD', 'ir')
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
				if not thermal:
					dest = os.path.join(self.facade_dir_raw,idx_list[i][0],'rgb',name)	
				else:
					dest = os.path.join(self.facade_dir_raw,idx_list[i][0],'ir',name)	
				
			else:
				dest = os.path.join(self.facade_dir_handheld, idx_list[i][0], name)
			
			shutil.copy(img_list[i], dest)
			shutil.copystat(img_list[i], dest)
		
	def rename_facade_dirs(self, drone=True, thermal=False):
		'''
		rename images for all the facade folders
		'''
		if drone:
			for facade in self.facade_drone_dirs:
				if not thermal:
					facade_dir = os.path.join(self.facade_dir_raw, facade, 'rgb')
					rename_dir(facade_dir)
				else:
					facade_dir = os.path.join(self.facade_dir_raw, facade, 'ir')
					rename_dir(facade_dir, thermal=True)
		else:
			for facade in self.facade_hhl_dirs:
				facade_dir = os.path.join(self.facade_dir_handheld, facade)
				rename_dir(facade_dir, drone=False)
			
	def filter_overlap(self, thermal=False):
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
			if not thermal:
				facade_dir = os.path.join(self.facade_dir_raw, facade_dir, 'rgb')
			else:
				facade_dir = os.path.join(self.facade_dir_raw, facade_dir, 'ir')
			
			filtered_dir = os.path.join(facade_dir, 'filtered')
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
	
#TODO: Add Jiamin's code 			
	def extract_distance(self):
		pass

#TODO: decide output for ML pipeline (considering thermal images)	
	def process_ready(self, drone=True, thermal=False):
		'''
		get ready to feed images to inference pipeline
		- copy image to the folder that is ready for processing
		- prepare inputs for ML models
		'''
		#copy image to the folder
		if drone:
			if thermal:
				thermal_pipeline = Thermal_pipeline(None, None, None)

			for facade_dir in tqdm(self.facade_drone_dirs):
				if not thermal:
					facade_raw_dir = os.path.join(self.facade_dir_raw, facade_dir, 'rgb')
					facade_new_dir = os.path.join(self.facade_dir_process, facade_dir)
					img_list = [os.path.join(facade_raw_dir, f) for f in os.listdir(facade_raw_dir) 
							  if os.path.isfile(os.path.join(facade_raw_dir, f))]
					for img in img_list:
						dest = os.path.join(facade_new_dir, os.path.split(img)[-1])
						shutil.copy(img, dest)
						shutil.copystat(img, dest)
				else:
					#un-distort the rgb image first
					input_folder = os.path.join(self.facade_dir_raw, facade_dir, 'rgb')					
					output_folder = os.path.join(self.result_dir, 'img_drone_rgb', facade_dir)
					thermal_pipeline.un_distort(input_folder, output_folder)
					ir_folder = os.path.join(self.facade_dir_raw, facade_dir, 'ir')
					img_list = [os.path.join(ir_folder, f) for f in os.listdir(ir_folder) 
							  if os.path.isfile(os.path.join(ir_folder, f))]
					ir_dest_dir = os.path.join(self.result_dir, 'img_drone_ir', facade_dir)
					for img in img_list:
						dest = os.path.join(ir_dest_dir, os.path.split(img)[-1])
						shutil.copy(img, dest)
						shutil.copystat(img, dest)

		#get inputs for ML models
		ml_inputs = {}
		upload_inputs = {}
		thermal_inputs = {}
		
		ml_inputs['building'] = upload_inputs['building'] = self.buildingID
		ml_inputs['flight'] = upload_inputs['flight'] = self.inspect_no[7:]
		if drone:
			ml_inputs['input_dir'] = upload_inputs['raw_dir'] = self.facade_dir_process
			ml_inputs['output_dir'] = upload_inputs['result_dir'] = os.path.join(self.result_dir,'all_results_drone_rgb')
			upload_inputs['facade_no'] = self.facade_drone_dirs
			if thermal:
				thermal_inputs['input'] = self.result_dir
				thermal_inputs['output'] = os.path.join(self.result_dir,'all_results_drone_ir')
				thermal_inputs['facade_no'] = self.facade_drone_dirs
				
		else:
			ml_inputs['input_dir'] = upload_inputs['raw_dir'] = self.facade_dir_handheld
			ml_inputs['output_dir'] = upload_inputs['result_dir'] = self.facade_result_handheld
			upload_inputs['facade_no'] = self.facade_hhl_dirs

		if os.path.isdir(os.path.join(self.others_dir, 'raw_SD')):
			shutil.rmtree(os.path.join(self.others_dir, 'raw_SD'))
		return ml_inputs, thermal_inputs, upload_inputs
		

				 
	def run(self):      
		
		time_data_drone, facade_list_drone = self.extract_timesheet(True)
		if self.handheld:
			time_data_handheld, facade_list_handheld = self.extract_timesheet(False)
		self.create_standard_dirs()
		self.combine_dirs()
		self.allocate_imgs(time_data_drone, facade_list_drone)
		self.rename_facade_dirs()
		self.filter_overlap()
		
		if self.thermal:
			self.combine_dirs(True)
			self.allocate_imgs(time_data_drone, facade_list_drone, thermal=True)
			self.rename_facade_dirs(thermal=True)
			self.filter_overlap(thermal=True)
			ml_inputs, thermal_inputs, upload_inputs = self.process_ready(thermal=True)
		else:
			ml_inputs, thermal_inputs, upload_inputs = self.process_ready()

		if self.handheld:
			self.allocate_imgs(time_data_handheld, facade_list_handheld, drone=False)
			self.rename_facade_dirs(False)
			ml_inputs_hhl, _, upload_inputs_hhl = self.process_ready(drone=False)
			return ml_inputs, thermal_inputs, upload_inputs, ml_inputs_hhl, upload_inputs_hhl
	
		return ml_inputs, thermal_inputs, upload_inputs
								
if __name__ == '__main__':
	thermal = True
	handheld = True
	inspection_no = '1'
	buildingID = '5'
	name = 'bishan'
	preprocess = Preprocess(name, inspection_no, buildingID, frequency=[2], handheld=handheld, thermal=thermal)
	ml_inputs, thermal_inputs, upload_inputs, ml_inputs_hhl, upload_inputs_hhl = preprocess.run()

	print(ml_inputs)
	print('------------------------------')
	print(thermal_inputs)
	print('------------------------------')
	print(upload_inputs)
	print("------------------------------")
	print(ml_inputs_hhl)
	print("-------------------------------")
	print(upload_inputs_hhl)
	
	

	

