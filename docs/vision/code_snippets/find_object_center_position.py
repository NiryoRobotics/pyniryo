from pyniryo import vision

img_threshold = vision.threshold_hsv(img_test, *vision.ColorHSV.ANY.value)
img_threshold = vision.morphological_transformations(img_threshold,
                                                     morpho_type=vision.MorphoType.OPEN,
                                                     kernel_shape=(11, 11),
                                                     kernel_type=vision.KernelType.ELLIPSE)

cnt = vision.biggest_contour_finder(img_threshold)

cnt_barycenter = vision.get_contour_barycenter(cnt)
cx, cy = cnt_barycenter
cnt_angle = vision.get_contour_angle(cnt)

img_debug = vision.draw_contours(img_threshold, [cnt])
img_debug = vision.draw_barycenter(img_debug, cx, cy)
img_debug = vision.draw_angle(img_debug, cx, cy, cnt_angle)
vision.show_img("Image with contours, barycenter and angle", img_debug, wait_ms=30)
