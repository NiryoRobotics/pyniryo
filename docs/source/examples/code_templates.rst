Code templates
==============

As code structures are always the same, we wrote down few templates for you
to start your code file with a good form

The short template
-------------------

Very simple, straightforward ::

    from pyniryo import *

    # Connect to robot & calibrate
    robot = NiryoRobot(<robot_ip_address>)
    robot.calibrate_auto()

    # --- --------- --- #
    # --- YOUR CODE --- #
    # --- --------- --- #

    # Releasing connection
    robot.close_connection()


Advanced template
-------------------

This template let the user define his own process but it handles connection,
calibration, tool equipping, and makes the robot go to sleep at the end ::

    from pyniryo import *

    local_mode = False # Or True
    tool_used = ToolID.GRIPPER_1
    # Set robot address
    robot_ip_address_rpi = "x.x.x.x"
    robot_ip_address_local = "127.0.0.1"

    robot_ip_address = robot_ip_address_local if local_mode else robot_ip_address_rpi


    def process(niryo_edu):
        # --- --------- --- #
        # --- YOUR CODE --- #
        # --- --------- --- #

    if __name__ == '__main__':
        # Connect to robot
        robot = NiryoRobot(robot_ip_address)
        # Calibrate robot if robot needs calibration
        robot.calibrate_auto()
        # Equip tool
        robot.update_tool()
        # Launching main process
        process(client)
        # Ending
        robot.go_to_sleep()
        # Releasing connection
        robot.close_connection()

Advanced template for Conveyor Bely
--------------------------------------

Same as :ref:`Advanced template` but with a Conveyor Belt ::

    from pyniryo import *

    # Set robot address
    robot_ip_address = "x.x.x.x"


    def process(robot, conveyor_id):
        robot.run_conveyor(conveyor_id)

        # --- --------- --- #
        # --- YOUR CODE --- #
        # --- --------- --- #

        robot.stop_conveyor()


    if __name__ == '__main__':
        # Connect to robot
        robot = NiryoRobot(robot_ip_address)
        # Calibrate robot if robot needs calibration
        robot.calibrate_auto()
        # Equip tool
        robot.update_tool()
        # Activating connexion with conveyor
        conveyor_id = robot.set_conveyor()
        # Launching main process
        process(robot, conveyor_id)
        # Ending
        robot.go_to_sleep()
        # Deactivating connexion with conveyor
        robot.unset_conveyor(conveyor_id)
        # Releasing connection
        robot.close_connection()

Advanced template for Vision
--------------------------------------

Huge template for Vision users! ::

    from pyniryo import *

    local_mode = False # Or True
    workspace_name = "workspace_1"  # Robot's Workspace Name
    # Set robot address
    robot_ip_address_rpi = "x.x.x.x"
    robot_ip_address_local = "127.0.0.1"

    robot_ip_address = robot_ip_address_local if local_mode else robot_ip_address_rpi

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

    def process(robot):
        robot.move_pose(observation_pose)
        catch_count = 0
        while catch_count < 3:
            ret = robot.get_target_pose_from_cam(workspace_name,
                                                height_offset=0.0,
                                                shape=ObjectShape.ANY,
                                                color=ObjectColor.ANY)
            obj_found, obj_pose, shape, color = ret
            if not obj_found:
                continue
            catch_count += 1
            # --- --------- --- #
            # --- YOUR CODE --- #
            # --- --------- --- #
            robot.place_from_pose(place_pose)

    if __name__ == '__main__':
        # Connect to robot
        robot = NiryoRobot(robot_ip_address)
        # Calibrate robot if robot needs calibration
        robot.calibrate_auto()
        # Equip tool
        robot.update_tool()
        # Launching main process
        process(client)
        # Ending
        robot.go_to_sleep()
        # Releasing connection
        robot.close_connection()

