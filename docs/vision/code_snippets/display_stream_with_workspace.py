from pyniryo import NiryoRobot, PoseObject
from pyniryo import vision

# Connecting to robot
robot = NiryoRobot('<robot_ip_address>')
robot.calibrate_auto()

# Moving to observation pose
observation_pose = PoseObject(0.2, 0.0, 0.3, 0.0, 1.56, 0.0)
robot.move(observation_pose)

while "User do not press Escape neither Q":
    # Getting image
    img_compressed = robot.get_img_compressed()
    # Uncompressing image
    img = vision.uncompress_image(img_compressed)
    # Trying to find markers
    workspace_found, res_img_markers = vision.debug_markers(img)
    # Trying to extract workspace if possible
    if workspace_found:
        img_workspace = vision.extract_img_workspace(img, workspace_ratio=1.0)
    else:
        img_workspace = None

    ...

    # - Display
    # Concatenating extracted workspace with markers annotation
    if img_workspace is not None:
        resized_img_workspace = vision.resize_img(img_workspace, height=res_img_markers.shape[0])
        img = vision.concat_imgs((img, res_img_markers, resized_img_workspace))
    # Showing images
    key = vision.show_img("Image & Markers", img)
    if key in [27, ord("q")]:  # Will break loop if the user press Escape or Q
        break
