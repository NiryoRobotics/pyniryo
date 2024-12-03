from vision_header import robot, observation_pose, workspace_name, place_pose

# Initializing variables
offset_size = 0.05
max_catch_count = 4

# Loop until enough objects have been caught
catch_count = 0
while catch_count < max_catch_count:
    # Moving to observation pose
    robot.move(observation_pose)

    # Trying to get object via Vision Pick
    obj_found, shape, color = robot.vision_pick(workspace_name)
    if not obj_found:
        robot.wait(0.1)
        continue

    # Calculate place pose and going to place the object
    next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
    robot.place_from_pose(next_place_pose)

    catch_count += 1

robot.go_to_sleep()
