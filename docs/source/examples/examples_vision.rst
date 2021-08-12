Examples: Vision
========================

This page shows how to use Ned's Vision Set.

| If you want to see more about Ned's Vision functions,
 you can look at :ref:`PyNiryo - Vision<source/api_doc/api:Vision>`
| If you want to see how to do Image Processing,
 go check out the :doc:`Image Processing section<../vision/image_processing_overview>`.

.. note::
    Even if you do not own a Vision Set, you can still realize these examples
    with the Gazebo simulation version.

.. danger::
    If you are using the real robot, make sure the environment around it is clear.


Needed piece of code
-------------------------------
.. important::
    In order to achieve the following examples, you need to
    create a vision workspace. In this page, the workspace used is named ``workspace_1``.
    To create it, the user should go on Niryo Studio!

As the examples start always the same, add the following lines at the beginning of codes::

    # Imports
    from pyniryo import *

    # - Constants
    workspace_name = "workspace_1"  # Robot's Workspace Name
    robot_ip_address = "x.x.x.x"

    # The pose from where the image processing happens
    observation_pose = PoseObject(
        x=0.16, y=0.0, z=0.35,
        roll=0.0, pitch=1.57, yaw=0.0,
    )
    # Place pose
    place_pose = PoseObject(
        x=0.0, y=-0.2, z=0.12,
        roll=0.0, pitch=1.57, yaw=-1.57
    )

    # - Initialization

    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if the robot needs calibration
    robot.calibrate_auto()
    # Updating tool
    robot.update_tool()

    # --- -------------- --- #
    # --- CODE GOES HERE --- #
    # --- -------------- --- #

    robot.close_connection()

.. hint::
    All the following examples are only a part of what can be made
    with the API in terms of Vision. We advise you to look at :ref:`API - Vision<source/api_doc/api:Vision>`
    to understand more deeply

Simple Vision Pick & Place
-------------------------------
The goal of a Vision Pick & Place is the same as a classical Pick & Place,
with a close difference: the camera detects where the robot has to go in order to pick!

This short example shows how to do your first Vision pick using the
:meth:`~.api.tcp_client.NiryoRobot.vision_pick` function: ::

    robot.move_pose(observation_pose)
    # Trying to pick target using camera
    obj_found, shape_ret, color_ret = robot.vision_pick(workspace_name)
    if obj_found:
        robot.place_from_pose(place_pose)

    robot.set_learning_mode(True)

.. _code_details_simple_vision_pick_n_place:

Code Details - Simple Vision Pick and Place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To execute a Vision pick, we firstly need to go to a place where the robot will
be able to see the workspace::

    robot.move_pose(observation_pose)

Then, we try to perform a Vision pick in the workspace with the
:meth:`~.api.tcp_client.NiryoRobot.vision_pick` function: ::

    obj_found, shape_ret, color_ret = robot.vision_pick(workspace_name)


Variables ``shape_ret`` and ``color_ret`` are respectively of type
:class:`~.api.enums_communication.ObjectShape` and :class:`~.api.enums_communication.ObjectColor`, and
store the shape and the color of the detected object! We will not use them for this first
example.

The ``obj_found`` variable is a boolean which indicates whereas an
object has been found and picked, or not. Thus, if the pick worked,
we can place the object at the place pose. ::

    if obj_found:
        robot.place_from_pose(place_pose)

Finally, we turn learning mode on::

    robot.set_learning_mode(True)


.. note::
    If your ``obj_found`` variable indicates ``False``, check that:

    * Nothing obstructs the camera field of view
    * Workspace's 4 markers are visible
    * At least 1 object is placed fully inside the workspace

First conditioning via Vision
-------------------------------------------
In most of use cases, the robot will need to perform more than one Pick & Place.
In this example, we will see how to condition multiple objects according to
a straight line: ::

    # Initializing variables
    offset_size = 0.05
    max_catch_count = 4

    # Loop until enough objects have been caught
    catch_count = 0
    while catch_count < max_catch_count:
        # Moving to observation pose
        robot.move_pose(observation_pose)

        # Trying to get object via Vision Pick
        obj_found, shape, color = robot.vision_pick(workspace_name)
        if not obj_found:
            robot.wait(0.1)
            continue

        # Calculate place pose and going to place the object
        next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
        robot.place_from_pose(next_place_pose)

        catch_count += 1

    robot.go_to_sleep()

