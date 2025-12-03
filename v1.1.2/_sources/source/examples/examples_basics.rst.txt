Examples: Basics
==========================

In this file, two short programs are implemented & commented in order to
help you understand the philosophy behind the PyNiryo package.

.. danger::
    If you are using the real robot, make sure the environment around it is clear.


Your first move joint
---------------------------

The following example shows a first use case.
It's a simple MoveJ. ::

    from pyniryo import *

    robot = NiryoRobot("10.10.10.10")

    robot.calibrate_auto()

    robot.move_joints(0.2, -0.3, 0.1, 0.0, 0.5, -0.8)

    robot.close_connection()

Code Details - First Move J
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
First of all, we import the library to be able to access functions. ::

    from pyniryo import *

Then, we instantiate the connection and link the variable ``robot`` to the robot
at the IP Address ``10.10.10.10``.  ::

    robot = NiryoRobot("10.10.10.10")

Once the connection is done, we calibrate the robot using its
:meth:`~.api.tcp_client.NiryoRobot.calibrate_auto` function. ::

    robot.calibrate_auto()

As the robot is now calibrated, we can do a Move Joints by giving the 6 axis positions
in radians! To do so, we use :meth:`~.api.tcp_client.NiryoRobot.move_joints`. ::

    robot.move_joints(0.2, -0.3, 0.1, 0.0, 0.5, -0.8)

Our process is now over, we can close the connection with
:meth:`~.api.tcp_client.NiryoRobot.quit`. ::

    robot.close_connection()


Your first pick and place
-------------------------------
In the second example, we are going to develop a pick and place algorithm. ::

    from pyniryo import *

    robot = NiryoRobot("10.10.10.10")

    robot.calibrate_auto()
    robot.update_tool()

    robot.release_with_tool()
    robot.move_pose(0.2, -0.1, 0.25, 0.0, 1.57, 0.0)
    robot.grasp_with_tool()

    robot.move_pose(0.2, 0.1, 0.25, 0.0, 1.57, 0.0)
    robot.release_with_tool()

    robot.close_connection()

Code Details - First Pick And Place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, we import the library and start the connection between our computer
and the robot. We also calibrate the robot. ::

    from pyniryo import *

    robot = NiryoRobot("10.10.10.10")
    robot.calibrate_auto()

Then, we equip the tool
with :meth:`~.api.tcp_client.NiryoRobot.update_tool`. ::

    robot.update_tool()

Now that our initialization is done, we can open the gripper (or push air from the vacuum)
with :meth:`~.api.tcp_client.NiryoRobot.release_with_tool`,
go to the picking pose via :meth:`~.api.tcp_client.NiryoRobot.move_pose`
& then catch an object
with :meth:`~.api.tcp_client.NiryoRobot.grasp_with_tool`! ::

    robot.release_with_tool()
    robot.move_pose(0.2, -0.1, 0.25, 0.0, 1.57, 0.0)
    robot.grasp_with_tool()

We now get to the place pose, and place the object. ::

    robot.move_pose(0.2, 0.1, 0.25, 0.0, 1.57, 0.0)
    robot.release_with_tool()

Our process is now over, we can close the connection. ::

    robot.close_connection()


Notes
---------
| You may not have fully understood how to move the robot and use
 PyNiryo and that is totally fine because you will find
 more details on the next examples page! 

| The important thing to remember from this page is how to import the library, connect
 to the robot & call functions.
