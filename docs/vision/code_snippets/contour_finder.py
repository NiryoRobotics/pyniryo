from pyniryo.vision import (threshold_hsv,
                            ColorHSV,
                            morphological_transformations,
                            MorphoType,
                            KernelType,
                            biggest_contours_finder,
                            draw_contours,
                            show_img,
                            show_img_and_wait_close)

img_threshold = threshold_hsv(img_test, *ColorHSV.ANY.value)
img_threshold = morphological_transformations(img_threshold,
                                              morpho_type=MorphoType.OPEN,
                                              kernel_shape=(11, 11),
                                              kernel_type=KernelType.ELLIPSE)

cnts = biggest_contours_finder(img_threshold, 3)

img_contours = draw_contours(img_threshold, cnts)

show_img("init", img_threshold)
show_img_and_wait_close("img with contours", img_contours)
