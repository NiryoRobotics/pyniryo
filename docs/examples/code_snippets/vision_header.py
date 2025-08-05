# Imports
from pyniryo import NiryoRobot, PoseObject

# - Constants
workspace_name = "workspace_1"  # Robot's Workspace Name
robot_ip_address = '<robot_ip_address>'

# The pose from where the image processing happens
observation_pose = PoseObject(0.18, 0.0, 0.34, 0.0, 1.56, 0.0)
# Place pose
place_pose = PoseObject(0.03, -0.25, 0.1, 0.0, 1.56, -1.56)

# - Initialization

# Connect to robot
robot = NiryoRobot(robot_ip_address)
# Calibrate robot if the robot needs calibration
robot.calibrate_auto()
# Updating tool
robot.update_tool()
