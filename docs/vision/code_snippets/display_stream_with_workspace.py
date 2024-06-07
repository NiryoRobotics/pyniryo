from pyniryo import NiryoRobot, PoseObject
from pyniryo import vision

# Connecting to robot
robot = NiryoRobot('<robot_ip_address>')
robot.calibrate_auto()

# Getting calibration param
mtx, dist = robot.get_camera_intrinsics()
# Moving to observation pose
observation_pose = PoseObject(0.2, 0.0, 0.3, 3.14, -0.01, -0.01)
robot.move(observation_pose)

while "User do not press Escape neither Q":
    # Getting image
    img_compressed = robot.get_img_compressed()
    # Uncompressing image
    img_raw = vision.uncompress_image(img_compressed)
    # Undistorting
    img_undistort = vision.undistort_image(img_raw, mtx, dist)
    # Trying to find markers
    workspace_found, res_img_markers = vision.debug_markers(img_undistort)
    # Trying to extract workspace if possible
    if workspace_found:
        img_workspace = vision.extract_img_workspace(img_undistort, workspace_ratio=1.0)
    else:
        img_workspace = None

    ...

    # - Display
    # Concatenating raw image and undistorted image
    concat_ims = vision.concat_imgs((img_raw, img_undistort))
    # Concatenating extracted workspace with markers annotation
    if img_workspace is not None:
        resized_img_workspace = vision.resize_img(img_workspace, height=res_img_markers.shape[0])
        res_img_markers = vision.concat_imgs((res_img_markers, resized_img_workspace))
    # Showing images
    vision.show_img("Images raw & undistorted", concat_ims)
    key = vision.show_img("Markers", res_img_markers, wait_ms=30)
    if key in [27, ord("q")]:  # Will break loop if the user press Escape or Q
        break
