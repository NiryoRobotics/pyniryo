"""
This file shows how to use PyNiryo to do a simple pick and place
with Ned using a conveyor
"""

# Imports
from pyniryo import NiryoRobot, PoseObject, ToolID, PinID, PinState, ConveyorDirection

# -- MUST Change these variables
simulation_mode = True
gripper_used = ToolID.GRIPPER_2  # Tool used for picking
gpio_sensor = PinID.GPIO_1A  # Pin of the sensor
# Set robot address
robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_simulation = "127.0.0.1"
robot_ip_address = robot_ip_address_simulation if simulation_mode else robot_ip_address_rpi

# -- Should Change these variables
# The pick pose
pick_pose = PoseObject(0.25, 0.0, 0.14, 3.14, 0.0, 0.0)

# The Place pose
place_pose = PoseObject(0.01, -0.22, 0.12, 3.14, -0.01, -1.48)


def pick_n_place_w_conveyor(niyro_robot: NiryoRobot):
    # Enable connection with conveyor
    conveyor_id = niyro_robot.set_conveyor()
    # Turn conveyor on
    niyro_robot.control_conveyor(conveyor_id=conveyor_id,
                                 control_on=True,
                                 speed=50,
                                 direction=ConveyorDirection.FORWARD)
    # Wait for sensor to turn to low state which means it has something in front of it
    while niyro_robot.digital_read(gpio_sensor) != PinState.LOW:
        niyro_robot.wait(0.1)
    # Turn conveyor off
    niyro_robot.control_conveyor(conveyor_id=conveyor_id,
                                 control_on=False,
                                 speed=0,
                                 direction=ConveyorDirection.FORWARD)
    # Pick
    niyro_robot.pick(pick_pose)
    # Place
    niyro_robot.place(place_pose)


# -- MAIN PROGRAM

if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Update tool
    robot.update_tool()
    # Launching main process
    pick_n_place_w_conveyor(robot)
    # Releasing connection
    robot.close_connection()
