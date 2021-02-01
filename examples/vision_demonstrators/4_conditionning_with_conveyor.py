from pyniryo import *

# -- MUST Change these variables
robot_ip_address = "192.168.1.200"
workspace_name = "wks_conveyor"

# -- Can change these variables
grid_dimension = (3, 3)
conveyor_id = ConveyorID.ID_1

# -- Should Change these variables
observation_pose = PoseObject(
    x=0.20, y=0., z=0.3,
    roll=0.0, pitch=1.57, yaw=0.0,
)

center_conditioning_pose = PoseObject(
    x=0.0, y=0.25, z=0.13,
    roll=0.0, pitch=1.57, yaw=1.57,
)


def process(niryo_robot):
    max_catch_count = 6
    shape_expected = ObjectShape.CIRCLE
    color_expected = ObjectColor.RED

    catch_count = 0
    while catch_count < max_catch_count:
        # Turning conveyor on
        niryo_robot.run_conveyor(conveyor_id)
        # Moving to observation pose
        niryo_robot.move_pose(observation_pose)
        # Check if object is in the workspace
        obj_found, pos_array, shape, color = niryo_robot.detect_object(workspace_name,
                                                                       shape=shape_expected,
                                                                       color=color_expected)
        if not obj_found:
            niryo_robot.wait(0.5)  # Wait to let the conveyor turn a bit
            continue
        # Stopping conveyor
        niryo_robot.stop_conveyor(conveyor_id)
        # Making a vision pick
        obj_found, shape, colo = niryo_robot.vision_pick(workspace_name,
                                                         shape=shape_expected,
                                                         color=color_expected)
        if not obj_found:  # If visual pick did not work
            continue
        # Calculating offset relative to conditioning center position
        offset_x = catch_count % grid_dimension[0] - grid_dimension[0] // 2
        offset_y = (catch_count // grid_dimension[1]) % 3 - grid_dimension[1] // 2
        place_pose = center_conditioning_pose.copy_with_offsets(0.05 * offset_x, 0.05 * offset_y)
        # Going to place
        niryo_robot.place_from_pose(place_pose)
        catch_count += 1
    # Stopping conveyor
    niryo_robot.stop_conveyor(conveyor_id)

    # Going to initial Observation pose
    niryo_robot.move_pose(observation_pose)


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Changing tool
    robot.update_tool()
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Launching main process
    process(robot)
    # Ending
    robot.go_to_sleep()
    # Releasing connection
    robot.close_connection()
