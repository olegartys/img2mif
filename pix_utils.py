def bgr_to_rgb(bgr_pix):
	r = (bgr_pix & 0xff)
	g = (bgr_pix & 0x00ff00) >> 8
	b = (bgr_pix & 0xff0000) >> 16
	return (r << 16) | (g << 8) | (b)

def bgr(b, g, r):
	return (b << 16) | (g << 8) | (r)

def rgb(r, g, b):
	return (r << 16) | (g << 8) | (r)

def rgb_to_tuple(rgb):
	b = (rgb & 0xff)
	g = (rgb & 0x00ff00) >> 8
	r = (rgb & 0xff0000) >> 16
	return (r, g, b)

def bgr_to_tuple(bgr):
	r = (bgr & 0xff)
	g = (bgr & 0x00ff00) >> 8
	b = (bgr & 0xff0000) >> 16
	return (b, g, r)
