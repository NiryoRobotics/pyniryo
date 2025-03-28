Examples : Conveyor Belt
========================

This document shows how to use Ned's Conveyor Belt.

If you want to see more about Ned's Conveyor Belt functions, you can look at the :py:meth:`conveyor functions<pyniryo.ned.api.tcp_client.NiryoRobot.set_conveyor>`

.. danger::
    If you are using the real robot, make sure the environment around it is clear.

Simple Conveyor control
-------------------------------
This short example shows how to connect a conveyor and
launch its motor (control it by setting its speed and direction):

.. literalinclude:: code_snippets/simple_conveyor.py
   :linenos:



Advanced Conveyor Belt control
-------------------------------
This example shows how to do a certain amount of pick & place by using
the Conveyor Belt with the infrared sensor:

.. literalinclude:: code_snippets/advanced_conveyor.py
   :linenos:

