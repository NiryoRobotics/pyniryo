pyniryo
=========

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

PyNiryo is distributed on `PyPI <https://pypi.org>`_ as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 2.7/3.5+

.. code-block:: bash

    $ pip install pyniryo

Documentation
-----------------

PyNiryo allows to write simple script in Python in order to control Niryo's robots

.. code-block:: python

    from pyniryo import *

    robot = NiryoRobot("10.10.10.10")

    robot.calibrate_auto()

    robot.move(JointsPosition(0.2, -0.3, 0.1, 0.0, 0.5, -0.8))

To see more examples or learn more about the available functions,
full documentation is available `here <https://niryorobotics.github.io/pyniryo>`_.

Nate Robot API
--------------

PyNiryo also provides a client for controlling Niryo's Nate robots through their API.

.. code-block:: python

    from pyniryo.nate.client import Nate
    from pyniryo.nate.models import Joints

    # Initialize with hostname and credentials
    nate = Nate(hostname="10.10.10.10", login=("user", "us3r"))

    # Or use environment variables
    nate = Nate()

    # Move the robot
    nate.robot.move(Joints(0, 0, 0, 0, 0, 0)).wait()

Constructor Arguments
~~~~~~~~~~~~~~~~~~~~~

The ``Nate`` class constructor accepts the following parameters:

- ``hostname`` (str | None): The hostname or IP address of the Nate API. If ``None``, it will use the ``NATE_HOSTNAME`` environment variable, defaulting to ``'localhost'`` if not set.
- ``token`` (str | None): Authentication token for API access. If ``None``, it will use the ``NATE_TOKEN`` environment variable. If a token is not provided, username/password authentication will be used instead.
- ``login`` (tuple[str, str] | None): A tuple containing ``(username, password)`` for authentication. If ``None``, it will use the ``NATE_USERNAME`` and ``NATE_PASSWORD`` environment variables. This parameter is omitted when using token authentication.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The following environment variables can be used to configure the Nate client:

**Authentication:**

- ``NATE_HOSTNAME`` - The hostname or IP address of the Nate API (default: ``'localhost'``)
- ``NATE_TOKEN`` - Authentication token for API access
- ``NATE_USERNAME`` - Username for login authentication (used when token is not provided)
- ``NATE_PASSWORD`` - Password for login authentication (used when token is not provided)

**Advanced Options:**

- ``NATE_HTTP_PORT`` - HTTP port for API communication (default: ``8443``)
- ``NATE_MQTT_PORT`` - MQTT port for real-time communication (default: ``1883``)
- ``NATE_INSECURE`` - Set to any value to enable insecure mode (disables SSL verification)
- ``NATE_USE_HTTP`` - Set to any value to use HTTP instead of HTTPS

License
-------

PyNiryo is distributed under the terms of
`GNU General Public License v3.0 <https://choosealicense.com/licenses/gpl-3.0>`_
