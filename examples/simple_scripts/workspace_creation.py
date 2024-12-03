"""
This script allows to take 4 positions and to create a workspace from them
"""

# Imports
from pyniryo import NiryoRobot

import sys

if sys.version_info[0] == 2:
    input_func = raw_input
else:
    input_func = input

robot_ip_address = '<robot_ip_address>'

# Connecting to robot
niyro_robot = NiryoRobot(robot_ip_address)

niyro_robot.calibrate_auto()
niyro_robot.set_learning_mode(True)

# Asking user to type the new workspace name
ws_name = input_func("Enter name of new workspace. Name: ")

# Initializing useful variables
points = []
id_point = 1

while id_point < 5:  # Iterating over 4 markers
    input_func("Press enter when on point {}".format(id_point + 1))
    # Getting pose
    pose = niyro_robot.get_pose()
    points.append(pose)
    id_point += 1

# Creating workspace
niyro_robot.save_workspace_from_robot_poses(ws_name, *points)
# Leaving
niyro_robot.close_connection()
