import sys
import cv2
import numpy as np
import colorsys
import matplotlib.colors as mcolors

class ColorInfo:
	def __init__(self,filename):
		png_image = cv2.imread(filename)
		hsv_image = cv2.cvtColor(png_image, cv2.COLOR_RGB2HSV)
		self._width = png_image.shape[1]
		self._height = png_image.shape[0]
		self._filename = filename
		self._png_image = png_image
		self._hsv_image = hsv_image
		self._H,self._S,self._V=cv2.split(self._hsv_image)

		self.count_h = 0
		self.sum_h = 0
		self.min_h = 255
		self.max_h = 0

		self.count_s = 0
		self.sum_s = 0
		self.min_s = 255
		self.max_s = 0
		self.count_v = 0
		self.sum_v = 0
		self.min_v = 255
		self.max_v = 0
		self.h_array=np.arange(0,256,1)
		self.s_array=np.arange(0,256,1)
		self.v_array=np.arange(0,256,1)
		self._r = 0
		self._g = 0
		self._b = 0
		self._minx = 2048 
		self._miny = 2048
		self._maxx = 0
		self._maxy = 0

	def handle_H(self):
		for y in range(0, self._height):
			for x in range(0, self._width):
				h_v = self._H[y][x]
				if h_v > 0:
					self._minx = min(x, self._minx)
					self._miny = min(y, self._miny)
					self._maxx = max(x, self._maxx)
					self._maxy = max(y, self._maxy) 
					self.h_array[h_v] = self.h_array[h_v]+1
					self.sum_h   = self.sum_h + h_v
					self.count_h = self.count_h + 1
					#self.min_h = min(h_v, self.min_h)
					#self.max_h = max(h_v, self.max_h)
		print (self._minx, self._miny, self._maxx, self._maxy)


	def handle_S(self):
		for s_line in self._S:
			for s_v in s_line:
				if s_v > 0:
					self.s_array[s_v] = self.s_array[s_v]+1
					self.sum_s   = self.sum_s + s_v
					self.count_s = self.count_s + 1
					#self.min_s = min(s_v, self.min_s)
					#self.max_s = max(s_v, self.max_s)

	def handle_V(self):
		for v_line in self._V:
			for v_v in v_line:
				if v_v > 0:
					self.v_array[v_v] = self.v_array[v_v]+1
					self.sum_v   = self.sum_v + v_v
					self.count_v = self.count_v + 1
					#self.min_v = min(v_v, self.min_v)
					#self.max_v = max(v_v, self.max_v)
	def compute_color(self):
		self.handle_H()
		self.handle_S()
		self.handle_V()

		real_h_count = 0
		real_h_sum = 0

		for i in range(0,255):
			if (self.h_array[i] < self.count_h*0.05):
				continue
			else:
				real_h_count = real_h_count + self.h_array[i]
				real_h_sum = real_h_sum + (self.h_array[i]*i)
		avg_h = real_h_sum/real_h_count

		real_s_count = 0
		real_s_sum = 0
		for i in range(0,255):
			if (self.s_array[i] < self.count_s*0.01):
				continue
			else:
				real_s_count = real_s_count + self.s_array[i]
				real_s_sum   = real_s_sum  + (self.s_array[i]*i)
		avg_s = real_s_sum/real_s_count

		real_v_count = 0
		real_v_sum = 0
		for i in range(0,255):
			if (self.v_array[i] < self.count_v*0.01):
				continue
			else:
				real_v_count = real_v_count + self.v_array[i]
				real_v_sum   = real_v_sum  + (self.v_array[i]*i)
		avg_v = real_v_sum/real_v_count

		_avg_h = self.sum_h/self.count_h
		_avg_s = self.sum_s/self.count_s
		_avg_v = self.sum_v/self.count_v

		h_f = avg_h/180
		s_f = avg_s/255
		v_f = avg_v/255

		(self._r, self._g, self._b) = colorsys.hsv_to_rgb(h_f, s_f, v_f)
		return {"color1":round(avg_h), "color2":round(avg_s), "color3":round(avg_v), "color4":round(_avg_h), "color5":round(_avg_s), "color6":round(_avg_v)}
