from pyniryo import PoseObject, PoseMetadata, TcpCommandException, ConveyorID

from src.base_test import BaseTestTcpApi


class Test01PickAndPlace(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.pose_list = [0.2, 0.1, 0.1, 0., 1.57, 0.]
        cls.pose_v1 = PoseObject(0.2, -0.1, 0.1, 0.0, 1.57, 0.0, metadata=PoseMetadata.v1())
        cls.pose_v2 = PoseObject(0.2, 0.1, 0.1, 0.0, -1.57, 3.14)

    def test_010_pick_from_pose(self):
        for pose in [self.pose_list, self.pose_v1, self.pose_v2]:
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.pick_from_pose(pose))

    def test_020_pick(self):
        for pose in [self.pose_v1, self.pose_v2]:
            self.assertIsNone(self.niryo_robot.pick(pose))

    def test_030_pick_w_list(self):
        with self.assertRaises(AttributeError):
            self.niryo_robot.pick(self.pose_list)

    def test_040_place_from_pose(self):
        for pose in [self.pose_list, self.pose_v1, self.pose_v2]:
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.place_from_pose(pose))

    def test_050_place(self):
        for pose in [self.pose_v1, self.pose_v2]:
            self.assertIsNone(self.niryo_robot.place(pose))

    def test_060_place_w_list(self):
        with self.assertRaises(AttributeError):
            self.niryo_robot.place(self.pose_list)

    def test_070_pick_and_place(self):
        for pose_a in [self.pose_list, self.pose_v1, self.pose_v2]:
            for pose_b in [self.pose_list, self.pose_v1, self.pose_v2]:
                self.assertIsNone(self.niryo_robot.pick_and_place(pose_a, pose_b))
