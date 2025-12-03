Examples: Tool action
========================

This page shows how to control Ned's tools.

If you want to see more, you can look at :py:meth:`tools functions<pyniryo.api.tcp_client.NiryoRobot.tool>`

.. important::
    In this section, you are already supposed to be connected to a calibrated robot.
    The robot instance is saved in the variable ``robot``.

.. danger::
    If you are using the real robot, make sure the environment around it is clear.

Tool control
-------------------

Equip Tool
^^^^^^^^^^^^

In order to use a tool, it should be plugged mechanically to the robot but also
connected to the software wise.

To do that, we should use the function
:meth:`~.api.tcp_client.NiryoRobot.update_tool`
which takes no argument. It will scan motor's connections and set the new tool!

The line to equip a new tool is:

.. code-block:: python
   :linenos:

    robot.update_tool()

.. note::
    For the `Grasping`_ and `Releasing`_ sections,
    this command should be added in your codes! If you want to use a specific
    tool, you need to store the |tool_id| you are using in a variable named ``tool_used``.


Grasping
^^^^^^^^^^^^^^^^^

To grasp with any tool, you can use the function
:meth:`~.api.tcp_client.NiryoRobot.grasp_with_tool`. This action corresponds to:

 - Close gripper for Grippers
 - Pull Air for Vacuum Pump
 - Activate for Electromagnet

The line to grasp is:

.. code-block:: python
   :linenos:

    robot.grasp_with_tool()

To grasp an object by specifying the tool:

.. code-block:: python
   :linenos:

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

To release an object by specifying parameters:

.. code-block:: python
   :linenos:

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

This operation can be proceed as follows:

#. Going over the object with a certain offset to avoid collision;
#. Going down to the object's height;
#. Grasping with tool;
#. Going back to step 1's pose;
#. Going over the place pose with a certain offset to avoid collision;
#. Going down to place's height;
#. Releasing the object with tool;
#. Going back to step 5's pose.


There are plenty of ways to perform a pick and place with PyNiryo. Methods will
be presented from the lowest to highest level.

Code Baseline
^^^^^^^^^^^^^^^^^^

For the sake of brevity, every piece of code beside the Pick & Place
function will not be rewritten for every method. So that, you
will need to use the code and implement the Pick & Place function to it.

.. literalinclude:: code_snippets/tool_action.py


First Solution: the heaviest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For this first function, every steps are done by hand, as well as
poses computing.

.. note::
    To see more about |pose_object|, go look at
    :ref:`PoseObject dedicated section <howto-poseobject>`

.. literalinclude:: code_snippets/pick_n_place_functions.py
   :linenos:
   :pyobject: pick_n_place_version_1


Second Solution: Pick from pose & Place from pose functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For those who have already seen the API Documentation, you may have seen
pick & place dedicated functions!

In this example, we use
:meth:`~.api.tcp_client.NiryoRobot.pick_from_pose` and
:meth:`~.api.tcp_client.NiryoRobot.place_from_pose` in order
to split our function in only 2 commands!

.. literalinclude:: code_snippets/pick_n_place_functions.py
   :linenos:
   :pyobject: pick_n_place_version_2

Third Solution: All in one
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The example exposed in the previous section could be useful if you want
to do an action between the pick & the place phases.

For those who want to do everything in one command, you can use
the :meth:`~.api.tcp_client.NiryoRobot.pick_and_place` function!

.. literalinclude:: code_snippets/pick_n_place_functions.py
   :linenos:
   :pyobject: pick_n_place_version_3


.. |tool_id| replace:: :class:`pyniryo.api.enums_communication.ToolID`
.. |pose_object| replace:: :class:`~pyniryo.api.objects.PoseObject`
