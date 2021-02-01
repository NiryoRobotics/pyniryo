# Imports
from pyniryo import *

# Connecting to robot
niryo_robot = NiryoRobot("10.10.10.10")  # =< Replace by robot ip address

# Calibrating Robot
niryo_robot.calibrate_auto()
# Updating tool
niryo_robot.update_tool()

# Looping Forever
while True:
    # Moving to observation pause
    niryo_robot.move_pose(0.16, 0.0, 0.35, 0.0, 1.57, 0.0)

    # -- 1 -- ##
    img_compressed = niryo_robot.get_img_compressed()
    img = uncompress_image(img_compressed)
    if show_img_and_check_close("Image", img):
        break
    # // 1 // ##
    # -- 2 -- ##
    im_work = extract_img_workspace(img, workspace_ratio=1.0)
    if im_work is None:
        print("Unable to find markers")
        continue
    if show_img_and_check_close("Image Work", im_work):
        break
    # // 2 // ##

    # -- 3 -- ##
    low_thresh_list, high_thresh_list = [90, 115, 75], [115, 255, 255]
    img_thresh = threshold_hsv(im_work, low_thresh_list, high_thresh_list)
    if show_img_and_check_close("Thresh", img_thresh):
        break

    # // 3 // ##

    # -- 4 & 5 -- ##
    im_morpho = morphological_transformations(img_thresh, morpho_type=MorphoType.OPEN,
                                              kernel_shape=(5, 5), kernel_type=KernelType.ELLIPSE)
    if show_img_and_check_close("Morpho", im_morpho):
        break
    # // 4 & 5 // ##

    # -- 6 -- #
    best_contour = biggest_contour_finder(im_morpho)
    if len(best_contour) == 0:
        print("No blob found")
        continue
    show_img("Biggest Contour", draw_contours(im_morpho, [best_contour]))
    # // 6 // #
    # -- 7 & 8 -- #
    cx, cy = get_contour_barycenter(best_contour)
    height, width = img_thresh.shape
    x_rel = float(cx) / width
    y_rel = float(cy) / height
    angle = get_contour_angle(best_contour)
    # // 7 & 8// #
    # -- 9 -- #
    ws_name = "workspace_1"
    height_offset = 0.0
    obj_pose = niryo_robot.get_target_pose_from_rel(ws_name, height_offset,
                                                    x_rel, y_rel, angle)
    # // 9 // #

    # -- 10 -- #
    place_pose = PoseObject(
        x=0.0, y=0.20, z=0.3,
        roll=0.0, pitch=1.57, yaw=1.57
    )

    # Picking the object
    niryo_robot.pick_from_pose(obj_pose)

    # Placing the object
    niryo_robot.place_from_pose(place_pose)
    # // 10 // #

niryo_robot.go_to_sleep()
niryo_robot.close_connection()
