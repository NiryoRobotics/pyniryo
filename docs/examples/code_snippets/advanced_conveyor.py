from pyniryo import NiryoRobot, PoseObject, PinID, PinState

# -- Setting variables
sensor_pin_id = PinID.GPIO_1A

catch_nb = 5

# The pick pose
pick_pose = PoseObject(0.25, -0.01, 0.15, 0.0, 1.56, 0.0)
# The Place pose
place_pose = PoseObject(0.02, -0.25, 0.1, 0.0, 1.56, -1.56)

# -- MAIN PROGRAM

# Connecting to the robot
robot = NiryoRobot('<robot_ip_address>')

# Activating connexion with the Conveyor Belt
conveyor_id = robot.set_conveyor()

for i in range(catch_nb):
    robot.run_conveyor(conveyor_id)
    while robot.digital_read(sensor_pin_id) == PinState.LOW:
        robot.wait(0.1)

    # Stopping robot's motor
    robot.stop_conveyor(conveyor_id)
    # Making a pick & place
    robot.pick_and_place(pick_pose, place_pose)

# Deactivating connexion with the Conveyor Belt
robot.unset_conveyor(conveyor_id)
