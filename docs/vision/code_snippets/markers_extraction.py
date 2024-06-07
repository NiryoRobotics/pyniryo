from pyniryo import extract_img_workspace, show_img, show_img_and_wait_close

status, im_work = extract_img_workspace(img, workspace_ratio=1.0)
show_img("init", img_test)
show_img_and_wait_close("img_workspace", img_workspace)
