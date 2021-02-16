PyNiryo API Documentation
=====================================

This file presents the different :ref:`Command Functions`,
:ref:`Enums` & :ref:`Python Objects <Python Object classes>` available with the API

* :ref:`Command Functions` are used to deal directly with the robot.
  It could be :meth:`~.api.tcp_client.NiryoRobot.move_joints`,
  :meth:`~.api.tcp_client.NiryoRobot.get_hardware_status`
  :meth:`~.api.tcp_client.NiryoRobot.vision_pick`, or also
  :meth:`~.api.tcp_client.NiryoRobot.run_conveyor`
* :ref:`Enums` are used to pass specific arguments to functions. For instance
  :class:`~.api.enums_communication.PinState`,
  :class:`~.api.enums_communication.ConveyorDirection`, ...
* :ref:`Python Objects <Python Object classes>`, as |pose_object|, ease some operations

Command Functions
------------------------------------
.. automodule:: api.tcp_client
   :members:

This section references all existing functions to control your robot, which includes

- Moving the robot
- Using Vision
- Controlling Conveyor Belts
- Playing with Hardware

All functions to control the robot are accessible via an instance of
the class :class:`~.api.enums_communication.NiryoRobot` ::

    robot = NiryoRobot(<robot_ip_address>)

See examples on :ref:`Examples Section <Examples: Basics>`

List of functions subsections:

.. contents::
   :local:
   :depth: 1

TCP Connection
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: connect, close_connection

Main purpose functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: calibrate, calibrate_auto, need_calibration, get_learning_mode, set_learning_mode,
              set_arm_max_velocity, set_jog_control, wait
    :member-order: bysource

Joints & Pose
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: get_joints, get_pose, get_pose_quat, move_joints, move_pose,
              shift_pose, jog_joints, jog_pose,
              move_linear_pose, move_to_home_pose, go_to_sleep,
              forward_kinematics, inverse_kinematics
    :member-order: bysource

Saved Poses
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: get_pose_saved, save_pose, delete_pose, get_saved_pose_list
    :member-order: bysource

Pick & Place
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: pick_from_pose, place_from_pose, pick_and_place
    :member-order: bysource

Trajectories
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: get_trajectory_saved, execute_trajectory_from_poses, execute_trajectory_saved,
              save_trajectory, delete_trajectory, get_saved_trajectory_list
    :member-order: bysource

Tools
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: get_current_tool_id, update_tool, grasp_with_tool,release_with_tool,
              open_gripper, close_gripper, pull_air_vacuum_pump, push_air_vacuum_pump,
              setup_electromagnet, activate_electromagnet, deactivate_electromagnet
    :member-order: bysource

Hardware
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: set_pin_mode, digital_write, digital_read,
              get_hardware_status, get_digital_io_state
    :member-order: bysource

Conveyor
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: set_conveyor, unset_conveyor, run_conveyor,
              stop_conveyor, control_conveyor, get_connected_conveyors_id
    :member-order: bysource

Vision
^^^^^^^^^^^^^

.. autoclass:: NiryoRobot
    :members: get_img_compressed, get_target_pose_from_rel, get_target_pose_from_cam,
              vision_pick, move_to_object, detect_object, get_camera_intrinsics,
              save_workspace_from_robot_poses, save_workspace_from_points,
              delete_workspace, get_workspace_ratio, get_workspace_list
    :member-order: bysource


Enums
------------------------------------

Enums are used to pass specific parameters to functions.

For instance, :meth:`~.api.tcp_client.NiryoRobot.change_tool`
will need a parameter from
:class:`~.api.objects.ToolID` enum ::

    robot.change_tool(ToolID.GRIPPER_1)

List of enums:

* :class:`~.api.objects.CalibrateMode`
* :class:`~.api.objects.RobotAxis`
* :class:`~.api.objects.ToolID`
* :class:`~.api.objects.PinMode`
* :class:`~.api.objects.PinState`
* :class:`~.api.objects.PinID`
* :class:`~.api.objects.ConveyorID`
* :class:`~.api.objects.ConveyorDirection`
* :class:`~.api.objects.ObjectColor`
* :class:`~.api.objects.ObjectShape`

.. automodule:: api.enums_communication
    :members:
    :undoc-members:
    :exclude-members: Command
    :member-order: bysource

.. undoc-members -> allow to see members of enums
.. show-inheritance -> display enum.Enum

Python object classes
------------------------------------

Special objects :D

.. automodule:: api.objects
    :members:
    :no-undoc-members:
    :member-order: bysource


.. |pose_object| replace:: :class:`~.api.objects.PoseObject`
