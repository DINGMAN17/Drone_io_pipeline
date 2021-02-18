import os
import flirimageextractor
from matplotlib import pyplot as plt, cm
import numpy as np

def extract_data_from_dir(input_img_dir, palettes=None, minTemp=32, maxTemp=35):

	flir = flirimageextractor.FlirImageExtractor(palettes=[cm.gray_r])
	img_list = [f for f in
				os.listdir(input_img_dir)
				if os.path.isfile(os.path.join(input_img_dir, f))]

	temp_arr_path = os.path.join(input_img_dir, 'temperature_data')
	vis_img_path = os.path.join(input_img_dir, 'vis')
	
	for path in [temp_arr_path, vis_img_path]:
		if not os.path.exists(path):
			os.makedirs(path)
	
	for img in img_list:
		img_path = os.path.join(input_img_dir, img)
		out_path_np = os.path.join(temp_arr_path, img.split('.')[0]+'.npy')
		out_path_img_vis = os.path.join(vis_img_path, img.split('.')[0]+'_vis.png')
		flir.process_image(img_path)
		thermal_image_np = flir.get_thermal_np()
		np.save(out_path_np, thermal_image_np)
		#print(flir.get_rgb_np())

		#IR image processed with fixed temperature range
		flir.save_images(minTemp, maxTemp)

		fig, ax = plt.subplots()
		img = ax.imshow(thermal_image_np, cmap=cm.RdBu_r)
		fig.colorbar(img, ax=ax)
		fig.savefig(out_path_img_vis)

extract_data_from_dir('/home/paul/Workspaces/python/Drone_io_pipeline-main/Inference_Demo/02_outdoor_ground_results/')
        