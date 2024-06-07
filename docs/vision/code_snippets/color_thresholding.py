from pyniryo.vision import threshold_hsv, ColorHSV, show_img, show_img_and_wait_close

img_threshold_red = threshold_hsv(img_test, *ColorHSV.RED.value)

blue_min_hsv = [90, 85, 70]
blue_max_hsv = [125, 255, 255]

img_threshold_blue = threshold_hsv(img_test, list_min_hsv=blue_min_hsv, list_max_hsv=blue_max_hsv, reverse_hue=False)

show_img("img_threshold_red", img_threshold_red)

show_img_and_wait_close("img_threshold_blue", img_threshold_blue)
