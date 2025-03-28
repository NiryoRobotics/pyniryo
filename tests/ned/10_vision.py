#!/usr/bin/env python
import numpy as np
import cv2

from pyniryo import ObjectShape, ObjectColor, TcpCommandException, PoseObject, JointsPosition

from .src.base_test import BaseTestTcpApi, BaseTestWithWorkspace


class Test01Camera(BaseTestTcpApi):

    def test_010_get_img_compressed(self):
        img_compressed = self.niryo_robot.get_img_compressed()
        self.assertIsInstance(img_compressed, bytes)
        img = cv2.imdecode(np.frombuffer(img_compressed, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertIsInstance(img, np.ndarray)

    def test_020_get_camera_intrinsics(self):
        camera_intrinsics = self.niryo_robot.get_camera_intrinsics()
        self.assertIsInstance(camera_intrinsics, tuple)
        self.assertEqual(len(camera_intrinsics), 2)
        mtx, dist = camera_intrinsics
        self.assertIsInstance(mtx, np.ndarray)
        self.assertEqual(mtx.shape, (3, 3))

        self.assertIsInstance(dist, np.ndarray)
        self.assertEqual(dist.shape, (1, 5))

    def test_030_set_brightness(self):
        self.assertIsNone(self.niryo_robot.set_brightness(1))

    def test_031_set_brightness_negative_number(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_brightness(-1)

    def test_040_set_contrast(self):
        self.assertIsNone(self.niryo_robot.set_contrast(1))

    def test_041_set_contrast_negative_number(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_contrast(-1)

    def test_050_set_saturation(self):
        self.assertIsNone(self.niryo_robot.set_saturation(1))

    def test_051_set_saturation_negative_number(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_saturation(-1)

    def test_060_get_image_parameters(self):
        image_parameters = self.niryo_robot.get_image_parameters()
        self.assertIsInstance(image_parameters, tuple)
        self.assertEqual(len(image_parameters), 3)
        brightness, contrast, saturation = image_parameters
        self.assertIsInstance(brightness, float)
        self.assertIsInstance(contrast, float)
        self.assertIsInstance(saturation, float)


class Test02Detection(BaseTestWithWorkspace):

    def test_010_detect_object(self):
        object_found, object_rel_pose, shape, color = self.niryo_robot.detect_object(self.workspace_name,
                                                                                     ObjectShape.ANY,
                                                                                     ObjectColor.ANY)
        self.assertIsInstance(object_found, bool)
        self.assertTrue(object_found)
        self.assertEqual(len(object_rel_pose), 3)
        self.assertIsInstance(shape, ObjectShape)
        self.assertIsInstance(color, ObjectColor)

    def test_020_get_target_pose_from_rel(self):
        rel_x, rel_y, rel_yaw = 0.1, 0.1, 0.0
        target_pose = self.niryo_robot.get_target_pose_from_rel(self.workspace_name,
                                                                self.height_offset,
                                                                rel_x,
                                                                rel_y,
                                                                rel_yaw)
        self.assertIsInstance(target_pose, PoseObject)

    def test_030_get_target_pose_from_cam(self):
        object_found, target_pose, shape, color = self.niryo_robot.get_target_pose_from_cam(self.workspace_name,
                                                                                            self.height_offset,
                                                                                            ObjectShape.ANY,
                                                                                            ObjectColor.ANY)
        self.assertIsInstance(object_found, bool)
        self.assertTrue(object_found)
        self.assertIsInstance(target_pose, PoseObject)
        self.assertIsInstance(shape, ObjectShape)
        self.assertIsInstance(color, ObjectColor)


class Test03VisionMove(BaseTestWithWorkspace):

    def test_010_vision_pick(self):
        self.assertIsNotNone(
            self.niryo_robot.vision_pick(self.workspace_name, self.height_offset, ObjectShape.ANY, ObjectColor.ANY))

    def test_020_move_to_object(self):
        self.assertIsNotNone(
            self.niryo_robot.move_to_object(self.workspace_name, self.height_offset, ObjectShape.ANY, ObjectColor.ANY))
