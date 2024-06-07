# Imports
from pyniryo import NiryoRobot, PoseObject

# - Constants
workspace_name = "workspace_1"  # Robot's Workspace Name
robot_ip_address = '<robot_ip_address>'

# The pose from where the image processing happens
observation_pose = PoseObject(0.16, 0.0, 0.35, 3.14, 0.0, 0.0)
# Place pose
place_pose = PoseObject(0.01, -0.2, 0.12, 3.14, -0.01, -1.5)

# - Initialization

# Connect to robot
robot = NiryoRobot(robot_ip_address)
# Calibrate robot if the robot needs calibration
robot.calibrate_auto()
# Updating tool
robot.update_tool()
