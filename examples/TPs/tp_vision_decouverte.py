# Imports
from pyniryo import NiryoRobot, PoseObject, vision

# Connecting to robot
niryo_robot = NiryoRobot("10.10.10.10")  # =< Replace by robot ip address

# Calibrating Robot
niryo_robot.calibrate_auto()
# Updating tool
niryo_robot.update_tool()

# Looping Forever
while True:
    # Moving to observation pause
    niryo_robot.move(PoseObject(0.17, 0.0, 0.35, 3.14, 0.02, -0.02))

    # -- 1 -- ##
    img_compressed = niryo_robot.get_img_compressed()
    img = vision.uncompress_image(img_compressed)
    if vision.show_img_and_check_close("Image", img):
        break
    # // 1 // ##
    # -- 2 -- ##
    im_work = vision.extract_img_workspace(img, workspace_ratio=1.0)
    if im_work is None:
        print("Unable to find markers")
        continue
    if vision.show_img_and_check_close("Image Work", im_work):
        break
    # // 2 // ##

    # -- 3 -- ##
    low_thresh_list, high_thresh_list = [90, 115, 75], [115, 255, 255]
    img_thresh = vision.threshold_hsv(im_work, low_thresh_list, high_thresh_list)
    if vision.show_img_and_check_close("Thresh", img_thresh):
        break

    # // 3 // ##

    # -- 4 & 5 -- ##
    im_morpho = vision.morphological_transformations(img_thresh,
                                                     morpho_type=vision.MorphoType.OPEN,
                                                     kernel_shape=(5, 5),
                                                     kernel_type=vision.KernelType.ELLIPSE)
    if vision.show_img_and_check_close("Morpho", im_morpho):
        break
    # // 4 & 5 // ##

    # -- 6 -- #
    best_contour = vision.biggest_contour_finder(im_morpho)
    if len(best_contour) == 0:
        print("No blob found")
        continue
    vision.show_img("Biggest Contour", vision.draw_contours(im_morpho, [best_contour]))
    # // 6 // #
    # -- 7 & 8 -- #
    cx, cy = vision.get_contour_barycenter(best_contour)
    height, width = img_thresh.shape
    x_rel = float(cx) / width
    y_rel = float(cy) / height
    angle = vision.get_contour_angle(best_contour)
    # // 7 & 8// #
    # -- 9 -- #
    ws_name = "workspace_1"
    height_offset = 0.0
    obj_pose = niryo_robot.get_target_pose_from_rel(ws_name, height_offset, x_rel, y_rel, angle)
    # // 9 // #

    # -- 10 -- #
    place_pose = PoseObject(0.16, 0.0, 0.35, 3.14, -0.0, -0.01)

    # Picking the object
    niryo_robot.pick(obj_pose)

    # Placing the object
    niryo_robot.place(place_pose)
    # // 10 // #

niryo_robot.go_to_sleep()
niryo_robot.close_connection()
