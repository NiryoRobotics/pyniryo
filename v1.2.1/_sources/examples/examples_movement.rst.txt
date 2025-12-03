Examples: Movement
=========================

This document shows how to control Ned in order to make Move Joints & Move Pose.

If you want to see more, you can look at :py:meth:`joints and poses functions<pyniryo.api.tcp_client.NiryoRobot.get_joints>`

.. important::
    In the following sections, you are supposed to be already connected to a calibrated robot.
    The robot's instance is saved in the variable ``robot``. To know how to do so, go
    look at section :doc:`examples_basics`.

.. danger::
    If you are using the real robot, make sure the environment around it is clear.

Joints
-------------------

Move Joints
^^^^^^^^^^^^^^^^^^

Joints positions are represented by the object :class:`~.api.objects.JointsPosition`.
It can take any number of joints values, but you'll have to give it 6 values in order to work with a Ned2.
The JointsPosition is an iterable object, which means you can operate with it as if it was a list, for example

To do a move joints, you can either use the :meth:`~.api.tcp_client.NiryoRobot.move` function or give a
:class:`~.api.objects.JointsPosition` to the :meth:`~.api.tcp_client.NiryoRobot.joints` setter, at your convenience

.. code-block:: python
  :linenos:

   JointsPosition(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

   # with the move function:
   robot.move(JointsPosition(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

   #with setter
   robot.joints = JointsPosition(-0.2, 0.3, 0.2, 0.3, -0.6, 0.0)

You should note that these 2 commands are doing exactly the same thing!
In your future scripts, chose the one you prefer, but try to remain consistent to
keep a good readability.

Get Joints
^^^^^^^^^^^^^^^^^^
To get actual joint positions, you can use the function :meth:`~.api.tcp_client.NiryoRobot.get_joints`
or the :meth:`~.api.tcp_client.NiryoRobot.joints` getter. Both will return a :class:`~.api.objects.JointsPosition` object

.. code-block:: python
  :linenos:

   # with function
   joints_read = robot.get_joints()

   # with getter
   joints_read = robot.joints

Pose
-------------------

Move Pose
^^^^^^^^^^^^
To perform a moveP, you have to use the :class:`~.api.objects.PoseObject` object:

As for MoveJ, it is possible to use the :meth:`~.api.tcp_client.NiryoRobot.move` or the ``pose`` setter,
at your convenience

.. code-block::
  :linenos:

  pose_target = PoseObject(0.2, 0.0, 0.2, 0.0, 0.0, 0.0)

  # Moving Pose with function
  robot.move(pose_target)

  # Moving Pose with setter
  robot.pose = pose_target

Get Pose
^^^^^^^^^^^^
To get the end effector actual pose, you can use
the function :meth:`~.api.tcp_client.NiryoRobot.get_pose`
or the ``pose`` getter. Both will return a |pose_object|:

.. code-block::
  :linenos:

    # Getting Joints with function
    pose_read = robot.get_pose()

    # Getting Joints with getter
    pose_read = robot.pose

.. _howto-poseobject:

How to use the PoseObject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The |pose_object| is a Python object which allows to store all poses' 6 coordinates (x, y, z,
roll, pitch, yaw) in one single instance.
It can be converted into a list if needed with the method
:meth:`~.api.objects.PoseObject.to_list`.

It also allows to create new |pose_object| with some offset, much easier than
copying list and editing only 1 or 2 values.
For instance, imagine that we want to shift the place pose by 5 centimeters at each iteration of a loop,
you can use the :meth:`~.api.objects.PoseObject.copy_with_offsets` method

.. code-block::
  :linenos:

    pick_pose = PoseObject(x=0.30, y=0.0, z=0.15, roll=0, pitch=1.57, yaw=0.0)
    first_place_pose = PoseObject(x=0.0, y=0.2, z=0.15, roll=0, pitch=1.57, yaw=0.0)
    for i in range(5):
        robot.move(pick_pose)
        new_place_pose = first_place_pose.copy_with_offsets(x_offset=0.05 * i)
        robot.move(new_place_pose)



.. |pose_object| replace:: :class:`~.api.objects.PoseObject`
