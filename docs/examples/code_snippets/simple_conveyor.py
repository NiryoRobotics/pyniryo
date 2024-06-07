from pyniryo import NiryoRobot, ConveyorDirection

# Connecting to robot
robot = NiryoRobot('<robot_ip_address>')

# Activating connexion with Conveyor Belt
conveyor_id = robot.set_conveyor()

# Running the Conveyor Belt at 50% of its maximum speed, in forward direction
robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.FORWARD)

# Waiting 3 seconds
robot.wait(3)

# Stopping robot's motor
robot.stop_conveyor(conveyor_id)

# Deactivating connexion with the Conveyor Belt
robot.unset_conveyor(conveyor_id)
