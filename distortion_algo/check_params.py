# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 11:36:23 2021

@author: cryst
"""

import numpy as np
from distortion_getcalibrationpara_v4 import get_camera_parameters

err, KK, distCoeffs, rvecs, tvecs = get_camera_parameters(9, 6, 'test_img_not_working')
parameter_arr2 = np.load(r'C:\Users\cryst\Work\Facade_inspection\thermal\Tomita\test_template_folder\calibration_parameters.npy', allow_pickle=True)
err2, KK2, distCoeffs2, rvecs2, tvecs2 = parameter_arr2[:]

assert err == err2
assert distCoeffs.all() == distCoeffs2.all()
assert np.array(rvecs).all() == np.array(rvecs2).all()
assert np.array(tvecs).all() == np.array(tvecs2).all()
assert KK.all() == KK2.all()

