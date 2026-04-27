Examples: Movement
=========================

This document shows how to control Ned in order to make Move Joints & Move Pose.

If you want to see more, you can look at :ref:`PyNiryo - Joints & Pose<source/api_doc/api:Joints & Pose>`

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
To make a moveJ, you can either provide:

- 6 floats : ``j1, j2, j3, j4, j5, j6``
- a list of 6 floats : ``[j1, j2, j3, j4, j5, j6]``

It is possible to provide these parameters to the function :meth:`~.api.tcp_client.NiryoRobot.move_joints`
or via the ``joints`` setter, at your convenience::

    # Moving Joints with function & 6 floats
    robot.move_joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    # Moving Joints with function & a list of floats
    robot.move_joints([-0.5, -0.6, 0.0, 0.3, 0.0, 0.0])
    
    # Moving Joints with setter & 6 floats
    robot.joints = 0.2, -0.4, 0.0, 0.0, 0.0, 0.0

    # Moving Joints with setter & a list of floats
    robot.joints = [-0.2, 0.3, 0.2, 0.3, -0.6, 0.0]

You should note that these 4 commands are doing exactly the same thing!
In your future scripts, chose the one you prefer, but try to remain consistent to
keep a good readability.

Get Joints
^^^^^^^^^^^^^^^^^^
To get actual joint positions, you can use the function :meth:`~.api.tcp_client.NiryoRobot.get_joints`
or the ``joints`` getter. Both will return a list of the 6 joints position::

    # Getting Joints with function
    joints_read = robot.get_joints()

    # Getting Joints with getter
    joints_read = robot.joints

.. hint::
    As we are developing in Python, we can unpack list very easily, which means that
    we can retrieve joints value in 6 variables by writing ``j1, j2, j3, j4, j5, j6 = robot.get_joints()``.

Pose
-------------------

Move Pose
^^^^^^^^^^^^
To perform a moveP, you can provide:

- 6 floats : x, y, z, roll, pitch, yaw
- a list of 6 floats : [x, y, z, roll, pitch, yaw]
- a |pose_object|

As for MoveJ, it is possible to provide these parameters
to the function :meth:`~.api.tcp_client.NiryoRobot.move_pose`
or the ``pose`` setter, at your convenience::

    pose_target = [0.2, 0.0, 0.2, 0.0, 0.0, 0.0]
    pose_target_obj = PoseObject(0.2, 0.0, 0.2, 0.0, 0.0, 0.0)

    # Moving Pose with function
    robot.move_pose(0.2, 0.0, 0.2, 0.0, 0.0, 0.0)
    robot.move_pose(pose_target)
    robot.move_pose(pose_target_obj)

    # Moving Pose with setter
    robot.pose = (0.2, 0.0, 0.2, 0.0, 0.0, 0.0)
    robot.pose = pose_target
    robot.pose = pose_target_obj

Each of these 6 commands are doing the same thing.

Get Pose
^^^^^^^^^^^^
To get end effector actual pose, you can use
the function :meth:`~.api.tcp_client.NiryoRobot.get_pose`
or the ``pose`` getter. Both will return a |pose_object|: ::

    # Getting Joints with function
    pose_read = robot.get_pose()

    # Getting Joints with getter
    pose_read = robot.pose


How to use the PoseObject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The |pose_object| is a Python object which allows to store all poses' 6 coordinates (x, y, z,
roll, pitch, yaw) in one single instance.
It can be converted into a list if needed with the method
:meth:`~.api.objects.PoseObject.to_list`.

It also allows to create new |pose_object| with some offset, much easier than
copying list and editing only 1 or 2 values.
For instance, imagine that we want to shift the place pose by 5 centimeters at each iteration of a loop,
you can use the :meth:`~.api.objects.PoseObject.copy_with_offsets` method::

    pick_pose = PoseObject(
    x=0.30, y=0.0, z=0.15,
    roll=0, pitch=1.57, yaw=0.0
    )
    first_place_pose = PoseObject(
        x=0.0, y=0.2, z=0.15,
        roll=0, pitch=1.57, yaw=0.0
    )
    for i in range(5):
        robot.move_pose(pick_pose)
        new_place_pose = first_place_pose.copy_with_offsets(x_offset=0.05 * i)
        robot.move_pose(new_place_pose)



.. |pose_object| replace:: :class:`~.api.objects.PoseObject`
