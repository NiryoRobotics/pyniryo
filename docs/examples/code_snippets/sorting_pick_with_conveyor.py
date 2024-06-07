from vision_header import robot, workspace_name, observation_pose, place_pose
from pyniryo import ObjectColor, ObjectShape

# Initializing variables
offset_size = 0.05
max_catch_count = 4
shape_expected = ObjectShape.CIRCLE
color_expected = ObjectColor.RED

conveyor_id = robot.set_conveyor()

catch_count = 0
while catch_count < max_catch_count:
    # Turning conveyor on
    robot.run_conveyor(conveyor_id)
    # Moving to observation pose
    robot.move(observation_pose)
    # Check if object is in the workspace
    obj_found, pos_array, shape, color = robot.detect_object(workspace_name, shape=shape_expected, color=color_expected)
    if not obj_found:
        robot.wait(0.5)  # Wait to let the conveyor turn a bit
        continue
    # Stopping conveyor
    robot.stop_conveyor(conveyor_id)
    # Making a vision pick
    obj_found, shape, color = robot.vision_pick(workspace_name, shape=shape_expected, color=color_expected)
    if not obj_found:  # If visual pick did not work
        continue

    # Calculate place pose and going to place the object
    next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
    robot.place(next_place_pose)

    catch_count += 1

# Stopping & unsetting conveyor
robot.stop_conveyor(conveyor_id)
robot.unset_conveyor(conveyor_id)

robot.go_to_sleep()
