import flirimageextractor
from matplotlib import cm
import numpy as np

flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
flir.process_image('/home/paul/Workspaces/python/Drone_io_pipeline-main/Inference_Demo/test_thermal/DJI_0001_R.JPG')
thermal_image_np = flir.get_thermal_np()
np.save('thermal_image_array', thermal_image_np)
print(thermal_image_np)
flir.save_images(minTemp=20, maxTemp=35)
flir.plot()