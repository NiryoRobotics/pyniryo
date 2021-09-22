Functions documentation
=====================================

This file presents the different functions and :ref:`source/vision/image_processing_api:Enums Image Processing` available for image processing.


These functions are divided in subsections:

* :ref:`source/vision/image_processing_api:Pure Image Processing` are used to deal with the thresholding,
  contours detection, ..
* :ref:`source/vision/image_processing_api:Workspaces wise` section contains functions to extract workspace
  and deal with the relative position in the workspace
* The section :ref:`source/vision/image_processing_api:Show` allows to display images
* :ref:`source/vision/image_processing_api:Image Editing` contains lot of function which can compress images,
  add text to image, ...



Pure image processing
^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: vision.image_functions.threshold_hsv
.. automethod:: vision.image_functions.debug_threshold_color
.. automethod:: vision.image_functions.morphological_transformations
.. automethod:: vision.image_functions.get_contour_barycenter
.. automethod:: vision.image_functions.get_contour_angle
.. automethod:: vision.image_functions.biggest_contour_finder
.. automethod:: vision.image_functions.biggest_contours_finder
.. automethod:: vision.image_functions.draw_contours

Workspaces wise
^^^^^^^^^^^^^^^^^^^^

.. automethod:: vision.image_functions.extract_img_workspace
.. automethod:: vision.image_functions.debug_markers
.. automethod:: vision.image_functions.relative_pos_from_pixels

Show
^^^^^^^^^^^^^^^^^^^^

.. automethod:: vision.image_functions.show_img_and_check_close
.. automethod:: vision.image_functions.show_img
.. automethod:: vision.image_functions.show_img_and_wait_close

Image Editing
^^^^^^^^^^^^^^^^^^^^

.. automethod:: vision.image_functions.compress_image
.. automethod:: vision.image_functions.uncompress_image
.. automethod:: vision.image_functions.add_annotation_to_image
.. automethod:: vision.image_functions.undistort_image
.. automethod:: vision.image_functions.resize_img
.. automethod:: vision.image_functions.concat_imgs

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
