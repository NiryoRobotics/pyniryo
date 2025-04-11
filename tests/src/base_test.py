import os
import unittest
import numpy as np
from uuid import uuid4

from pyniryo import NiryoRobot, PoseObject, PoseMetadata, JointsPosition
from pyniryo.api.exceptions import ClientNotConnectedException


class BaseTestTcpApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls, needs_move=False):
        robot_ip_address = os.environ.get('ROBOT_IP_ADDRESS', '127.0.0.1')
        try:
            cls.niryo_robot: NiryoRobot = NiryoRobot(robot_ip_address, verbose=False)
        except ClientNotConnectedException:
            cls.niryo_robot = None

        cls._needs_move = needs_move

    @classmethod
    def tearDownClass(cls):
        if cls.niryo_robot is None:
            return
        cls.niryo_robot.close_connection()

    def setUp(self):
        self.assertIsNotNone(self.niryo_robot, "Can't connect to the robot")
        # clean the flag to not impact the following test if the previous one failed
        self.niryo_robot.clear_collision_detected()
        if self._needs_move:
            self.niryo_robot.calibrate_auto()
            self.niryo_robot.move_to_home_pose()

    @staticmethod
    def assertAlmostEqualVector(a, b, decimal=1):
        np.testing.assert_almost_equal(a, b, decimal)

    def assertAlmostEqualJoints(self, a, b, decimal=1):
        if isinstance(a, list):
            a = JointsPosition(*a)
        if isinstance(b, list):
            b = JointsPosition(*b)
        self.assertAlmostEqualVector(a.to_list(), b.to_list(), decimal)

    def assertAlmostEqualPose(self, a, b, decimal=1):
        """
        Ensure the poses are compatible, then convert the euler angles to quaternions
        """
        if isinstance(a, list):
            a = PoseObject(*a, metadata=PoseMetadata.v1())
        if isinstance(b, list):
            b = PoseObject(*b, metadata=PoseMetadata.v1())

        # Compare the position
        self.assertAlmostEqualVector([a.x, a.y, a.z], [b.x, b.y, b.z], decimal)

        # Compare the orientation
        product = np.dot(a.quaternion(), b.quaternion())
        threshold = 1 - 10**-decimal
        self.assertGreater(np.abs(product), threshold)

    def assertWarnsDeprecated(self):
        return self.assertWarns(DeprecationWarning)


class BaseTestWithWorkspace(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.niryo_robot.update_tool()

        cls.observation_pose = JointsPosition(0, 0.3, -0.8, 0, -1.35, 0)
        workspace_id = str(uuid4())[:4]
        cls.workspace_name = f'workspace_pyniryo_test_{workspace_id}'
        cls.height_offset = 0.1

        if cls.workspace_name in cls.niryo_robot.get_workspace_list():
            cls.niryo_robot.delete_workspace(cls.workspace_name)

        point_1 = [0.120, -0.085, 0]
        point_2 = [0.120, 0.085, 0]
        point_3 = [0.205, 0.085, 0]
        point_4 = [0.205, -0.085, 0]
        cls.niryo_robot.save_workspace_from_points(cls.workspace_name, point_1, point_2, point_3, point_4)

    @classmethod
    def tearDownClass(cls):
        cls.niryo_robot.delete_workspace(cls.workspace_name)
        super().tearDownClass()

    def setUp(self):
        self.assertIsNotNone(self.niryo_robot, "Can't connect to the robot")
        # clean the flag to not impact the following test if the previous one failed
        self.niryo_robot.clear_collision_detected()
        if self._needs_move:
            self.niryo_robot.calibrate_auto()
        self.niryo_robot.move(self.observation_pose)
