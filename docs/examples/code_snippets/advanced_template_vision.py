from pyniryo import NiryoRobot, PoseObject, ObjectShape, ObjectColor

local_mode = False  # Or True
workspace_name = "workspace_1"  # Robot's Workspace Name
# Set robot address
robot_ip_address = '<robot_ip_address>'
robot_ip_address_local = "127.0.0.1"

robot_ip_address = robot_ip_address_local if local_mode else robot_ip_address

# The pose from where the image processing happens
observation_pose = PoseObject(0.18, 0.0, 0.34, 0.0, 1.56, 0.0)

# Center of the conditioning area
place_pose = PoseObject(0.0, -0.23, 0.13, 0.0, 1.56, -1.56)


def process(robot: NiryoRobot):
    robot.move(observation_pose)
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

        ...

        robot.place(place_pose)


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Equip tool
    robot.update_tool()
    # Launching main process
    process(robot)
    # Ending
    robot.go_to_sleep()
    # Releasing connection
    robot.close_connection()
