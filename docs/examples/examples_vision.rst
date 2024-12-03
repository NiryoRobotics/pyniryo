Examples: Vision
========================

This page shows how to use Ned's Vision Set.

| If you want to see more about Ned's Vision functions,
 you can look at :ref:`PyNiryo - Vision<vision-api>`
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

As the examples start always the same, add the following lines at the beginning of codes

.. literalinclude:: code_snippets/vision_header.py
   :caption: vision_header.py
   :linenos:

.. hint::
    All the following examples are only a part of what can be made
    with the API in terms of Vision. We advise you to look at :ref:`API - Vision<vision-api>`
    to understand more deeply

Simple Vision Pick & Place
-------------------------------
The goal of a Vision Pick & Place is the same as a classical Pick & Place,
with a close difference: the camera detects where the robot has to go in order to pick!

This short example shows how to do your first Vision pick using the
:meth:`~.api.tcp_client.NiryoRobot.vision_pick` function:

.. literalinclude:: code_snippets/vision_simple_pick_place.py
   :linenos:

.. _code_details_simple_vision_pick_n_place:

Code Details - Simple Vision Pick and Place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To execute a Vision pick, we firstly need to go to a place where the robot will
be able to see the workspace

.. literalinclude:: code_snippets/vision_simple_pick_place.py
   :linenos:
   :lineno-match:
   :lines: 3

Then, we try to perform a Vision pick in the workspace with the
:meth:`~.api.tcp_client.NiryoRobot.vision_pick` function:

.. literalinclude:: code_snippets/vision_simple_pick_place.py
   :linenos:
   :lineno-match:
   :lines: 5


Variables ``shape_ret`` and ``color_ret`` are respectively of type
:class:`~.api.enums_communication.ObjectShape` and :class:`~.api.enums_communication.ObjectColor`, and
store the shape and the color of the detected object! We will not use them for this first
example.

The ``obj_found`` variable is a boolean which indicates whereas an
object has been found and picked, or not. Thus, if the pick worked,
we can place the object at the place pose.

.. literalinclude:: code_snippets/vision_simple_pick_place.py
   :linenos:
   :lineno-match:
   :lines: 6-7

Finally, we turn learning mode on

.. literalinclude:: code_snippets/vision_simple_pick_place.py
   :linenos:
   :lineno-match:
   :lines: 9


.. note::
    If your ``obj_found`` variable indicates ``False``, check that:

    * Nothing obstructs the camera field of view
    * Workspace's 4 markers are visible
    * At least 1 object is placed fully inside the workspace

First conditioning via Vision
-------------------------------------------
In most of use cases, the robot will need to perform more than one Pick & Place.
In this example, we will see how to condition multiple objects according to
a straight line:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:

.. _code_details_first_conditionning_via_vision:

Code Details - First Conditioning via Vision
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to catch ``max_catch_count`` objects, and space each of
them by ``offset_size`` meter:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 4-5

We start a loop until the robot has caught ``max_catch_count`` objects:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 8-9

For each iteration, we firstly go to the observation pose and then,
try to make a Vision pick in the workspace:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 11-14


If the Vision pick failed, we wait 0.1 second and then, start a new iteration:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 15-17

Else, we compute the new place position according to the number of catches, and
then, go placing the object at that place:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 20-21

We also increment the ``catch_count`` variable

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 23

Once the target catch number is achieved, we go to sleep:

.. literalinclude:: code_snippets/vision_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 25

Multi Reference Conditioning
-------------------------------
During a conditioning task, objects may not always be placed as the same
place according to their type. In this example, we will see how to align object
according to their color, using the
color element :class:`~.api.enums_communication.ObjectColor`
returned by :meth:`~.api.tcp_client.NiryoRobot.vision_pick` function

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:

.. _code_details_multi_ref_conditioning:

Code Details - Multi Reference Conditioning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to catch objects until Vision Pick failed ``max_failure_count`` times.
Each of the object will be put on a specific column according to its color.
The number of catches for each color will be stored on a dictionary ``count_dict``.

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 4-17

For each iteration, we firstly go to the observation pose and then,
try to make a Vision pick in the workspace

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 19-21

If the Vision pick failed, we wait 0.1 second and then, start a new iteration, without
forgetting to increment the failure counter

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 22-25

Else, we compute the new place position according to the number of catches, and
then, go place the object at that place:

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 27-41

We increment the ``count_dict`` dictionary and reset ``try_without_success``:

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 44-45

Once the target catch number is achieved, we go to sleep:

.. literalinclude:: code_snippets/vision_multi_reference_conditioning.py
   :linenos:
   :lineno-match:
   :lines: 47

Sorting Pick with Conveyor
-------------------------------

An interesting way to bring objects to the robot, is the use of a Conveyor Belt.
In this examples, we will see how to catch only a certain type of object by
stopping the conveyor as soon as the object is detected on the workspace.

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:

Code Details - Sort Picking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly, we initialize your process: we want the robot to catch 4 red circles. To do so,
we set variables ``shape_expected`` and ``color_expected`` with
:attr:`ObjectShape.CIRCLE <api.enums_communication.ObjectShape.CIRCLE>`
and :attr:`ObjectColor.RED <api.enums_communication.ObjectColor.RED>`.

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 5-8

We activate the connection with the Conveyor Belt and
start a loop until the robot has caught ``max_catch_count`` objects

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 10-13

For each iteration, we firstly run the Conveyor Belt (if the latter is already running,
nothing will happen), then go to the observation pose

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 14-17

We then check if an object corresponding to our criteria
is in the workspace. If not, we wait 0.5 second and then, start a new iteration

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 19-22

Else, stop the Conveyor Belt and try to make a Vision pick

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 23-28

If Vision Pick succeed, compute new place pose, and place the object

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 30-34

Once the target catch number is achieved, we stop the Conveyor Belt and go to sleep

.. literalinclude:: code_snippets/sorting_pick_with_conveyor.py
   :linenos:
   :lineno-match:
   :lines: 36-40

