Examples: Conveyor
========================

This document shows how to use Ned's conveyor belt

If you want see more about Ned's conveyor belt functions, you can look at :ref:`PyNiryo - Conveyor<Conveyor>`

.. danger::
    If you are using the real robot, make sure the environment around it is clear

Simple Conveyor control
-------------------------------
This short example show how to connect a conveyor and
launch its motor (control it by setting its speed and direction) : ::

    from pyniryo import *

    # Connecting to robot
    robot = NiryoRobot(<robot_ip_address>)

    # Activating connexion with conveyor
    conveyor_id = robot.set_conveyor()

    # Running conveyor at 50% of its maximum speed, in Forward direction
    robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.FORWARD)

    # Waiting 3 seconds
    robot.wait(3)

    # Stopping robot motor
    robot.stop_conveyor(conveyor_id)

    # Deactivating connexion with conveyor
    robot.unset_conveyor(conveyor_id)

Advanced Conveyor control
-------------------------------
This example shows how to do a certain amount of pick & place by using
the conveyor with the infrared sensor ::

    from pyniryo import *

    # -- Setting variables
    sensor_pin_id = PinID.GPIO_1A

    catch_nb = 5

    # The pick pose
    pick_pose = PoseObject(
        x=0.25, y=0., z=0.15,
        roll=-0., pitch=1.57, yaw=0.0,
    )
    # The Place pose
    place_pose = PoseObject(
        x=0., y=-0.25, z=0.1,
        roll=0., pitch=1.57, yaw=-1.57)

    # -- MAIN PROGRAM

    # Connecting to robot
    robot = NiryoRobot(<robot_ip_address>)

    # Activating connexion with conveyor
    conveyor_id = robot.set_conveyor()

    for i in range(catch_nb):
        robot.run_conveyor(conveyor_id)
        while robot.digital_read(sensor_pin_id) == PinState.LOW:
            robot.wait(0.1)

        # Stopping robot motor
        robot.stop_conveyor(conveyor_id)
        # Making a pick & place
        robot.pick_and_place(pick_pose, place_pose)

    # Deactivating connexion with conveyor
    robot.unset_conveyor(conveyor_id)

