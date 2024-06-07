# Imports
from pyniryo import NiryoRobot, PoseObject, ObjectShape, ObjectColor

simulation_mode = True

# Set robot address & workspace name
if simulation_mode:
    robot_ip_address, workspace_name = "127.0.0.1", "gazebo_1"
else:
    robot_ip_address, workspace_name = "10.10.10.10", "workspace_1"

# -- Should Change these variables
# The pose from where the image processing happens
observation_pose = PoseObject(0.18, 0.0, 0.35, -3.14, -0.04, -0.19)

# First conditioning pose
place_pose_simulation = PoseObject(0.31, -0.12, 0.1, 3.14, -0.01, -0.01)
place_pose_reality = PoseObject(0.3, -0.11, 0.1, 3.14, -0.0, 0.01)
offset_y_between_place = -0.055

if simulation_mode:
    place_pose = place_pose_simulation
else:
    place_pose = place_pose_reality

# -- MAIN PROGRAM


def vision_pick_n_place(niyro_robot: NiryoRobot):
    # Loop
    try_without_success = 0
    catch_count = 0
    while try_without_success < 3:
        # Moving to observation pose
        niyro_robot.move(observation_pose)
        # Trying to pick target using camera
        ret = niyro_robot.vision_pick(workspace_name, height_offset=0.0, shape=ObjectShape.ANY, color=ObjectColor.ANY)
        obj_found, _, _ = ret
        if not obj_found:
            try_without_success += 1
            continue

        # Everything is good, so we going to place the object
        new_place_pose = place_pose.copy_with_offsets(x_offset=offset_y_between_place * catch_count)
        niyro_robot.place(new_place_pose)
        catch_count += 1


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Update tool
    robot.update_tool()
    # Launching main process
    vision_pick_n_place(robot)
    # Releasing connection
    robot.close_connection()
