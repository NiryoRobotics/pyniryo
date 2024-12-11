Verify your Setup and Get Started
===========================================

In order to verify your computer's setup, we are going to run a program
from it, and see if the robot answers as expected.

.. note:: Before verifying your setup, be sure that your
    physical robot (or simulation) is turned on

Firstly, go in the folder of your choice and
create an empty file named "pyniryo_test.py". This file
will contain the checking code

Edit this file and fill it with the following code ::

    from pyniryo import *

    robot_ip_address = "10.10.10.10"

    # Connect to robot & calibrate
    robot = NiryoRobot(robot_ip_address)
    robot.calibrate_auto()
    # Move joints
    robot.move_joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    # Turn learning mode ON
    robot.set_learning_mode(True)
    # Stop TCP connection
    robot.close_connection()

.. attention::
    Replace the third line with your :doc:`Robot IP Address <ip_address>`
    if you are not using Hotspot Mode

Still on your computer, open a terminal, and place your current directory in the same folder
than your file. Then, run the command : ::

    python pyniryo_test.py

.. note::
    If you are using Python 3, you may need to change ``python`` to ``python3``

If you robot start calibrating, then move, and finally, go to learning mode,
your setup is validated, you can now start coding !

