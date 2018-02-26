import re
from abc import ABC, abstractmethod

from pix_utils import *

class AbstractMifColorMap(ABC):
	@abstractmethod
	def get_bgr_pix(self, mif_pix):
 		pass

	@abstractmethod
	def get_mif_pix(self, bgr_pix):
		pass

class FileMifColorMap(AbstractMifColorMap):
	def __init__(self, mif_colormap_path):
		self.__cmap, self.__cmap_reversed = \
			FileMifColorMap.__init_from_file(mif_colormap_path)

	def get_bgr_pix(self, mif_pix):
		return self.__cmap[mif_pix]

	def get_mif_pix(self, bgr_pix):
		return FileMifColorMap.__pix_bgr_to_mif(bgr_pix, self.__cmap)

	def img(self):
		return __dump(self.__cmap)

	def dump_to_img(self, out_path):
		cmap_img = FileMifColorMap.__dump(self.__cmap)
		cv2.imwrite(out_path, cmap_img)

	@staticmethod
	def __pix_bgr_to_mif(bgr_color, mif_cmap):
		delta = 10000000000000
		mif_color_index = 0

		i = 0
		for cur_mif_color in mif_cmap:
			cur_delta = abs(bgr_to_rgb(bgr_color) - bgr_to_rgb(cur_mif_color))
			if cur_delta < delta:
				delta = cur_delta
				mif_color_index = i

			i += 1

		return mif_color_index

	@staticmethod
	def __init_from_file(mif_colormap_path):
		with open(mif_colormap_path) as f:
			cmap = []
			cmap_reversed = dict()

			lines = f.readlines()
			for line in lines:
				match_s = re.findall(r'(\S+):(\w+)', line)
				if len(match_s) != 0:
					mif_color = int(match_s[0][0], 16)
					bgr_color = int(match_s[0][1], 16)
					# rgb_color = bgr_to_rgb(bgr_color)
					# self.__cmap.append(rgb_color)

					# Store mif -> bgr mapping as plain list since mif range
					# is [0; ff]
					cmap.append(bgr_color)

					cmap_reversed[bgr_color] = mif_color

			return (cmap, cmap_reversed,)

	@staticmethod
	def __dump(cmap):
		color_width = 4
		color_height = 300
		color_count = len(cmap)

		cur_color = 0

		img = np.zeros([color_height, color_count * color_width, 3])

		for color in cmap:
			rgb_tup = rgb_to_tuple(color)

			for i in range(color_height):
				for j in range(color_width):
					img[i, j + cur_color*color_width] = rgb_tup

			cur_color += 1

		return img

class WebPaletteMifColorMap(AbstractMifColorMap):
	WIDTH = 24
	DEPTH = 256

	def __init__(self):
		pass

	def get_bgr_pix(self, mif_pix):
		r = (mif_pix & 0xe0)
		g = (mif_pix & 0x1c) << 3
		b = (mif_pix & 0x03) << 6 

		return (b << 16) | (g << 8) | (r)

	def get_mif_pix(self, bgr_pix):
		b, g, r = bgr_to_tuple(bgr_pix)

		return (r & 0xe0) + ((g >> 3) & 0x1c) + (b >> 6)

	def dump_to_mif(self, cmap_mif_out_path):
		with open(cmap_mif_out_path, "w") as f:
			f.write("WIDTH = {};\n".format(WebPaletteMifColorMap.WIDTH))
			f.write("DEPTH = {};\n".format(WebPaletteMifColorMap.DEPTH))
			f.write("ADDRESS_RADIX = HEX;\n")
			f.write("DATA_RADIX = HEX;\n")

			f.write("CONTENT BEGIN\n")

			for i in range(WebPaletteMifColorMap.DEPTH):
				f.write("{:x}:{:x};\n".format(i, self.get_bgr_pix(i)))

			f.write("CONTENT END\n")
