from pyniryo import NiryoRobot, ToolID

local_mode = False  # Or True
tool_used = ToolID.GRIPPER_1
# Set robot address
robot_ip_address = '<robot_ip_address>'
robot_ip_address_local = "127.0.0.1"

robot_ip_address = robot_ip_address_local if local_mode else robot_ip_address


def process(robot):
    ...


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
