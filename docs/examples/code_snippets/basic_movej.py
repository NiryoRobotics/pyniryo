from pyniryo import NiryoRobot, JointsPosition

robot = NiryoRobot('<robot_ip_address>')

robot.calibrate_auto()

robot.move(JointsPosition(0.2, -0.3, 0.1, 0.0, 0.5, -0.8))

robot.close_connection()
