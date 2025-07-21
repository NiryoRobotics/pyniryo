"""
This script shows how to use kinematics with PyNiryo
"""

from pyniryo import NiryoRobot, JointsPosition

simulation_mode = True
robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_simulation = "127.0.0.1"

robot_ip_address = robot_ip_address_simulation if simulation_mode else robot_ip_address_rpi

# Connecting to robot
niyro_robot = NiryoRobot(robot_ip_address)

# Calibrating Robot
niyro_robot.calibrate_auto()

# Getting initial pose
initial_pose = niyro_robot.get_pose()

# Calculating pose with FK and moving to this pose
pose_target = niyro_robot.forward_kinematics(JointsPosition(0.2, 0.0, -0.4, 0.0, 0.0, 0.0))
niyro_robot.move(pose_target)

# Calculating joints via IK and moving to these joints
joints_target = niyro_robot.inverse_kinematics(initial_pose)
niyro_robot.move(joints_target)

# Leaving
niyro_robot.set_learning_mode(True)
niyro_robot.close_connection()
