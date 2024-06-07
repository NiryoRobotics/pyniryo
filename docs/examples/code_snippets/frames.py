from pyniryo import NiryoRobot, PoseObject, JointsPosition

robot_ip_address = '<robot_ip_address>'
gripper_speed = 400

if __name__ == '__main__':
    robot = NiryoRobot(robot_ip_address)

    # Create frame
    point_o = [0.15, 0.15, 0]
    point_x = [0.25, 0.2, 0]
    point_y = [0.2, 0.25, 0]

    robot.save_dynamic_frame_from_points("dynamic_frame", "description", point_o, point_x, point_y)

    # Get list of frames
    print(robot.get_saved_dynamic_frame_list())
    # Check creation of the frame
    info = robot.get_saved_dynamic_frame("dynamic_frame")
    print(info)

    # Pick
    robot.open_gripper(gripper_speed)
    # Move to the frame
    initial_pose = PoseObject(0, 0, 0, 3.14, 0.01, -0.2)
    initial_pose.metadata.frame = "dynamic_frame"
    robot.move(initial_pose)
    robot.close_gripper(gripper_speed)

    # Move in frame
    robot.move_relative([0, 0, 0.1, 0, 0, 0], "dynamic_frame", linear=True)
    robot.move_relative([0.1, 0, 0, 0, 0, 0], "dynamic_frame")
    robot.move_relative([0, 0, -0.1, 0, 0, 0], "dynamic_frame", linear=True)

    # Place
    robot.open_gripper(gripper_speed)
    robot.move_relative([0, 0, 0.1, 0, 0, 0], "dynamic_frame", linear=True)

    # Home
    robot.move(JointsPosition(0, 0.5, -1.25, 0, 0, 0))

    # Delete frame
    robot.delete_dynamic_frame("dynamic_frame")
