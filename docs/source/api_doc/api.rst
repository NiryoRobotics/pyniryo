PyNiryo API Documentation
=====================================

This file presents the different :ref:`source/api_doc/api:Command Functions`,
:ref:`source/api_doc/api:Enums` & :ref:`source/api_doc/api:Python Object classes` available with the API

* :ref:`source/api_doc/api:Command Functions` are used to deal directly with the robot.
  It could be :meth:`~.api.tcp_client.NiryoRobot.move_joints`,
  :meth:`~.api.tcp_client.NiryoRobot.get_hardware_status`
  :meth:`~.api.tcp_client.NiryoRobot.vision_pick`, or also
  :meth:`~.api.tcp_client.NiryoRobot.run_conveyor`
* :ref:`source/api_doc/api:Enums` are used to pass specific arguments to functions. For instance
  :class:`~.api.enums_communication.PinState`,
  :class:`~.api.enums_communication.ConveyorDirection`, ...
* :ref:`source/api_doc/api:Python Object classes`, as |pose_object|, ease some operations

Command functions
------------------------------------

This section references all existing functions to control your robot, which includes

- Moving the robot
- Using Vision
- Controlling Conveyor Belts
- Playing with Hardware

All functions to control the robot are accessible via an instance of
the class :class:`~.api.enums_communication.NiryoRobot` ::

    robot = NiryoRobot(<robot_ip_address>)

See examples on :ref:`source/examples/examples_basics:Examples: Basics`

List of functions subsections:

.. contents::
   :local:
   :depth: 1

.. py:currentmodule:: api.tcp_client

TCP Connection
^^^^^^^^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.connect
.. automethod:: api.tcp_client.NiryoRobot.close_connection

Main purpose functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.calibrate
.. automethod:: api.tcp_client.NiryoRobot.calibrate_auto
.. automethod:: api.tcp_client.NiryoRobot.need_calibration
.. automethod:: api.tcp_client.NiryoRobot.get_learning_mode
.. automethod:: api.tcp_client.NiryoRobot.set_learning_mode
.. automethod:: api.tcp_client.NiryoRobot.set_arm_max_velocity
.. automethod:: api.tcp_client.NiryoRobot.set_jog_control
.. automethod:: api.tcp_client.NiryoRobot.wait

Joints & Pose
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.get_joints
.. automethod:: api.tcp_client.NiryoRobot.get_pose
.. automethod:: api.tcp_client.NiryoRobot.get_pose_quat
.. automethod:: api.tcp_client.NiryoRobot.move_joints
.. automethod:: api.tcp_client.NiryoRobot.move_pose
.. automethod:: api.tcp_client.NiryoRobot.move_linear_pose
.. automethod:: api.tcp_client.NiryoRobot.shift_pose
.. automethod:: api.tcp_client.NiryoRobot.shift_linear_pose
.. automethod:: api.tcp_client.NiryoRobot.jog_joints
.. automethod:: api.tcp_client.NiryoRobot.jog_pose
.. automethod:: api.tcp_client.NiryoRobot.move_to_home_pose
.. automethod:: api.tcp_client.NiryoRobot.go_to_sleep
.. automethod:: api.tcp_client.NiryoRobot.forward_kinematics
.. automethod:: api.tcp_client.NiryoRobot.inverse_kinematics

Saved Poses
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.get_pose_saved
.. automethod:: api.tcp_client.NiryoRobot.save_pose
.. automethod:: api.tcp_client.NiryoRobot.delete_pose
.. automethod:: api.tcp_client.NiryoRobot.get_saved_pose_list

Pick & Place
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.pick_from_pose
.. automethod:: api.tcp_client.NiryoRobot.place_from_pose
.. automethod:: api.tcp_client.NiryoRobot.pick_and_place

Trajectories
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.get_trajectory_saved
.. automethod:: api.tcp_client.NiryoRobot.execute_trajectory_from_poses
.. automethod:: api.tcp_client.NiryoRobot.execute_trajectory_saved
.. automethod:: api.tcp_client.NiryoRobot.save_trajectory
.. automethod:: api.tcp_client.NiryoRobot.delete_trajectory
.. automethod:: api.tcp_client.NiryoRobot.get_saved_trajectory_list

