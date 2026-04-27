Versions compatibility
----------------------------

.. list-table:: Version compatibility table
   :header-rows: 1
   :widths: auto
   :stub-columns: 0
   :align: center

   *  -  PyNiryo version
      -  Robot system version
      -  Robot
   *  -  <= 1.0.5
      -  <= 3.2.0
      -  ``Ned``
   *  -  1.1.0
      -  4.0.0
      -  ``Niryo One``, ``Ned``, ``Ned2``
   *  -  1.1.1
      -  4.0.1
      -  ``Niryo One``, ``Ned``, ``Ned2``
   *  -  1.1.2
      -  >=4.1.1
      -  ``Niryo One``, ``Ned``, ``Ned2``
   *  - 1.2.0
      - >= 5.5.0
      - ``Ned2``

.. warning::
   Starting PyNiryo 1.2.0, the positions are no longer arrays of float but classes instead. The primary goal of this is to allow us have a better control on the robot positions.
   Since we are able to differenciate poses from joints, the api becomes more easy to use as you can use the functions without worrying about the type of pose you're using.
   Therefore, the functions such as move_joints or move_pose are no longer needed and are replaced by generic functions such as move.

   Please note that the old functions have been kept in order to maintain the compatibility with older version, but they are marked deprecated and will soon be deleted.
   For instance, the functions :meth:`~.api.tcp_client.NiryoRobot.move_pose`, :meth:`~.api.tcp_client.NiryoRobot.move_joints` and :meth:`~.api.tcp_client.NiryoRobot.move_linear_pose` have all been deprecated in favor of :meth:`~.api.tcp_client.NiryoRobot.move`
