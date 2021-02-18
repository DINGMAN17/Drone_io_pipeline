#add colorbar
from PIL import Image, ImageEnhance
import numpy as np
import os
import glob
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, cm
import matplotlib.colors as mcolors

def add_colorbar(filename, palette):
	temperature_arr = np.load(filename, allow_pickle=True)
	print(temperature_arr)

	fig, ax = plt.subplots()
	img = ax.imshow(temperature_arr, cmap=palette)
	fig.colorbar(img, ax=ax)

	#plt.subplot()
	#plt.imshow(temperature_arr, cmap=cm.gnuplot2)
	fig.savefig('test_colorbar.png')
	plt.show()

#add_colorbar('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/thermal_image_array.npy', cm.gnuplot2)


def add_colorbar_jpg(filename, palette=None):
	im = Image.open(filename)
	imnew = im.convert("P", palette=Image.ADAPTIVE)#, dither=Image.NONE)
	data = np.asarray(imnew)
	palette = imnew.getpalette()

	colors = np.array(palette).reshape(-1, 3) / 255.0
	cmap = mcolors.ListedColormap(colors)

	fig, axes = plt.subplots(nrows=3, figsize=(8, 15))
	axes[0].imshow(im)

	for cm, ax in zip(['gray_r', cmap], axes[1:]):
		cax = ax.imshow(data, cmap=cm)
		mesh = ax.pcolormesh(data, cmap = cm)
		fig.colorbar(cax, ax=ax) #boundaries=np.linspace(25,2,35)

	fig.tight_layout()
	plt.show()

#add_colorbar_jpg('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/test_image')

def save_from_array(filename, palette=cm.gray, minTemp=25, maxTemp=30):
	temperature_arr = np.load(filename, allow_pickle=True)
	thermal_normalized = (temperature_arr - minTemp) / (maxTemp - minTemp)

	print(thermal_normalized)
	img_thermal = Image.fromarray(palette(thermal_normalized, bytes=True))

	# convert to jpeg and enhance
	img_thermal = img_thermal.convert("RGB")
	enhancer = ImageEnhance.Sharpness(img_thermal)
	img_thermal = enhancer.enhance(3)

	img_thermal.save('test_image', "jpeg", quality=100)

def delete_images(input_dir, prefix=None):
	for i in glob.glob(os.path.join(input_dir, prefix)):
		os.remove(i)
	#os.remove(file) for file in os.listdir('path/to/directory') if file.endswith('.png')

#save_from_array('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/thermal_image_array.npy')
#add_colorbar_jpg('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/test_image')
#name = '/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/thermal_image_array.npy'
#print(name.split('/')[-1].split('.')[0])
delete_images('/home/paul/Workspaces/python/Drone_io_pipeline-main/Inference_Demo/02_outdoor_ground_results/', '*gray.JPG')
