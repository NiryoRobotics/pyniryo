Functions Documentation
=====================================

.. important::
    Section is not finished yet !

This file presents the different functions and :ref:`Enums` available for image processing


These functions are divided in subsections:

* :ref:`Pure Image Processing` are used to deal with the thresholding,
  contours detection, ..
* :ref:`Workspaces wise` section contains functions to extract workspace
  and deal with the relative position in the workspace
* The section :ref:`Show` allows to display images
* :ref:`Image Editing` contains lot of function which can compress images,
  add text to image, ...



Pure Image Processing
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: vision.image_functions
   :members: threshold_hsv, debug_threshold_color, morphological_transformations, get_contour_barycenter,
             get_contour_angle, biggest_contour_finder, biggest_contours_finder, draw_contours

Workspaces wise
^^^^^^^^^^^^^^^^^^^^

.. automodule:: vision.image_functions
   :members: extract_img_workspace, debug_markers, relative_pos_from_pixels

Show
^^^^^^^^^^^^^^^^^^^^

.. automodule:: vision.image_functions
   :members: show_img_and_check_close, show_img, show_img_and_wait_close

Image Editing
^^^^^^^^^^^^^^^^^^^^

.. automodule:: vision.image_functions
   :members: compress_image, uncompress_image, add_annotation_to_image,
             undistort_image, resize_img, concat_imgs

Enums Image Processing
^^^^^^^^^^^^^^^^^^^^^^^

Enums are used to pass specific parameters to functions.

List of enums:

* :class:`~.vision.enums.ColorHSV`
* :class:`~.vision.enums.ColorHSVPrime`
* :class:`~.vision.enums.ObjectType`
* :class:`~.vision.enums.MorphoType`
* :class:`~.vision.enums.KernelType`

.. automodule:: vision.enums
    :members:
    :undoc-members:
    :member-order: bysource
