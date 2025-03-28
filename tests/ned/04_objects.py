import unittest
from collections.abc import Iterable, Sequence

from pyniryo import JointsPosition, PoseObject


class Test01JointsPosition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.joints_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        cls.joints_position = JointsPosition(*cls.joints_list)

    def test_010_is_iterable(self):
        self.assertIsInstance(self.joints_position, Iterable)

    def test_030_has_length(self):
        self.assertTrue(hasattr(self.joints_position, '__len__'))
        self.assertEqual(len(self.joints_position), len(self.joints_list))

    def test_040_slicing(self):
        for i in range(len(self.joints_list)):
            self.assertEqual(self.joints_position[i], self.joints_list[i])
            self.assertEqual(self.joints_position[i:], self.joints_list[i:])
            self.assertEqual(self.joints_position[:i], self.joints_list[:i])

    def test_050_mutable(self):
        self.joints_position[0] = self.joints_list[0]

    def test_060_is_convertible_to_list(self):
        self.assertEqual(self.joints_position.to_list(), list(self.joints_list))


class Test02PoseObject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pose_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        cls.pose_object = PoseObject(*cls.pose_list)

    def test_010_is_iterable(self):
        self.assertIsInstance(self.pose_object, Iterable)

    def test_030_has_length(self):
        self.assertTrue(hasattr(self.pose_object, '__len__'))
        self.assertEqual(len(self.pose_object), len(self.pose_list))

    def test_040_slicing(self):
        for i in range(len(self.pose_list)):
            self.assertEqual(self.pose_object[i], self.pose_list[i])
            self.assertEqual(self.pose_object[i:], self.pose_list[i:])
            self.assertEqual(self.pose_object[:i], self.pose_list[:i])

    def test_060_mutable(self):
        self.pose_object[0] = self.pose_list[0]

    def test_070_is_convertible_to_list(self):
        self.assertEqual(self.pose_object.to_list(), list(self.pose_list))


if __name__ == '__main__':
    unittest.main()