Tools
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.get_current_tool_id
.. automethod:: api.tcp_client.NiryoRobot.update_tool
.. automethod:: api.tcp_client.NiryoRobot.grasp_with_tool
.. automethod:: api.tcp_client.NiryoRobot.release_with_tool
.. automethod:: api.tcp_client.NiryoRobot.open_gripper
.. automethod:: api.tcp_client.NiryoRobot.close_gripper
.. automethod:: api.tcp_client.NiryoRobot.pull_air_vacuum_pump
.. automethod:: api.tcp_client.NiryoRobot.push_air_vacuum_pump
.. automethod:: api.tcp_client.NiryoRobot.setup_electromagnet
.. automethod:: api.tcp_client.NiryoRobot.activate_electromagnet
.. automethod:: api.tcp_client.NiryoRobot.deactivate_electromagnet
.. automethod:: api.tcp_client.NiryoRobot.enable_tcp
.. automethod:: api.tcp_client.NiryoRobot.set_tcp
.. automethod:: api.tcp_client.NiryoRobot.reset_tcp
.. automethod:: api.tcp_client.NiryoRobot.tool_reboot

Hardware
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.set_pin_mode
.. automethod:: api.tcp_client.NiryoRobot.digital_write
.. automethod:: api.tcp_client.NiryoRobot.digital_read
.. automethod:: api.tcp_client.NiryoRobot.get_hardware_status
.. automethod:: api.tcp_client.NiryoRobot.get_digital_io_state

Conveyor
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.set_conveyor
.. automethod:: api.tcp_client.NiryoRobot.unset_conveyor
.. automethod:: api.tcp_client.NiryoRobot.run_conveyor
.. automethod:: api.tcp_client.NiryoRobot.stop_conveyor
.. automethod:: api.tcp_client.NiryoRobot.control_conveyor
.. automethod:: api.tcp_client.NiryoRobot.get_connected_conveyors_id

Vision
^^^^^^^^^^^^^

.. automethod:: api.tcp_client.NiryoRobot.get_img_compressed
.. automethod:: api.tcp_client.NiryoRobot.set_brightness
.. automethod:: api.tcp_client.NiryoRobot.set_contrast
.. automethod:: api.tcp_client.NiryoRobot.set_saturation
.. automethod:: api.tcp_client.NiryoRobot.get_image_parameters
.. automethod:: api.tcp_client.NiryoRobot.get_target_pose_from_rel
.. automethod:: api.tcp_client.NiryoRobot.get_target_pose_from_cam
.. automethod:: api.tcp_client.NiryoRobot.vision_pick
.. automethod:: api.tcp_client.NiryoRobot.move_to_object
.. automethod:: api.tcp_client.NiryoRobot.detect_object
.. automethod:: api.tcp_client.NiryoRobot.get_camera_intrinsics
.. automethod:: api.tcp_client.NiryoRobot.save_workspace_from_robot_poses
.. automethod:: api.tcp_client.NiryoRobot.save_workspace_from_points
.. automethod:: api.tcp_client.NiryoRobot.delete_workspace
.. automethod:: api.tcp_client.NiryoRobot.get_workspace_ratio
.. automethod:: api.tcp_client.NiryoRobot.get_workspace_list

Enums
------------------------------------

Enums are used to pass specific parameters to functions.

For instance, :meth:`~.api.tcp_client.NiryoRobot.shift_pose`
will need a parameter from
:class:`~.api.objects.RobotAxis` enum ::

    robot.shift_pose(RobotAxis.Y, 0.15)

List of enums:

* :class:`~.api.enums_communication.CalibrateMode`
* :class:`~.api.enums_communication.RobotAxis`
* :class:`~.api.enums_communication.ToolID`
* :class:`~.api.enums_communication.PinMode`
* :class:`~.api.enums_communication.PinState`
* :class:`~.api.enums_communication.PinID`
* :class:`~.api.enums_communication.ConveyorID`
* :class:`~.api.enums_communication.ConveyorDirection`
* :class:`~.api.enums_communication.ObjectColor`
* :class:`~.api.enums_communication.ObjectShape`

.. automodule:: api.enums_communication
    :members:
    :undoc-members:
    :exclude-members: Command
    :member-order: bysource

.. undoc-members -> allow to see members of enums
.. show-inheritance -> display enum.Enum

Python object classes
------------------------------------

Special objects

.. automodule:: api.objects
    :members:
    :no-undoc-members:
    :member-order: bysource

.. |pose_object| replace:: :class:`~.api.objects.PoseObject`