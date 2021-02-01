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

PyNiryo allows to write simple script in Python in order to control Ned

.. code-block:: python

    from pyniryo import *

    ned = NiryoRobot("10.10.10.10")

    ned.calibrate_auto()

    ned.move_joints(0.2, -0.3, 0.1, 0.0, 0.5, -0.8)

To see more examples or learn more about the available functions,
full documentation is available at http://docs.niryo.com/dev/pyniryo


License
-------

PyNiryo is distributed under the terms of
`GNU General Public License v3.0 <https://choosealicense.com/licenses/gpl-3.0>`_
