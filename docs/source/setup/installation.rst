Installation
============

| The library uses `Python <https://www.python.org/>`_, which must be installed and available
 in your working environment
| The version should be **equal or above** :

* 2.7 if you are using Python 2
* 3.6 if you are using Python 3

.. hint::
    To check your Python version, use the command ``python --version`` if
    you are using Python 2 and ``python3 --version`` if you are using Python3

The below sections explain how to install the library with **pip**,
the package installer for Python

.. attention::
    If you have both Python 2 & Python 3 installed on your computer, the command
    ``pip`` will install packages in Python 2 version.
    You should use ``pip3`` instead in order to target Python 3

Installation with pip
-------------------------------

You need to install Numpy package beforehand: ::

    pip install numpy


To install Ned's Python package via ``pip``, simply execute::

    pip install pyniryo

You can find more information about
the PyPi package `here <https://pypi.org/project/pyniryo/>`_

If you also want to use Vision functions to do your own Image Processing pipeline
install OpenCV via the command: ::

    pip install opencv-python



Uninstall
---------

To uninstall the library use::

    pip uninstall pyniryo

