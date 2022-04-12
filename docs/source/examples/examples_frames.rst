Examples : Dynamic frames
============================

This document shows how to use dynamic frames.

If you want to see more about dynamic frames functions, you can look at :ref:`PyNiryo - Frames<source/api_doc/api:Dynamic frames>`

.. danger::
    If you are using the real robot, make sure the environment around it is clear.

Simple dynamic frame control
-------------------------------
This example shows how to create a frame and do a small pick and place in this frame: ::

    from pyniryo import *

    robot_ip_address = "192.168.1.91"
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
        initial_pose = PoseObject(0, 0, 0, 0, 1.57, 0)	
        robot.move_pose(initial_pose, "dynamic_frame")
        robot.close_gripper(gripper_speed)

        # Move in frame
        robot.move_linear_relative("dynamic_frame", [0, 0, 0.1, 0, 0, 0])
        robot.move_relative("dynamic_frame", [0.1, 0, 0, 0, 0, 0])
        robot.move_linear_relative("dynamic_frame", [0, 0, -0.1, 0, 0, 0])

        # Place
        robot.open_gripper(gripper_speed)
        robot.move_linear_relative("dynamic_frame", [0, 0, 0.1, 0, 0, 0])

        # Home
        robot.move_joints(0, 0.5, -1.25, 0, 0, 0)

        # Delete frame
        robot.delete_dynamic_frame("dynamic_frame")