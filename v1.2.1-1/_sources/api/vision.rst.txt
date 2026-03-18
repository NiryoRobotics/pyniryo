.. _vision-api:

Vision API
=====================================

This file presents the different functions and `Enums Image Processing`_ available for image processing.


These functions are divided in subsections:

* `Pure Image Processing`_ are used to deal with the thresholding,
  contours detection, ..
* `Workspaces wise`_ section contains functions to extract workspace
  and deal with the relative position in the workspace
* The section `Show`_ allows to display images
* `Image Editing`_ contains lot of function which can compress images,
  add text to image, ...


.. py:currentmodule:: pyniryo

Pure image processing
^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: pyniryo.vision.image_functions.threshold_hsv
.. automethod:: pyniryo.vision.image_functions.debug_threshold_color
.. automethod:: pyniryo.vision.image_functions.morphological_transformations
.. automethod:: pyniryo.vision.image_functions.get_contour_barycenter
.. automethod:: pyniryo.vision.image_functions.get_contour_angle
.. automethod:: pyniryo.vision.image_functions.biggest_contour_finder
.. automethod:: pyniryo.vision.image_functions.biggest_contours_finder
.. automethod:: pyniryo.vision.image_functions.draw_contours
.. automethod:: pyniryo.vision.image_functions.draw_barycenter
.. automethod:: pyniryo.vision.image_functions.draw_angle

Workspaces wise
^^^^^^^^^^^^^^^^^^^^

.. automethod:: pyniryo.vision.image_functions.extract_img_workspace
.. automethod:: pyniryo.vision.image_functions.debug_markers
.. automethod:: pyniryo.vision.image_functions.relative_pos_from_pixels

Show
^^^^^^^^^^^^^^^^^^^^

.. automethod:: pyniryo.vision.image_functions.show_img_and_check_close
.. automethod:: pyniryo.vision.image_functions.show_img
.. automethod:: pyniryo.vision.image_functions.show_img_and_wait_close

Image Editing
^^^^^^^^^^^^^^^^^^^^

.. automethod:: pyniryo.vision.image_functions.compress_image
.. automethod:: pyniryo.vision.image_functions.uncompress_image
.. automethod:: pyniryo.vision.image_functions.add_annotation_to_image
.. automethod:: pyniryo.vision.image_functions.undistort_image
.. automethod:: pyniryo.vision.image_functions.resize_img
.. automethod:: pyniryo.vision.image_functions.concat_imgs

Enums Image Processing
^^^^^^^^^^^^^^^^^^^^^^^

Enums are used to pass specific parameters to functions.

List of enums:

* :class:`~.pyniryo.vision.enums.ColorHSV`
* :class:`~.pyniryo.vision.enums.ColorHSVPrime`
* :class:`~.pyniryo.vision.enums.ObjectType`
* :class:`~.pyniryo.vision.enums.MorphoType`
* :class:`~.pyniryo.vision.enums.KernelType`

.. automodule:: pyniryo.vision.enums
    :members:
    :undoc-members:
    :member-order: bysource
