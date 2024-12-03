from pyniryo.vision import debug_markers, debug_threshold_color, show_img, show_img_and_wait_close, ColorHSV

debug_color = debug_threshold_color(img_test, ColorHSV.RED)
_status, debug_markers_im = debug_markers(img_test, workspace_ratio=1.0)

show_img("init", img_test)
show_img("debug_color", debug_color)
show_img_and_wait_close("debug_markers", debug_markers_im)
