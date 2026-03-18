Examples : Dynamic frames
============================

This document shows how to use dynamic frames.

If you want to see more about dynamic frames functions, you can look at :py:meth:`dynamic frames functions<pyniryo.ned.api.tcp_client.NiryoRobot.get_saved_dynamic_frame_list>`

.. danger::
    If you are using the real robot, make sure the environment around it is clear.

Simple dynamic frame control
-------------------------------
This example shows how to create a frame and do a small pick and place in this frame:

.. literalinclude:: code_snippets/frames.py
   :linenos:
