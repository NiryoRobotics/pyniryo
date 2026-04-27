PyNiryo Documentation
================================

.. image:: images/PyNiryo_logo_2.png
   :width: 50%
   :align: center


This documentation presents Ned's PyPi package, which is a
TCP API made with Python.

It offers a simple way for developers to create programs for robot and
to control them via remote communication from their computers.
Contrary to the Python ROS Wrapper, the user will not need to be connected on the robot
through a terminal.

.. note:: This package is able to control Ned in simulation
   as well as the physical robot.

.. figure:: images/niryo_ned_front.jpg
   :alt: Niryo Ned
   :height: 400px
   :align: center

   Ned

Version compatibility
----------------------------

.. list-table:: Version compatibility table
   :header-rows: 1
   :widths: auto
   :stub-columns: 0
   :align: center

   *  -  PyNiryo version
      -  ROS Stack version
      -  Robot
   *  -  <= 1.0.5
      -  <= 3.2.0
      -  ``Ned``
   *  -  1.1.0
      -  4.0.0
      -  ``Niryo One``, ``Ned``, ``Ned2``

Before getting started
----------------------------


| If you haven’t already done so, make sure to learn about
 the ROS robot software by reading `ROS documentation <https://docs.niryo.com/dev/ros/index.html>`_.

| This documentation also contains everything you need to
 know if you want to use Ned through simulation.


Sections organization
-----------------------------------

This document is organized in 4 main sections.

Setup
^^^^^^^^^^^

Install & Setup your environment in order to use Ned with PyNiryo.

Firstly, follow :doc:`Installation instructions <source/setup/installation>`,
then :doc:`find your Robot IP address <source/setup/ip_address>` to be ready.

.. toctree::
   :caption: Setup
   :hidden:

   source/setup/installation
   source/setup/ip_address
   source/setup/verify_setup

Examples
^^^^^^^^^^^^^^^

Learn how to use the PyNiryo package to implement various tasks.

.. toctree::
   :hidden:
   :caption: Examples

   source/examples/examples_basics
   source/examples/examples_movement
   source/examples/examples_tool_action
   source/examples/examples_conveyor
   source/examples/examples_vision
   source/examples/code_templates

API Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Master controls with PyNiryo with full the detailed functions
:doc:`here <source/api_doc/api>`.

Discover also :doc:`Vision Functions <source/vision/image_processing_overview>`
to create your own image processing pipelines!

.. toctree::
   :hidden:
   :caption: API Documentation

   source/api_doc/api

Start with Image Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^


Discover how to create your own image processing pipelines!


.. toctree::
   :hidden:
   :caption: Image Processing

   source/vision/image_processing_overview
   source/vision/image_processing_api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

