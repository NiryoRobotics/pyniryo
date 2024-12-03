from pyniryo import NiryoRobot

# Set robot address
robot_ip_address = '<robot_ip_address>'


def process(robot, conveyor_id):
    robot.run_conveyor(conveyor_id)

    ...

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
