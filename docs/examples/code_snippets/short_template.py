from pyniryo import NiryoRobot

# Connect to robot & calibrate
robot = NiryoRobot('<robot_ip_address>')
robot.calibrate_auto()

...

# Releasing connection
robot.close_connection()
