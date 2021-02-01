"""
This script allows to capture Ned's video streaming and to make some image processing on it
"""

# Imports
from pyniryo.api import *
import pyniryo.vision as vision

simulation_mode = True
# Set robot address
robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_simulation = "127.0.0.1"
robot_ip_address = robot_ip_address_simulation if simulation_mode else robot_ip_address_rpi

# Set Observation Pose. It's where the robot will be placed for streaming
observation_pose = PoseObject(
    x=0.2, y=0.0, z=0.34,
    roll=0, pitch=1.57, yaw=-0.2,
)


def video_stream(niyro_robot):
    # Getting calibration param
    mtx, dist = niyro_robot.get_camera_intrinsics()
    # Moving to observation pose
    niyro_robot.move_pose(*observation_pose.to_list())

    while "User do not press Escape neither Q":
        # Getting image
        img_compressed = niyro_robot.get_img_compressed()
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

        # - Display
        # Concatenating raw image and undistorted image
        concat_ims = vision.concat_imgs((img_raw, img_undistort))
        # Concatenating extracted workspace with markers annotation
        if img_workspace is not None:
            resized_img_workspace = vision.resize_img(img_workspace, height=res_img_markers.shape[0])
            res_img_markers = vision.concat_imgs((res_img_markers, resized_img_workspace))

        # Showing images
        vision.show_img("Images raw & undistorted", concat_ims, wait_ms=0)
        key = vision.show_img("Markers", res_img_markers, wait_ms=30)
        if key in [27, ord("q")]:  # Will break loop if the user press Escape or Q
            break

    niyro_robot.set_learning_mode(True)


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Launching main process
    video_stream(robot)
    # Releasing connection
    robot.close_connection()

