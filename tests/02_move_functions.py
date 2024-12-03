import math

from pyniryo import TcpCommandException, ConveyorID, PoseObject, RobotAxis, PoseMetadata, JointsPosition, TcpVersion
from src.base_test import BaseTestTcpApi


class Test01Joints(BaseTestTcpApi):
    # TODO : Add limits tests for joints && poses

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.joints = [
            JointsPosition(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            JointsPosition(0.1, -0.1, 0.0, 0.0, 0.0, 0.0),
            JointsPosition(0.0, 0.44, -1.22, 0.0, 0.0, 0.0),
            JointsPosition(-1.0, 0.44, -0.6, 0.8, 1.2, -1.4)
        ]

    def test_010_get_joints(self):
        self.assertIsInstance(self.niryo_robot.get_joints(), JointsPosition)
        self.assertIsInstance(self.niryo_robot.joints, JointsPosition)
        self.assertAlmostEqualJoints(self.niryo_robot.get_joints(), self.niryo_robot.joints)

    def test_020_move_joints(self):
        for joints_position in self.joints:
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.move_joints(joints_position))
            self.assertAlmostEqualJoints(self.niryo_robot.get_joints(), joints_position)

    def test_030_move_joints_wrong_params(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_joints(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)

    def test_040_move(self):
        for joints_position in self.joints:
            self.assertIsNone(self.niryo_robot.move(joints_position))
            self.assertAlmostEqualJoints(self.niryo_robot.get_joints(), joints_position)

    def test_050_move_wrong_params(self):
        with self.assertRaises(TypeError):
            self.niryo_robot.move(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)
        with self.assertRaises(AttributeError):
            self.niryo_robot.move(self.joints[0].to_list())

    def test_060_joints_setter(self):
        for joints_position in self.joints:
            self.niryo_robot.joints = joints_position
            self.assertAlmostEqualJoints(self.niryo_robot.joints, joints_position)


class Test02Pose(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.poses_v1 = [
            PoseObject(0.2, 0, 0.3, 0, 0, 0, metadata=PoseMetadata.v1()),
            PoseObject(0.14, 0, 0.204, -0.017, 0.745, -0.001, metadata=PoseMetadata.v1()),
            PoseObject(0.135, 0.067, 0.514, -1.748, -0.746, 1.305, metadata=PoseMetadata.v1()),
            PoseObject(0.052, -0.22, 0.525, -0.378, 0.068, -1.394, metadata=PoseMetadata.v1()),
        ]
        cls.poses_v2 = [
            PoseObject(0.14, 0.0, 0.20, 3.11, -0.82, 0.04),
            PoseObject(0.14, 0.07, 0.50, 0.85, 0.07, 2.75),
            PoseObject(0.06, -0.21, 0.52, 1.70, -1.18, 0.09),
            PoseObject(0.14, 0.0, 0.20, 3.11, -0.83, 0.04),
        ]

    def test_010_get_pose(self):
        self.assertIsInstance(self.niryo_robot.get_pose(), PoseObject)
        self.assertIsInstance(self.niryo_robot.pose, PoseObject)
        self.assertAlmostEqualPose(self.niryo_robot.get_pose(), self.niryo_robot.pose)

    def test_020_get_pose_v2(self):
        self.assertIsInstance(self.niryo_robot.get_pose_v2(), PoseObject)
        self.assertEqual(self.niryo_robot.get_pose_v2().metadata.tcp_version, TcpVersion.DH_CONVENTION)
        self.assertIsInstance(self.niryo_robot.pose_v2, PoseObject)
        self.assertAlmostEqualPose(self.niryo_robot.get_pose_v2(), self.niryo_robot.pose_v2)

    def test_030_move_pose(self):
        for pose_v1 in self.poses_v1:
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.move_pose(pose_v1.to_list()))
            self.assertAlmostEqualPose(self.niryo_robot.get_pose(), pose_v1)

    def test_040_move_pose_wrong_params(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)
            self.niryo_robot.move_pose(self.poses_v2[0])

    def test_050_move(self):
        for pose in self.poses_v1:
            self.assertIsNone(self.niryo_robot.move(pose))
            self.assertAlmostEqualPose(self.niryo_robot.get_pose(), pose)
        for pose in self.poses_v2:
            self.assertIsNone(self.niryo_robot.move(pose))
            self.assertAlmostEqualPose(self.niryo_robot.get_pose_v2(), pose)

    def test_060_pose_setter(self):
        for pose_v1 in self.poses_v1:
            with self.assertWarnsDeprecated():
                self.niryo_robot.pose = pose_v1.to_list()
            self.assertAlmostEqualPose(self.niryo_robot.pose, pose_v1)

    def test_061_pose_setter_w_pose_object(self):
        for pose_v1 in self.poses_v1:
            with self.assertWarnsDeprecated():
                self.niryo_robot.pose = pose_v1
            self.assertAlmostEqualPose(self.niryo_robot.pose, pose_v1)

    def test_070_pose_v2_setter(self):
        for pose_v2 in self.poses_v2:
            self.niryo_robot.pose_v2 = pose_v2
            self.assertAlmostEqualPose(self.niryo_robot.pose_v2, pose_v2)

    def test_080_move_wrong_params(self):
        with self.assertRaises(TypeError):
            self.niryo_robot.move(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)
        with self.assertRaises(AttributeError):
            self.niryo_robot.move(self.poses_v1[0].to_list())

    def test_090_move_linear_pose(self):
        pose = PoseObject(0.2, 0, 0.4, 0, 0, 0, metadata=PoseMetadata.v1())
        self.niryo_robot.move(pose)
        for ix in range(3):
            pose[ix] += 0.05
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.move_linear_pose(pose))
            self.assertAlmostEqualPose(self.niryo_robot.get_pose(), pose)

    def test_100_move_linear_pose_wrong_params(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_linear_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)
            self.niryo_robot.move_linear_pose(self.poses_v2[0])

    def test_110_move_linear(self):
        pose = PoseObject(0.2, 0, 0.4, math.pi, -math.pi / 2, 0)
        self.niryo_robot.move(pose)
        for ix in range(3):
            pose[ix] += 0.05
            self.assertIsNone(self.niryo_robot.move(pose, linear=True))
            self.assertAlmostEqualPose(self.niryo_robot.get_pose_v2(), pose)

    def test_120_shift_pose(self):
        for axis in RobotAxis:
            self.assertIsNone(self.niryo_robot.shift_pose(axis, 0.05))

    def test_130_shift_linear_pose(self):
        for _ in range(10):
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.shift_linear_pose(RobotAxis.Z, 0.05))

    def test_140_shift_pose_linear(self):
        for _ in range(10):
            self.assertIsNone(self.niryo_robot.shift_pose(RobotAxis.Z, 0.05, linear=True))


