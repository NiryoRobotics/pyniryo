"""
This script shows an example of how to use Ned's vision to
make a conditioning with any of the objects supplied with the Vision Kit
The script works in 2 ways:
- One where all the vision process is made on the robot
- One where the vision process is made on the computer

The first one shows how easy it is to use Ned's vision kit with PyNiryo
The second demonstrates a way to do image processing from user's computer. It highlights
the fact that the user can imagine every type of process on his computer.

The objects will be conditioned in a grid of dimension grid_dimension. If the grid is completed,
objects will be pack over the lower level
"""

from pyniryo import NiryoRobot, PoseObject, ObjectShape, ObjectColor, vision
import cv2

# -- MUST Change these variables
simulation_mode = True
if simulation_mode:
    robot_ip_address, workspace_name = "127.0.0.1", "gazebo_1"
else:
    robot_ip_address, workspace_name = "10.10.10.10", "workspace_1"

# -- Can Change these variables
grid_dimension = (3, 3)  # conditioning grid dimension
vision_process_on_robot = False  # boolean to indicate if the image processing append on the Robot
display_stream = True  # Only used if vision on computer

# -- Should Change these variables
# The pose from where the image processing happens
observation_pose = PoseObject(0.16, -0.0, 0.32, 3.14, 0.12, -0.01)

# Center of the conditioning area
center_conditioning_pose = PoseObject(0.0, -0.25, 0.12, 3.14, -0.01, -1.57)

# -- MAIN PROGRAM


def process(niryo_robot: NiryoRobot):
    """
    :type niryo_robot: NiryoRobot
    :rtype: None
    """
    # Initializing variables
    obj_pose = None
    try_without_success = 0
    count = 0
    if not vision_process_on_robot:
        mtx, dist = niryo_robot.get_camera_intrinsics()
    else:
        mtx = dist = None
    # Loop
    while try_without_success < 5:
        # Moving to observation pose
        niryo_robot.move(observation_pose)

        if vision_process_on_robot:
            ret = niryo_robot.get_target_pose_from_cam(workspace_name,
                                                       height_offset=0.0,
                                                       shape=ObjectShape.ANY,
                                                       color=ObjectColor.ANY)
            obj_found, obj_pose, _, _ = ret

        else:  # Home made image processing
            img_compressed = niryo_robot.get_img_compressed()
            img = vision.uncompress_image(img_compressed)
            img = vision.undistort_image(img, mtx, dist) # on Ned2, needed only for versions < v5.8.3-b62
            # extracting working area
            im_work = vision.extract_img_workspace(img, workspace_ratio=1.0)
            if im_work is None:
                print("Unable to find markers")
                try_without_success += 1
                if display_stream:
                    cv2.imshow("Last image saw", img)
                    cv2.waitKey(25)
                continue

            # Applying Threshold on ObjectColor
            color_hsv_setting = vision.ColorHSV.ANY.value
            img_thresh = vision.threshold_hsv(im_work, *color_hsv_setting)

            if display_stream:
                vision.show_img("Last image saw", img, wait_ms=100)
                vision.show_img("Image thresh", img_thresh, wait_ms=100)
            # Getting biggest contour/blob from threshold image
            contour = vision.biggest_contour_finder(img_thresh)
            if contour is None or len(contour) == 0:
                print("No blob found")
                obj_found = False
            else:
                img_thresh_rgb_w_contour = vision.draw_contours(img_thresh, [contour])

                # Getting contour/blob center and angle
                cx, cy = vision.get_contour_barycenter(contour)
                img_thresh_rgb_w_contour = vision.draw_barycenter(img_thresh_rgb_w_contour, cx, cy)
                cx_rel, cy_rel = vision.relative_pos_from_pixels(im_work, cx, cy)

                angle = vision.get_contour_angle(contour)
                img_thresh_rgb_w_contour = vision.draw_angle(img_thresh_rgb_w_contour, cx, cy, angle)

                vision.show_img("Image thresh", img_thresh_rgb_w_contour, wait_ms=30)

                # Getting object world pose from relative pose
                obj_pose = niryo_robot.get_target_pose_from_rel(workspace_name,
                                                                height_offset=0.0,
                                                                x_rel=cx_rel,
                                                                y_rel=cy_rel,
                                                                yaw_rel=angle)
                obj_found = True
        if not obj_found:
            try_without_success += 1
            continue
        # Everything is good, so we going to object
        niryo_robot.pick(obj_pose)

        # Computing new place pose
        offset_x = count % grid_dimension[0] - grid_dimension[0] // 2
        offset_y = (count // grid_dimension[1]) % 3 - grid_dimension[1] // 2
        offset_z = count // (grid_dimension[0] * grid_dimension[1])
        place_pose = center_conditioning_pose.copy_with_offsets(0.05 * offset_x, 0.05 * offset_y, 0.025 * offset_z)

        # Placing
        niryo_robot.place(place_pose)

        try_without_success = 0
        count += 1


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Changing tool
    robot.update_tool()
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Launching main process
    process(robot)
    # Ending
    robot.go_to_sleep()
    # Releasing connection
    robot.close_connection()
