"""
This script shows 2 ways of making a vision pick and place.
You will need one workspace recorded in the Niryo studio
"""

# Imports
from pyniryo import *

# -- MUST Change these variables
simulation_mode = True
tool_used = ToolID.GRIPPER_1  # Tool used for picking
workspace_name = "workspace_1"  # Robot's Workspace Name
# Set robot address
robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_simulation = "127.0.0.1"
robot_ip_address = robot_ip_address_simulation if simulation_mode else robot_ip_address_rpi

# -- Should Change these variables
# The pose from where the image processing happens
observation_pose = PoseObject(
    x=0.18, y=0.0, z=0.35,
    roll=0.0, pitch=1.57, yaw=-0.2,
)

# Center of the conditioning area
place_pose = PoseObject(
    x=0.0, y=-0.23, z=0.12,
    roll=0.0, pitch=1.57, yaw=-1.57
)


# -- MAIN PROGRAM

def vision_pick_n_place_1(niyro_robot):
    # Loop
    try_without_success = 0
    while try_without_success < 5:
        # Moving to observation pose
        niyro_robot.move_pose(*observation_pose.to_list())
        # Trying to get target pose using camera
        ret = niyro_robot.get_target_pose_from_cam(workspace_name,
                                                   height_offset=0.0,
                                                   shape=ObjectShape.ANY,
                                                   color=ObjectColor.ANY)
        obj_found, obj_pose, shape, color = ret
        if not obj_found:
            try_without_success += 1
            continue

        # At this point, we can do specific operation on the obj_pose if we want
        # to catch the object with a tilted angle for instance
        # ---
        # ---

        # Everything is good, so we going to pick the object
        niyro_robot.pick_from_pose(obj_pose)

        # Going to place
        niyro_robot.place_from_pose(place_pose)
        break


def vision_pick_n_place_2(niyro_robot):
    # Loop
    try_without_success = 0
    while try_without_success < 5:
        # Moving to observation pose
        niyro_robot.move_pose(*observation_pose.to_list())
        # Trying to pick target using camera
        ret = niyro_robot.vision_pick(workspace_name,
                                      height_offset=0.0,
                                      shape=ObjectShape.ANY,
                                      color=ObjectColor.ANY)
        obj_found, shape_ret, color_ret = ret
        if not obj_found:
            try_without_success += 1
            continue
        # Vision pick has succeed which means that Ned should have already catch the object !

        # Everything is good, so we going to place the object
        niyro_robot.place_from_pose(place_pose)
        break


if __name__ == '__main__':
    # Connect to robot
    client = NiryoRobot(robot_ip_address)
    # Changing tool
    client.update_tool()
    # Calibrate robot if robot needs calibration
    client.calibrate(CalibrateMode.AUTO)
    # Launching main process
    print("Starting Version 1")
    vision_pick_n_place_1(client)
    print("Starting Version 2")
    vision_pick_n_place_2(client)
    # Ending
    client.go_to_sleep()
    # Releasing connection
    client.close_connection()
