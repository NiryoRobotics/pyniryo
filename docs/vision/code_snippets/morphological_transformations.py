from pyniryo.ned.vision import (threshold_hsv,
                                ColorHSV,
                                morphological_transformations,
                                MorphoType,
                                KernelType,
                                show_img,
                                show_img_and_wait_close)

img_threshold = threshold_hsv(img_test, *ColorHSV.ANY.value)

img_close = morphological_transformations(img_threshold,
                                          morpho_type=MorphoType.CLOSE,
                                          kernel_shape=(11, 11),
                                          kernel_type=KernelType.ELLIPSE)

img_erode = morphological_transformations(img_threshold,
                                          morpho_type=MorphoType.ERODE,
                                          kernel_shape=(9, 9),
                                          kernel_type=KernelType.RECT)

show_img("img_threshold", img_threshold)
show_img("img_erode", img_erode)
show_img_and_wait_close("img_close", img_close)
