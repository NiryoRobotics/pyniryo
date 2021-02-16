Examples: Tool Action
========================

This page shows how to control Ned's tools

If you want to see more, you can look at :ref:`PyNiryo - Tools<Tools>`

.. important::
    In this section, you are already supposed to be connected to a calibrated robot.
    The robot instance is saved in the variable ``robot``

.. danger::
    If you are using the real robot, make sure the environment around it is clear

Tool control
-------------------

Equip Tool
^^^^^^^^^^^^

In order to use a tool, it should be plugged mechanically to the robot but also
connected to the software wise.

To do that, we should use the function
:meth:`~.api.tcp_client.NiryoRobot.update_tool`
which takes no argument. It will scan motor's connections and set the new tool !

The line to equip a new tool is ::

    robot.update_tool()

.. note::
    For the :ref:`Grasping <Grasping>` and :ref:`Releasing <Releasing>` sections,
    this command should be added in your codes! If you want to use a specific
    tool, you need to store the |tool_id| you are using in a variable named ``tool_used``


Grasping
^^^^^^^^^^^^^^^^^

To grasp with any tool, you can use the function
:meth:`~.api.tcp_client.NiryoRobot.grasp_with_tool`. This action corresponds to :

 - Close gripper for Grippers
 - Pull Air for Vacuum Pump
 - Activate for Electromagnet

The line to grasp is ::

    robot.grasp_with_tool()

To grasp an object by specifying the tool ::

    if tool_used in [ToolID.GRIPPER_1, ToolID.GRIPPER_2, ToolID.GRIPPER_3]:
        robot.close_gripper(speed=500)
    elif tool_used == ToolID.ELECTROMAGNET_1:
        pin_electromagnet = PinID.XXX
        robot.setup_electromagnet(pin_electromagnet)
        robot.activate_electromagnet(pin_electromagnet)
    elif tool_used == ToolID.VACUUM_PUMP_1:
        robot.pull_air_vacuum_pump()


Releasing
^^^^^^^^^^^^^^^^^^

To release with any tool, you can use the function
:meth:`~.api.tcp_client.NiryoRobot.release_with_tool`. This action corresponds to:

  - Open gripper for Grippers
  - Push Air for Vacuum pump
  - Deactivate for Electromagnet

To release an object by specifying parameters ::

    if tool_used in [ToolID.GRIPPER_1, ToolID.GRIPPER_2, ToolID.GRIPPER_3]:
        robot.open_gripper(speed=500)
    elif tool_used == ToolID.ELECTROMAGNET_1:
        pin_electromagnet = PinID.XXX
        robot.setup_electromagnet(pin_electromagnet)
        robot.deactivate_electromagnet(pin_electromagnet)
    elif tool_used == ToolID.VACUUM_PUMP_1:
        robot.push_air_vacuum_pump()


Pick & Place with tools
-----------------------------------

A Pick & Place is an action which consists in going to a certain pose
in order to pick an object and then, going to another pose to place it.

This operation can be proceed as follows :

#. Going over the object with a certain offset to avoid collision
#. Going down to the object's height
#. Grasping with tool
#. Going back to step 1's pose.
#. Going over the place pose with a certain offset to avoid collision
#. Going down to place's height
#. Releasing the object with tool
#. Going back to step 5's pose.


There is plenty of ways to perform a pick and place with PyNiryo. Methods will
be presented from the lowest to highest level.

Code Baseline
^^^^^^^^^^^^^^^^^^

For the sake of brevity, every piece of code beside the Pick & Place
function will not be rewritten for every method. So that, you
will need to use the code and implement the Pick & Place function to it  ::

    # Imports
    from pyniryo import *
    
    tool_used = ToolID.XXX  # Tool used for picking
    robot_ip_address = "x.x.x.x" # Robot address
    
    # The pick pose
    pick_pose = PoseObject(
        x=0.25, y=0., z=0.15,
        roll=-0.0, pitch=1.57, yaw=0.0,
    )
    # The Place pose
    place_pose = PoseObject(
        x=0.0, y=-0.25, z=0.1,
        roll=0.0, pitch=1.57, yaw=-1.57)
    
    def pick_n_place_version_x(robot):
        # -- -------------- -- #
        # -- CODE GOES HERE -- #
        # -- -------------- -- #

    if __name__ == '__main__':
        # Connect to robot
        client = NiryoRobot(robot_ip_address)
        # Calibrate robot if robot needs calibration
        client.calibrate_auto()
        # Changing tool
        client.update_tool()
    
        pick_n_place_version_x(client)
    
        # Releasing connection
        client.close_connection()

