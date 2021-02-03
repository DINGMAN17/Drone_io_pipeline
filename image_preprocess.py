# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 14:43:28 2021

@author: cryst
"""
import os
import sys
import shutil
import glob
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

def crop(input_file, height, width):
	img = Image.open(input_file)
	img_width, img_height = img.size
	for i in range(img_height//height):
		for j in range(img_width//width):
			box = (j*width, i*height, (j+1)*width, (i+1)*height)
			yield img.crop(box)
			
def dir_create(path):
	'''
	creating a new directory and recursively deleting the contents of an 
	existing directory.
	'''
	if (os.path.exists(path)) and (os.listdir(path) != []):
		shutil.rmtree(path)
		os.makedirs(path)
	if not os.path.exists(path):
		os.makedirs(path)
			
def split_patch(input_img_dir, input_label_dir, prev_path, new_path, 
				height, width, start_num=1, copy_prev_dataset=True):
	
	image_dir = os.path.join(new_path, 'all', '640x480_images')   
	label_dir = os.path.join(new_path, 'all', '640x480_labels')
	pre_path_img = os.path.join(prev_path, 'all', '640x480_images')
	pre_path_labels = os.path.join(prev_path, 'all', '640x480_labels')
	if copy_prev_dataset:
		rename_label_num = rename_image_num = copy_previous_dataset(pre_path_img, pre_path_labels, image_dir, label_dir)[0]
	else:
		rename_image_num = rename_label_num = 0

	img_list = [f for f in
				os.listdir(input_img_dir)
				if os.path.isfile(os.path.join(input_img_dir, f))]
	file_num = 0
	
	for infile in img_list:
		infile_path = os.path.join(input_img_dir, infile)
		for k, piece in enumerate(crop(infile_path,
									   height, width), start_num):
			img = Image.new('RGB', (width, height), 255)
			img.paste(piece)
			# img_path = os.path.join(image_dir, 
			#                         infile.split('.')[0]+ '_'
			#                         + str(k).zfill(4) + '.png')
			img_path = os.path.join(image_dir, 
									str(rename_image_num).zfill(4) + '.jpg')
			img.save(img_path)
			rename_image_num += 1
			
		infile_path = os.path.join(input_label_dir,
								   infile.split('.')[0] + '.png')

		for k, piece in enumerate(crop(infile_path,
									   height, width), start_num):
			label = Image.new('RGB', (width, height), 255)
			label.paste(piece)
			# label_path = os.path.join(label_dir,
			#                         infile.split('.')[0] + '_'
			#                         + str(k).zfill(1) + '.png')
			label_path = os.path.join(label_dir, 
									str(rename_label_num).zfill(4) + '.png')
			label.save(label_path)
			rename_label_num += 1
		file_num += 1
		sys.stdout.write("\rFile %s was processed." % file_num)
		sys.stdout.flush()

def copy_previous_dataset(pre_path_img, pre_path_labels, image_dir, label_dir):
	'''
	combine the existing dataset with the new dataset by copying 
	the previous dataset to the new dataset directory
	Note: must follow the naming convention. e.g 'dataset1', 'dataset2'
	'''
	#copy previous dataset to the new dataset directory
	filenames = [f for f in
				 os.listdir(pre_path_img)
				 if os.path.isfile(os.path.join(pre_path_img, f))]
	for item in filenames:
		source_img = os.path.join(pre_path_img, item)
		source_label = os.path.join(pre_path_labels,
								   item.split('.')[0] + '.png')
		shutil.copy2(source_img, image_dir)
		shutil.copy2(source_label, label_dir)

	#get the maximum file name number for renaming the new dataset
	rename_num = len(os.listdir(image_dir))
	print("\r%s images  was copied from previous dataset." % rename_num)
	
	return rename_num, image_dir, label_dir

def create_current_dir(out_dir):
	'''
	reate the directory to store new dataset based on the previous dir name
	Note: must follow the naming convention. e.g 'dataset1', 'dataset2'
	'''
	#get directory names of previous and current dataset
	f_max = max([int(f[-1]) for f in
				os.listdir(out_dir)])
	prev_dataset = [f for f in
				os.listdir(out_dir)
				if int(f[-1]) == f_max][0]
	num = f_max+1
	name = list(prev_dataset)
	name[-1] = str(num)
	new_dataset = ''.join(name)
	prev_path = os.path.join(out_dir, prev_dataset)
	
	#create dirs for the new dataset
	new_path = os.path.join(out_dir, new_dataset) 
	image_dir = os.path.join(new_path, 'all', '640x480_images')   
	label_dir = os.path.join(new_path, 'all', '640x480_labels')
	if not os.path.exists(new_path):
		os.mkdir(new_path)
	dir_create(image_dir)
	dir_create(label_dir)

	return prev_path, new_path
	
		
def image_patch_plotter(images_path, offset, img_type='png'):
	'''
	show all parts of the splitted image, the original image is divided into 9 patches

	Parameters
	----------
	images_path : str
	offset : int
	'''
	if img_type == 'png':
		images_list = glob.glob(os.path.join(images_path, '*.png'))
	else:
		images_list = glob.glob(os.path.join(images_path, '*.jpg'))
	fig = plt.figure(figsize=(12, 10))
	columns = 3
	rows = 3
	ax = []
	for i in range(columns*rows):
		# create subplot and append to ax
		img = mpimg.imread(images_list[i+offset])
		ax.append(fig.add_subplot(rows, columns, i+1))
		ax[-1].set_title('image patch number '+ str(i+1))
		plt.imshow(img)
	plt.show() 
	
def image_label_plotter(image_path, label_path, image_number=None):
	'''
	Render the original image with its label.

	Parameters
	----------
	image_path : str
	label_path : str
	image_number : int, optional
		if not specified, it'll render a random image from the image list
	'''
	input_images_list = glob.glob(os.path.join(image_path, '*.jpg'))
	input_labels_list = glob.glob(os.path.join(label_path, '*.png'))
	if image_number is None:
		image_number = random.randint(0, len(input_images_list)-1)
	# for i, (image_path, label_path) in enumerate(zip(input_images_list,
	#                                             input_labels_list)):
	image_path, label_path = input_images_list[image_number-1],\
							 input_labels_list[image_number-1]
	fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(18, 9))
	image = mpimg.imread(image_path)
	label = mpimg.imread(label_path)
	ax1.set_title('Image ' + str(image_number))
	ax1.imshow(image)
	ax2.imshow(label)
	ax2.set_title('Label ' + str(image_number))
	 
def rescale(filename):
	'''
	Rescale image to 640x480 (might not be useful for XT2 images, depends on image quality)
	'''
	img = Image.open(filename)
	size = (640, 480)
	img.thumbnail(size, Image.ANTIALIAS)
	img.save(filename)

if __name__ == '__main__':
	 image_path = r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset\dataset3\labelme_output\JPEGImages'
	 label_path = r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset\dataset3\labelme_output\SegmentationClassPNG'
	 out_path = r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset'
	 prev_path, new_path = create_current_dir(out_path)
	 image_dir = os.path.join(new_path, 'all', '640x480_images')   
	 label_dir = os.path.join(new_path, 'all', '640x480_labels')
	 pre_path_img = os.path.join(prev_path, 'all', '640x480_images')
	 pre_path_labels = os.path.join(prev_path, 'all', '640x480_labels')
	 #copy_previous_dataset(pre_path_img, pre_path_labels, image_dir, label_dir)
	 #print(os.listdir(r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset\dataset3\all\640x480_images'))
	 split_patch(image_path, label_path, prev_path, new_path, 480, 640, 1, True)

	 #image_label_plotter(image_path, label_path) 
	 #image_patch_plotter(r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset_demo\output\640x480_images', 9, 'jpg')
	 #image_patch_plotter(r'C:\Users\cryst\Work\Facade_inspection\pipeline_design\Drone_io_pipeline-main\Test_image_preprocess\dataset_demo\output\640x480_labels', 9)
	#image_part_plotter(output_labels_list, 0)
	 #split_patch(image_path, label_path, out_path, 480, 640, 1, True)
	#rescale_image('C:/Users/cryst/Work/Facade_inspection/pipeline_design/DJI_0015_org.jpg')