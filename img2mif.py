import cv2
from matplotlib import pyplot as plt
import numpy as np

import re
import argparse
import tempfile

from pix_utils import *
from mif_cmap import FileMifColorMap, WebPaletteMifColorMap
import mif_convert

CMAP_PATH = "/home/olegartys/quartus_prj/4grade/lab8/SPDS_Lab_8_DE1_SoC_Default/VGA_DATA/index_logo.mif"

# Img -> mif constants
SOURCE_IMG_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.bmp"
# MIF_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/orig.mif"
MIF_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.mif"

# Mif -> img constants
SOURCE_MIF_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass.mif"
IMG_OUT_PATH = "/home/olegartys/quartus_prj/4grade/lab8/snowmass_reversed.bmp"

def merge_channels(img):
	rows, cols, _ = img.shape

	ret_img = np.zeros(shape=(rows,cols))
	for row in range(rows):
		for col in range(cols):
			b = img[row, col][0]
			g = img[row, col][1]
			r = img[row, col][2]
			ret_img[row, col] = bgr(b, g, r)

	return ret_img

def parse_args(argv):
	parser = argparse.ArgumentParser(description='Image to MIF converted. By default webpalette colormap is used.')

	parser.add_argument('image', help='Path to the image to be converted')
	parser.add_argument('mif_image', help='Path to the output MIF image')

	parser.add_argument('-r', '--reverse', action='store_true',
		help='Perform a reverse operation: convert MIF image to the format \
			specified in arguments')
	parser.add_argument('--colormap', default='img_index.mif',
		help='Name of the output MIF colormap file')

	return parser.parse_args()

def main(argv):
	args = parse_args(argv)

	img_path = args.image
	mif_img_path = args.mif_image
	colormap_path = args.colormap
	is_reverse = args.reverse

	if not is_reverse:
		# Image is ALREADY in bgr

		_img = cv2.imread(img_path, cv2.IMREAD_COLOR)

		# Merge channels of the image into the one

		img = merge_channels(_img)

		img = img.astype(int)

		# Build color map

		cmap = WebPaletteMifColorMap()
		cmap.dump_to_mif(colormap_path)

		# And convert

		mif_convert.img_to_mif(img, mif_img_path, cmap)

	else:
		# Dump webpalette colormap into temporary file.
		# We will need it only to simulate the FPGA logic that decodes
		# MIF image through colormap.

		fd_webpalette_cmap = tempfile.NamedTemporaryFile(delete=False)

		cmap = WebPaletteMifColorMap()
		cmap.dump_to_mif(fd_webpalette_cmap.name)

		fd_webpalette_cmap.close()

		# From MIF file generate image by the way FPGA does it through
		# the webpalette colormap

		cmap_file = FileMifColorMap(fd_webpalette_cmap.name)
		mif_convert.mif_to_img(mif_img_path, img_path, cmap_file)

	return 0

if __name__ == "__main__":
	import sys
	sys.exit(main(sys.argv))

# def main_24():
# 	# Image is ALREADY in bgr
  
# 	_img = cv2.imread(SOURCE_IMG_PATH, cv2.IMREAD_COLOR)
# 	rows, cols, _ = _img.shape

# 	img = np.zeros(shape=(rows,cols))
# 	for row in range(rows):
# 		for col in range(cols):
# 			b = _img[row, col][0]
# 			g = _img[row, col][1]
# 			r = _img[row, col][2]
# 			# img[row, col] = bgr(b, g, r)
# 			img[row, col] = bgr(b, g, r)

# 	print(_img)

# 	print("=====CONVERTED=====")

# 	print(img)

# 	# Output data to the .mif file

# 	with open(MIF_OUT_PATH, "w") as f:
# 		f.write("WIDTH = 32;\n")
# 		f.write("DEPTH = {};\n".format(rows * cols))
# 		f.write("ADDRESS_RADIX = HEX;\n")
# 		f.write("DATA_RADIX = HEX;\n")

# 		f.write("CONTENT BEGIN\n")

# 		i = 0
# 		for pix in np.nditer(img):
# 			f.write("{:x}:{:x};\n".format(i, int(pix)))
# 			i += 1

# 		f.write("CONTENT END\n")

# 	return 0
