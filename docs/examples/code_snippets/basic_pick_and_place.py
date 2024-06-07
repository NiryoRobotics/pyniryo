from pyniryo import NiryoRobot, PoseObject

robot = NiryoRobot('<robot_ip_address>')

robot.calibrate_auto()
robot.update_tool()

robot.release_with_tool()
robot.move(PoseObject(0.19, -0.12, 0.24, -3.14, 0.01, -0.1))
robot.grasp_with_tool()

robot.move(PoseObject(0.2, 0.09, 0.25, -3.14, -0.0, -0.03))
robot.release_with_tool()

robot.close_connection()
