from vision_header import robot, observation_pose, workspace_name, place_pose

robot.move(observation_pose)
# Trying to pick target using camera
obj_found, shape_ret, color_ret = robot.vision_pick(workspace_name)
if obj_found:
    robot.place_from_pose(place_pose)

robot.set_learning_mode(True)
