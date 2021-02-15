#add colorbar
import numpy as np
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, cm

temperature_arr = np.load('/home/paul/Workspaces/python/Drone_io_pipeline-main/Thermal/thermal_image_array.npy', allow_pickle=True)
print(temperature_arr)

fig, ax = plt.subplots()
img = ax.imshow(temperature_arr, cmap=cm.gnuplot2)
fig.colorbar(img, ax=ax)

#plt.subplot()
#plt.imshow(temperature_arr, cmap=cm.gnuplot2)
fig.savefig('test_colorbar.png')
plt.show()

