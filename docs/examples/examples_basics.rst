Examples: Basics
==========================

In this file, two short programs are implemented & commented in order to
help you understand the philosophy behind the PyNiryo package.

.. danger::
    If you are using the real robot, make sure the environment around it is clear.


Your first move joint
---------------------------

The following example shows a first use case.
It's a simple MoveJ.

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:


Code Details - First Move J
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
First of all, we import the library to be able to access functions.

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:
   :lines: 1

Then, we instantiate the connection and link the variable ``robot`` to the robot
by giving its IP Address.

.. note::
   Don't know what's the robot IP address ? Take a look at :ref:`How to Find your Robot’s IP address <find-ip-address>`

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:
   :lineno-match:
   :lines: 3

Once the connection is done, we calibrate the robot using its
:meth:`~.api.tcp_client.NiryoRobot.calibrate_auto` function.

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:
   :lineno-match:
   :lines: 5

As the robot is now calibrated, we can do a Move Joints by giving the 6 axis positions
in radians! To do so, we use :meth:`~.api.tcp_client.NiryoRobot.move` with a :class:`~.api.objects.JointsPosition` object.

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:
   :lineno-match:
   :lines: 7

Our process is now over, we can close the connection with
:meth:`~.api.tcp_client.NiryoRobot.close_connection`.

.. literalinclude:: code_snippets/basic_movej.py
   :linenos:
   :lineno-match:
   :lines: 9

Your first pick and place
-------------------------------
In the second example, we are going to develop a pick and place algorithm.

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:

Code Details - First Pick And Place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, we import the library and start the connection between our computer
and the robot. We also calibrate the robot.

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:
   :lineno-match:
   :lines: 1-5

Then, we equip the tool
with :meth:`~.api.tcp_client.NiryoRobot.update_tool`.

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:
   :lineno-match:
   :lines: 6

Now that our initialization is done, we can open the gripper (or push air from the vacuum)
with :meth:`~.api.tcp_client.NiryoRobot.release_with_tool`,
go to the picking pose via :meth:`~.api.tcp_client.NiryoRobot.move`
& then catch an object
with :meth:`~.api.tcp_client.NiryoRobot.grasp_with_tool`!

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:
   :lineno-match:
   :lines: 8-10

We now get to the place pose, and place the object.

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:
   :lineno-match:
   :lines: 12-13

Our process is now over, we can close the connection.

.. literalinclude:: code_snippets/basic_pick_and_place.py
   :linenos:
   :lineno-match:
   :lines: 15

Notes
---------
| You may not have fully understood how to move the robot and use
 PyNiryo and that is totally fine because you will find
 more details on the next examples page! 

| The important thing to remember from this page is how to import the library, connect
 to the robot & call functions.
