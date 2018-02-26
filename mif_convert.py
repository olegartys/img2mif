import numpy as np
import re

import cv2

from pix_utils import *

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

def img_to_mif(img_path, mif_out_path, cmap):
	# Image is ALREADY in bgr

	_img = cv2.imread(img_path, cv2.IMREAD_COLOR)

	# Merge channels of the image into the one

	img = merge_channels(_img)

	img = img.astype(int)

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