class Test03Kinematics(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.joints = [
            JointsPosition(0.32, -0.01, -1.29, -2.09, 0.92, 0.01),
            JointsPosition(1.43, -0.12, 1.05, 1.26, 0.92, 0.01),
        ]
        cls.poses_v1 = [
            PoseObject(0.08, 0.070, 0.14, -0.31, 0.76, 2.19, metadata=PoseMetadata.v1()),
            PoseObject(0.06, 0.15, 0.62, 2.33, -0.68, 0.08, metadata=PoseMetadata.v1()),
        ]
        cls.poses_v2 = [
            PoseObject(0.08, 0.070, 0.14, 2.83, -0.76, 2.63),
            PoseObject(0.06, 0.15, 0.62, -0.73, 0.56, -0.96),
        ]

    def test_010_forward_kinematics(self):
        for joints_position, pose_v1 in zip(self.joints, self.poses_v1):
            self.assertAlmostEqualPose(self.niryo_robot.forward_kinematics(joints_position), pose_v1)

    def test_020_forward_kinematics_v2(self):
        for joints_position, pose_v2 in zip(self.joints, self.poses_v2):
            self.assertAlmostEqualPose(self.niryo_robot.forward_kinematics_v2(joints_position), pose_v2)

    def test_030_inverse_kinematics(self):
        for joints_position, pose_v1 in zip(self.joints, self.poses_v1):
            self.assertAlmostEqualJoints(self.niryo_robot.inverse_kinematics(pose_v1), joints_position)

    def test_031_inverse_kinematics_w_floats(self):
        for joints_position, pose_v1 in zip(self.joints, self.poses_v1):
            self.assertAlmostEqualJoints(self.niryo_robot.inverse_kinematics(*pose_v1), joints_position)

    def test_040_inverse_kinematics_v2(self):
        for joints_position, pose_v2 in zip(self.joints, self.poses_v2):
            self.assertAlmostEqualJoints(self.niryo_robot.inverse_kinematics_v2(pose_v2), joints_position)


class Test04Jog(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.n_joints = len(cls.niryo_robot.get_joints())

    def test_010_set_jog_control(self):
        self.assertIsNone(self.niryo_robot.set_jog_control(True))
        self.assertIsNone(self.niryo_robot.set_jog_control(False))

    def test_020_wrong_param(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_jog_control(-1)

    def test_030_context(self):
        with self.niryo_robot.jog_control():
            pass

    def test_040_jog_joints(self):
        jog_offset = [0] * self.n_joints
        with self.niryo_robot.jog_control():
            for joint_ix in range(self.n_joints):
                jog_offset[joint_ix] = 0.1
                with self.assertWarnsDeprecated():
                    self.assertIsNone(self.niryo_robot.jog_joints(jog_offset))

    def test_050_jog_pose(self):
        pose_offset = [0] * 6
        with self.niryo_robot.jog_control():
            for pose_ix in range(6):
                pose_offset[pose_ix] = 0.1
                with self.assertWarnsDeprecated():
                    self.assertIsNone(self.niryo_robot.jog_pose(pose_offset))

    def test_060_jog_w_joints_position(self):
        jog_offset = JointsPosition(*[0] * self.n_joints)
        with self.niryo_robot.jog_control():
            for joint_ix in range(self.n_joints):
                jog_offset[joint_ix] = 0.1
                self.assertIsNone(self.niryo_robot.jog(jog_offset))

    def test_070_jog_w_pose_object(self):
        pose_offset = PoseObject(0, 0, 0, 0, 0, 0)
        with self.niryo_robot.jog_control():
            for pose_ix in range(6):
                pose_offset[pose_ix] = 0.1
                self.assertIsNone(self.niryo_robot.jog(pose_offset))
