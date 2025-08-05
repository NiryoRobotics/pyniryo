# Imports
from pyniryo import NiryoRobot, ToolID, PoseObject

robot_ip_address = '<robot_ip_address>'  # Robot address

# The pick pose
pick_pose = PoseObject(0.25, 0.0, 0.15, 0.0, 1.560, 0.0)
# The Place pose
place_pose = PoseObject(0.03, -0.25, 0.1, 0.0, 1.56, -1.56)


def pick_n_place(robot):
    ...


if __name__ == '__main__':
    # Connect to robot
    client = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    client.calibrate_auto()
    # Changing tool
    client.update_tool()

    pick_n_place(client)

    # Releasing connection
    client.close_connection()