.. _code_details_first_conditionning_via_vision:

Code Details - First Conditioning via Vision
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to catch ``max_catch_count`` objects, and space each of
them by ``offset_size`` meter: ::

    offset_size = 0.05
    max_catch_count = 4

We start a loop until the robot has caught ``max_catch_count`` objects: ::

    catch_count = 0
    while catch_count < max_catch_count:

For each iteration, we firstly go to the observation pose and then,
try to make a Vision pick in the workspace: ::

    robot.move_pose(observation_pose)

    obj_found, shape, color = robot.vision_pick(workspace_name)


If the Vision pick failed, we wait 0.1 second and then, start a new iteration: ::

    if not obj_found:
        robot.wait(0.1)
        continue

Else, we compute the new place position according to the number of catches, and
then, go placing the object at that place: ::

    next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
    robot.place_from_pose(next_place_pose)

We also increment the ``catch_count`` variable::

    catch_count += 1

Once the target catch number is achieved, we go to sleep: ::

    robot.go_to_sleep()


Multi Reference Conditioning
-------------------------------
During a conditioning task, objects may not always be placed as the same
place according to their type. In this example, we will see how to align object
according to their color, using the
color element :class:`~.api.enums_communication.ObjectColor`
returned by :meth:`~.api.tcp_client.NiryoRobot.vision_pick` function::

    # Distance between elements
    offset_size = 0.05
    max_failure_count = 3

    # Dict to write catch history
    count_dict = {
        ObjectColor.BLUE: 0,
        ObjectColor.RED: 0,
        ObjectColor.GREEN: 0,
    }

    try_without_success = 0
    # Loop until too much failures
    while try_without_success < max_failure_count:
        # Moving to observation pose
        robot.move_pose(observation_pose)
        # Trying to get object via Vision Pick
        obj_found, shape, color = robot.vision_pick(workspace_name)
        if not obj_found:
            try_without_success += 1
            robot.wait(0.1)
            continue

        # Choose X position according to how the color line is filled
        offset_x_ind = count_dict[color]

        # Choose Y position according to ObjectColor
        if color == ObjectColor.BLUE:
            offset_y_ind = -1
        elif color == ObjectColor.RED:
            offset_y_ind = 0
        else:
            offset_y_ind = 1

        # Going to place the object
        next_place_pose = place_pose.copy_with_offsets(x_offset=offset_x_ind * offset_size,
                                                       y_offset=offset_y_ind * offset_size)
        robot.place_from_pose(next_place_pose)

        # Increment count
        count_dict[color] += 1
        try_without_success = 0

    robot.go_to_sleep()

.. _code_details_multi_ref_conditioning:

Code Details - Multi Reference Conditioning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to catch objects until Vision Pick failed ``max_failure_count`` times.
Each of the object will be put on a specific column according to its color.
The number of catches for each color will be stored on a dictionary ``count_dict``. ::

    # Distance between elements
    offset_size = 0.05
    max_failure_count = 3

    # Dict to write catch history
    count_dict = {
        ObjectColor.BLUE: 0,
        ObjectColor.RED: 0,
        ObjectColor.GREEN: 0,
    }

    try_without_success = 0
    # Loop until too much failures
    while try_without_success < max_failure_count:

For each iteration, we firstly go to the observation pose and then,
try to make a Vision pick in the workspace::

    robot.move_pose(observation_pose)

    obj_found, shape, color = robot.vision_pick(workspace_name)

If the Vision pick failed, we wait 0.1 second and then, start a new iteration, without
forgetting to increment the failure counter::

    if not obj_found:
        try_without_success += 1
        robot.wait(0.1)
        continue

Else, we compute the new place position according to the number of catches, and
then, go place the object at that place::

    # Choose X position according to how the color line is filled
    offset_x_ind = count_dict[color]

    # Choose Y position according to ObjectColor
    if color == ObjectColor.BLUE:
        offset_y_ind = -1
    elif color == ObjectColor.RED:
        offset_y_ind = 0
    else:
        offset_y_ind = 1

    # Going to place the object
    next_place_pose = place_pose.copy_with_offsets(x_offset=offset_x_ind * offset_size,
                                                   y_offset=offset_y_ind * offset_size)
    robot.place_from_pose(next_place_pose)

