from pyniryo import NiryoRobot, PoseObject
from pyniryo.ned.vision import uncompress_image, undistort_image, concat_imgs, show_img

observation_pose = PoseObject(0.18, -0.01, 0.35, 3.14, -0.0, -0.24)

# Connecting to robot
robot = NiryoRobot('<robot_ip_address>')
robot.calibrate_auto()

# Getting calibration param
mtx, dist = robot.get_camera_intrinsics()
# Moving to observation pose
robot.move(observation_pose)

while "User do not press Escape neither Q":
    # Getting image
    img_compressed = robot.get_img_compressed()
    # Uncompressing image
    img_raw = uncompress_image(img_compressed)
    # Undistorting
    img_undistort = undistort_image(img_raw, mtx, dist)

    # - Display
    # Concatenating raw image and undistorted image
    concat_ims = concat_imgs((img_raw, img_undistort))

    # Showing images
    key = show_img("Images raw & undistorted", concat_ims, wait_ms=30)
    if key in [27, ord("q")]:  # Will break loop if the user press Escape or Q
        break