First Solution : the heaviest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For this first function, every steps are done by hand, as well as
poses computing

.. note::
    In this example, the tool used is a Gripper. If you want to use another
    tool than a gripper, do not forget to adapt grasp & release functions!

::

    def pick_n_place_version_1(robot):
        height_offset = 0.05  # Offset according to Z-Axis to go over pick & place poses
        gripper_speed = 400
    
        # Going Over Object
        robot.move_pose(pick_pose.x, pick_pose.y, pick_pose.z + height_offset,
                                   pick_pose.roll, pick_pose.pitch, pick_pose.yaw)
        # Opening Gripper
        robot.open_gripper(gripper_speed)
        # Going to picking place and closing gripper
        robot.move_pose(pick_pose)
        robot.close_gripper(gripper_speed)
    
        # Raising
        robot.move_pose(pick_pose.x, pick_pose.y, pick_pose.z + height_offset,
                                   pick_pose.roll, pick_pose.pitch, pick_pose.yaw)
    
        # Going Over Place pose
        robot.move_pose(place_pose.x, place_pose.y, place_pose.z + height_offset,
                                   place_pose.roll, place_pose.pitch, place_pose.yaw)
        # Going to Place pose
        robot.move_pose(place_pose)
        # Opening Gripper
        robot.open_gripper(gripper_speed)
        # Raising
        robot.move_pose(place_pose.x, place_pose.y, place_pose.z + height_offset,
                                   place_pose.roll, place_pose.pitch, place_pose.yaw)

Second Solution : Use of PoseObject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For the second solution, we use a  |pose_object| in
order to calculate approach poses more easily

.. note::
    To see more about |pose_object|, go look at
    :ref:`PoseObject dedicated section <How to use the PoseObject>`

::

    def pick_n_place_version_2(robot):
        height_offset = 0.05  # Offset according to Z-Axis to go over pick & place poses

        pick_pose_high = pick_pose.copy_with_offsets(z_offset=height_offset)
        place_pose_high = place_pose.copy_with_offsets(z_offset=height_offset)
    
        # Going Over Object
        robot.move_pose(pick_pose_high)
        # Opening Gripper
        robot.release_with_tool()
        # Going to picking place and closing gripper
        robot.move_pose(pick_pose)
        robot.grasp_with_tool()
        # Raising
        robot.move_pose(pick_pose_high)
    
        # Going Over Place pose
        robot.move_pose(place_pose_high)
        # Going to Place pose
        robot.move_pose(place_pose)
        # Opening Gripper
        robot.release_with_tool(gripper_speed)
        # Raising
        robot.move_pose(place_pose_high)

Third Solution : Pick from pose & Place from pose functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For those who have already seen the API Documentation, you may have seen
pick & place dedicated functions!

In this example, we use
:meth:`~.api.tcp_client.NiryoRobot.pick_from_pose` and
:meth:`~.api.tcp_client.NiryoRobot.place_from_pose` in order
to split our function in only 2 commands! ::

    def pick_n_place_version_3(robot):
        # Pick
        robot.pick_from_pose(pick_pose)
        # Place
        robot.place_from_pose(place_pose)

Fourth Solution : All in one
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The example exposed in the previous section could be useful if you want
to do an action between the pick & the place phases.

For those who want to do everything in one command, you can use
the :meth:`~.api.tcp_client.NiryoRobot.pick_and_place` function ! ::

    def pick_n_place_version_4(robot):
        # Pick & Place
        robot.pick_and_place(pick_pose, place_pose)


.. |tool_id| replace:: :class:`~.api.enums_communication.ToolID`
.. |pose_object| replace:: :class:`~.api.objects.PoseObject`
