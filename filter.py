import os
import sys
import cv2
import numpy as np

class ColorFilter:
	_green_low_range=np.array([35,43,46])
	_green_upp_range=np.array([77,255,200])

	_yellow_low_range=np.array([26,10,0])
	_yellow_upp_range=np.array([35,255,255])

	_purple_low_range=np.array([125,10,0])
	_purple_upp_range=np.array([155,255,255])

	_output_file_path=""

	def __init__(self, color, input_file):
		self._color = color
		self._input_file = input_file

	def do_crop_out(self, minx, miny, maxx, maxy):
		png_image = cv2.imread(self._output_file_path)[:,:,::-1]
		croped_image = png_image[miny:maxy, minx:maxx]
		cv2.imwrite(self._output_file_path, croped_image)
		return self._output_file_path

	def do_filter(self):
		jpg_image = cv2.imread(self._input_file)[:,:,::-1]
		hsv_image = cv2.cvtColor(jpg_image, cv2.COLOR_BGR2HSV)
		if (self._color=="green"):
			mask = cv2.inRange(hsv_image, self._green_low_range, self._green_upp_range)
		elif (self._color=="yellow"):
			mask = cv2.inRange(hsv_image, self._yellow_low_range, self._yellow_upp_range)
		elif (self._color=="purple"):
			mask = cv2.inRange(hsv_image, self._purple_low_range, self._purple_upp_range)


		image_masked = cv2.bitwise_and(jpg_image, jpg_image, mask=mask)
		png_image = cv2.cvtColor(image_masked, cv2.COLOR_BGR2RGB)
		out_dir_name = os.path.dirname(self._input_file)
		out_file_name = "filter_"+os.path.basename(self._input_file)
		out_file_name = out_file_name.split('.')[0]
		out_file_name = out_file_name+".png"
		self._output_file_path =os.path.join(out_dir_name,out_file_name)
		print(self._output_file_path)
		cv2.imwrite(self._output_file_path, png_image)

		return self._output_file_path
