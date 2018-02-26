import cv2
import numpy as np
from matplotlib import pyplot as plt

import re

from pix_utils import *
from mif_cmap import FileMifColorMap, WebPaletteMifColorMap

CMAP_PATH = "/home/olegartys/quartus_prj/4grade/lab8/SPDS_Lab_8_DE1_SoC_Default/VGA_DATA/index_logo.mif"

# Img -> mif constants
SOURCE_IMG_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.bmp"
# MIF_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/orig.mif"
MIF_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.mif"

# Mif -> img constants
SOURCE_MIF_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.mif"
IMG_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass_reversed.bmp"


def img_to_mif(img, mif_out_path, cmap):
	rows, cols = img.shape

	# Vectorize and apply fast pixel transform function

	pix_bgr_to_mif_bound = lambda bgr_pix : cmap.get_mif_pix(bgr_pix)

	pix_bgr_to_mif_vect = np.vectorize(pix_bgr_to_mif_bound)
	mif_img = pix_bgr_to_mif_vect(img)

	# Output data to the .mif file

	with open(mif_out_path, "w") as f:
		f.write("WIDTH = 8;\n")
		f.write("DEPTH = {};\n".format(rows * cols))
		f.write("\n")
		f.write("ADDRESS_RADIX = HEX;\n")
		f.write("DATA_RADIX = HEX;\n")
		f.write("\n")

		f.write("CONTENT BEGIN\n")

		i = 0
		for pix in np.nditer(mif_img):
			f.write("{:x}:{:x};\n".format(i, int(pix)))
			i += 1

		f.write("CONTENT END\n")

	return 0

def mif_to_img(mif_path, out_jpg_path, cmap):
	with open(mif_path) as f:
		lines = f.readlines()
		mif_orig_img = []
		bgr_orig_img = np.zeros([480, 640, 3])
		i = 0
		j = 0

		for line in lines:
			match_s = re.findall(r'(\S+):(\w+)', line)
			if len(match_s) != 0:
				mif_color = int(match_s[0][1], 16)
				mif_orig_img.append(mif_color)

		for mif_pix in mif_orig_img:
			bgr_pix = cmap.get_bgr_pix(mif_pix)
			bgr_orig_img[i, j] = bgr_to_tuple(bgr_pix)
			# bgr_orig_img[i, j] = rgb_to_tuple(bgr_to_rgb(bgr_pix))

			if j == 639:
				i += 1
				j = 0
			else:
				j += 1

		cv2.imwrite(out_jpg_path, bgr_orig_img)

	return 0

def merge_channels(img):
	rows, cols, _ = img.shape

	ret_img = np.zeros(shape=(rows,cols))
	for row in range(rows):
		for col in range(cols):
			b = img[row, col][0]
			g = img[row, col][1]
			r = img[row, col][2]
			ret_img[row, col] = bgr(b, g, r)
			# img[row, col] = rgb(r, g, b)

	return ret_img

def main():
	# Image is ALREADY in bgr
  
	_img = cv2.imread(SOURCE_IMG_PATH, cv2.IMREAD_COLOR)

	# Merge channels of the image into the one

	img = merge_channels(_img)

	img = img.astype(int)

	print(_img)
	print("=====CONVERTED=====")
	print(img)

	# Build color map

	cmap = WebPaletteMifColorMap()
	# cmap.dump_to_mif("webpalette_cmap.mif")

	print("--debug: bgr={} mif={}".format(img[0,0], cmap.get_mif_pix(img[0,0])))

	img_to_mif(img, MIF_OUT_PATH, cmap)

	# From mif generate image by the way FPGA does it

	cmap_file = FileMifColorMap("webpalette_cmap.mif")
	mif_to_img(SOURCE_MIF_PATH, IMG_OUT_PATH, cmap_file)

	return 0

def main_24():
	# Image is ALREADY in bgr
  
	_img = cv2.imread(SOURCE_IMG_PATH, cv2.IMREAD_COLOR)
	rows, cols, _ = _img.shape

	img = np.zeros(shape=(rows,cols))
	for row in range(rows):
		for col in range(cols):
			b = _img[row, col][0]
			g = _img[row, col][1]
			r = _img[row, col][2]
			# img[row, col] = bgr(b, g, r)
			img[row, col] = bgr(b, g, r)

	print(_img)

	print("=====CONVERTED=====")

	print(img)

	# Output data to the .mif file

	with open(MIF_OUT_PATH, "w") as f:
		f.write("WIDTH = 32;\n")
		f.write("DEPTH = {};\n".format(rows * cols))
		f.write("ADDRESS_RADIX = HEX;\n")
		f.write("DATA_RADIX = HEX;\n")

		f.write("CONTENT BEGIN\n")

		i = 0
		for pix in np.nditer(img):
			f.write("{:x}:{:x};\n".format(i, int(pix)))
			i += 1

		f.write("CONTENT END\n")

	return 0

if __name__ == "__main__":
	import sys
	sys.exit(main())


# def bgr_to_mif(cv_img, mif_cmap):
#   mif_image = []
#   rows, cols = cv_img.shape

#   for i in range(rows):
#     for j in range(cols):
#       k = cv_img[i, j]
#       mif_image.append(pix_bgr_to_mif(k, mif_cmap))

#   return mif_image
