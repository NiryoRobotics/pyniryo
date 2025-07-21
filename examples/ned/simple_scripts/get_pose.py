"""
Little Script which shows how to read a position with PyNiryo
"""
# !/usr/bin/env python

from pyniryo import NiryoRobot
import sys

if sys.version_info[0] == 2:
    input_func = raw_input
else:
    input_func = input


# Connecting to robot
niryo_robot = NiryoRobot(ip_address="10.10.10.10")

niryo_robot.calibrate_auto()

while "User to not quit":
    # Going to learning mode
    niryo_robot.set_learning_mode(True)

    input_func("Press enter to switch to turn learning mode off")
    niryo_robot.set_learning_mode(False)

    # Reading pose and displaying it
    pose = niryo_robot.get_pose()
    print(pose)
    if input_func("Press enter to get new pose / q to leave ") == 'q':
        break
niryo_robot.set_learning_mode(True)

niryo_robot.close_connection()