We increment the ``count_dict`` dictionary and reset ``try_without_success``: ::

    count_dict[color] += 1
    try_without_success = 0

Once the target catch number is achieved, we go to sleep: ::

    robot.go_to_sleep()

Sorting Pick with Conveyor
-------------------------------

An interesting way to bring objects to the robot, is the use of a Conveyor Belt.
In this examples, we will see how to catch only a certain type of object by
stopping the conveyor as soon as the object is detected on the workspace. ::

    # Initializing variables
    offset_size = 0.05
    max_catch_count = 4
    shape_expected = ObjectShape.CIRCLE
    color_expected = ObjectColor.RED

    conveyor_id = robot.set_conveyor()

    catch_count = 0
    while catch_count < max_catch_count:
        # Turning conveyor on
        robot.run_conveyor(conveyor_id)
        # Moving to observation pose
        robot.move_pose(observation_pose)
        # Check if object is in the workspace
        obj_found, pos_array, shape, color = robot.detect_object(workspace_name,
                                                                 shape=shape_expected,
                                                                 color=color_expected)
        if not obj_found:
            robot.wait(0.5)  # Wait to let the conveyor turn a bit
            continue
        # Stopping conveyor
        robot.stop_conveyor(conveyor_id)
        # Making a vision pick
        obj_found, shape, color = robot.vision_pick(workspace_name,
                                                    shape=shape_expected,
                                                    color=color_expected)
        if not obj_found:  # If visual pick did not work
            continue

        # Calculate place pose and going to place the object
        next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
        robot.place_from_pose(next_place_pose)

        catch_count += 1

    # Stopping & unsetting conveyor
    robot.stop_conveyor(conveyor_id)
    robot.unset_conveyor(conveyor_id)

    robot.go_to_sleep()

Code Details - Sort Picking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly, we initialize your process: we want the robot to catch 4 red circles. To do so,
we set variables ``shape_expected`` and ``color_expected`` with
:attr:`ObjectShape.CIRCLE <api.enums_communication.ObjectShape.CIRCLE>`
and :attr:`ObjectColor.RED <api.enums_communication.ObjectColor.RED>`. ::

    offset_size = 0.05
    max_catch_count = 4
    shape_expected = ObjectShape.CIRCLE
    color_expected = ObjectColor.RED

We activate the connection with the Conveyor Belt and
start a loop until the robot has caught ``max_catch_count`` objects::

    conveyor_id = robot.set_conveyor()

    catch_count = 0
    while catch_count < max_catch_count:

For each iteration, we firstly run the Conveyor Belt (if the latter is already running,
nothing will happen), then go to the observation pose::

        # Turning the Conveyor Belt on
        robot.run_conveyor(conveyor_id)
        # Moving to observation pose
        robot.move_pose(observation_pose)

We then check if an object corresponding to our criteria
is in the workspace. If not, we wait 0.5 second and then, start a new iteration::

    obj_found, pos_array, shape, color = robot.detect_object(workspace_name,
                                                             shape=shape_expected,
                                                             color=color_expected)
    if not obj_found:
        robot.wait(0.5)  # Wait to let the conveyor turn a bit
        continue

Else, stop the Conveyor Belt and try to make a Vision pick::

    # Stopping Conveyor Belt
    robot.stop_conveyor(conveyor_id)
    # Making a Vision pick
    obj_found, shape, color = robot.vision_pick(workspace_name,
                                                shape=shape_expected,
                                                color=color_expected)
    if not obj_found:  # If visual pick did not work
        continue

If Vision Pick succeed, compute new place pose, and place the object::

    # Calculate place pose and going to place the object
    next_place_pose = place_pose.copy_with_offsets(x_offset=catch_count * offset_size)
    robot.place_from_pose(next_place_pose)

    catch_count += 1

Once the target catch number is achieved, we stop the Conveyor Belt and go to sleep::

    # Stopping & unsetting Conveyor Belt
    robot.stop_conveyor(conveyor_id)
    robot.unset_conveyor(conveyor_id)

    robot.go_to_sleep()

