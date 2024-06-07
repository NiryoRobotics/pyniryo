from vision_header import robot, observation_pose, workspace_name, place_pose
from pyniryo import ObjectColor

# Distance between elements
offset_size = 0.05
max_failure_count = 3

# Dict to write catch history
count_dict = {
    ObjectColor.BLUE: 0,
    ObjectColor.RED: 0,
    ObjectColor.GREEN: 0,
}

try_without_success = 0
# Loop until too much failures
while try_without_success < max_failure_count:
    # Moving to observation pose
    robot.move(observation_pose)
    # Trying to get object via Vision Pick
    obj_found, shape, color = robot.vision_pick(workspace_name)
    if not obj_found:
        try_without_success += 1
        robot.wait(0.1)
        continue

    # Choose X position according to how the color line is filled
    offset_x_ind = count_dict[color]

    # Choose Y position according to ObjectColor
    if color == ObjectColor.BLUE:
        offset_y_ind = -1
    elif color == ObjectColor.RED:
        offset_y_ind = 0
    else:
        offset_y_ind = 1

    # Going to place the object
    next_place_pose = place_pose.copy_with_offsets(x_offset=offset_x_ind * offset_size,
                                                   y_offset=offset_y_ind * offset_size)
    robot.place_from_pose(next_place_pose)

    # Increment count
    count_dict[color] += 1
    try_without_success = 0

robot.go_to_sleep()
