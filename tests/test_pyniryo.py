#!/usr/bin/env python

import numpy as np
import sys
import unittest
import time

from pyniryo import (NiryoRobot,
                     RobotAxis,
                     ConveyorID,
                     ToolID,
                     CalibrateMode,
                     TcpCommandException,
                     PinID,
                     PoseObject,
                     DigitalPinObject,
                     PinState,
                     PinMode,
                     AnalogPinObject,
                     ObjectShape,
                     ObjectColor,
                     NiryoRobotException,
                     PoseMetadata,
                     JointsPosition,
                     Command)

simulation = "-rpi" not in sys.argv
tool_used = ToolID.GRIPPER_2

robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_gazebo = "127.0.0.1"
robot_ip_address = "192.168.1.207" #robot_ip_address_gazebo if simulation else robot_ip_address_rpi


class BaseTestTcpApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.niryo_robot = NiryoRobot(robot_ip_address)

    def setUp(self):
        # clean the flag to not impact the following test if the previous one failed
        self.niryo_robot.clear_collision_detected()

    @classmethod
    def tearDownClass(cls):
        cls.niryo_robot.close_connection()

    @staticmethod
    def assertAlmostEqualVector(a, b, decimal=1):
        np.testing.assert_almost_equal(a, b, decimal)

    def assertAlmostEqualPose(self, a, b, decimal=1):
        """
        Ensure the poses are compatible, then convert the euler angles to quaternions
        """
        if isinstance(a, list):
            a = PoseObject(*a, metadata=PoseMetadata.v1())
        if isinstance(b, list):
            b = PoseObject(*b, metadata=PoseMetadata.v1())
        self.assertEqual(a.metadata.tcp_version,
                         b.metadata.tcp_version,
                         "Can't compare two poses with different TCP versions")

        a_quaternion = [a.x, a.y, a.z] + a.quaternion()
        b_quaternion = [b.x, b.y, b.z] + b.quaternion()

        self.assertAlmostEqualVector(a_quaternion, b_quaternion, decimal)


# noinspection PyTypeChecker
class TestMainPurpose(BaseTestTcpApi):

    def test_calibration(self):
        self.assertIsNone(self.niryo_robot.calibrate(CalibrateMode.AUTO))
        self.assertIsNone(self.niryo_robot.calibrate_auto())
        self.assertIsNone(self.niryo_robot.calibrate(CalibrateMode.MANUAL))
        self.assertFalse(self.niryo_robot.need_calibration())
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(PinID)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(ConveyorID.ID_1)

    def test_learning_mode(self):

        def setter_learning_mode(state):
            self.niryo_robot.learning_mode = state

        base_state = self.niryo_robot.learning_mode

        self.assertIsNone(self.niryo_robot.set_learning_mode(False))
        self.assertFalse(self.niryo_robot.learning_mode)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_learning_mode(PinID)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.learning_mode = 1
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_learning_mode(ConveyorID.ID_1)
        self.assertIsNone(setter_learning_mode(True))
        self.assertTrue(self.niryo_robot.learning_mode)

        self.niryo_robot.learning_mode = base_state

    def test_set_arm_velocity(self):
        self.assertIsNone(self.niryo_robot.set_arm_max_velocity(1))
        self.assertIsNone(self.niryo_robot.set_arm_max_velocity(100))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_arm_max_velocity(-95))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_arm_max_velocity(0))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_arm_max_velocity(101))

    def test_set_jog_control(self):
        self.assertIsNone(self.niryo_robot.set_jog_control(True))
        self.assertIsNone(self.niryo_robot.set_jog_control(False))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_jog_control(-1))

# noinspection PyTypeChecker
class TestJointsPoseFunctions(BaseTestTcpApi):
    # TODO : Add limits tests for joints && poses
    def test_joints(self):

        def setter_joints(joints):
            self.niryo_robot.joints = joints

        # Classic Move Joints & Get Joints
        self.assertIsNone(self.niryo_robot.move_joints(0.1, -0.1, 0.0, 0.0, 0.0, 0.0))
        self.assertAlmostEqualVector(self.niryo_robot.joints, [0.1, -0.1, 0.0, 0.0, 0.0, 0.0])
        self.assertIsNone(setter_joints([0, 0, 0, 0, 0, 0]))
        self.assertAlmostEqualVector(self.niryo_robot.get_joints(), 6 * [0.0])
        # Jog
        self.assertIsNone(self.niryo_robot.jog_joints(0.1, -0.1, 0, 0, 0, 0))
        self.niryo_robot.wait(0.75)
        self.niryo_robot.set_jog_control(False)
        self.assertAlmostEqualVector(self.niryo_robot.get_joints(), [0.1, -0.1, 0.0, 0.0, 0.0, 0.0])
        # Check Exception
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_joints(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)

    def test_pose(self):

        def setter_pose(pose):
            self.niryo_robot.pose = pose

        # Classic Move Pose & Get Pose
        self.assertIsNone(self.niryo_robot.move_pose(0.15, 0.0, 0.25, 0.0, 0.0, 0.0))
        self.assertIsNone(self.niryo_robot.move_pose([0.2, 0, 0.25, 0.0, 0.0, 0.0]))
        self.assertIsNone(setter_pose(PoseObject(0.156, 0.09, 0.34, 0.307, -0.148, 0.755, metadata=PoseMetadata.v1())))
        expected_pose = PoseObject(0.156, 0.09, 0.34, -1.11, -1.23, -1.25)
        self.assertAlmostEqualPose(self.niryo_robot.get_pose(), expected_pose)
        self.assertAlmostEqualPose(self.niryo_robot.pose, expected_pose)
        # Linear Move Pose
        self.assertIsNone(self.niryo_robot.move_linear_pose(0.15, 0.09, 0.22, 0.31, -0.15, 0.75))
        target_pose = PoseObject(0.2, 0.09, 0.22, -1.11, -1.23, -1.25)
        self.assertIsNone(self.niryo_robot.move(target_pose, move_cmd=Command.MOVE_LINEAR_POSE))
        self.assertAlmostEqualPose(self.niryo_robot.get_pose(), target_pose)
        # Shift axis & Jog
        self.assertIsNone(self.niryo_robot.shift_pose(RobotAxis.Y, 0.05))
        self.assertIsNone(self.niryo_robot.jog_pose(-0.02, 0.0, 0.02, 0.1, 0, 0))
        self.niryo_robot.set_jog_control(False)
        # Shift axis linear
        self.assertIsNone(self.niryo_robot.shift_linear_pose(RobotAxis.Y, 0.05))
        # Check Exceptions
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.shift_pose(ToolID.ELECTROMAGNET_1, 0.05)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_linear_pose(0.54, 0.964, 0.7, "a", "m", 1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.shift_linear_pose(ConveyorID.ID_1, 0.9)

    def test_move(self):
        test_positions = [
            PoseObject(0.2, 0, 0.3, 0, 0, 0, metadata=PoseMetadata.v1()),
            PoseObject(0.14, 0, 0.204, -0.017, 0.745, -0.001, metadata=PoseMetadata.v1()),
            PoseObject(0.135, 0.067, 0.514, -1.748, -0.746, 1.305, metadata=PoseMetadata.v1()),
            PoseObject(0.052, -0.22, 0.525, -0.378, 0.068, -1.394, metadata=PoseMetadata.v1()),
            PoseObject(0.14, 0, 0.203, 0.005, 0.747, 0.001, metadata=PoseMetadata.v1()),
            PoseObject(0.14006130314993392,
                       6.048173041991534e-06,
                       0.20401713144974865,
                       3.110362076103925,
                       -0.8266489340816215,
                       0.037467558750953124),
            PoseObject(0.1432125589005656,
                       0.06831283301679453,
                       0.5002248793857345,
                       0.8520537601093433,
                       0.07059014583057896,
                       2.7549475859358963),
            PoseObject(0.06091218004601295,
                       -0.21754547980629296,
                       0.5256674137051471,
                       1.70125249680832,
                       -1.1864220377733763,
                       0.09318154272294449),
            PoseObject(0.14006130314993392,
                       6.048173041991534e-06,
                       0.20401713144974865,
                       3.110362076103925,
                       -0.8266489340816215,
                       0.037467558750953124),
            JointsPosition(0, 0, 0, 0, 0, 0),
            JointsPosition(0.1, -0.1, 0.0, 0.0, 0.0, 0.0),
            JointsPosition(0, 0.5, -1.25, 0, 0, 0),
            JointsPosition(-1, 0.5, -0.6, 0.8, 1.2, -1.4),
            JointsPosition(0, 0.5, -1.25, 0, 0, 0),
        ]

        for test_position in test_positions:
            self.niryo_robot.move(test_position)
            if isinstance(test_position, JointsPosition):
                self.assertAlmostEqualVector(self.niryo_robot.joints.to_list(), test_position.to_list())
            elif test_position.metadata.tcp_version == self.niryo_robot.pose.metadata.tcp_version:
                # can't compare poses with different conventions
                self.assertAlmostEqualPose(self.niryo_robot.pose, test_position)

            self.assertFalse(self.niryo_robot.collision_detected)

    def test_kinematics(self):
        initial_pose = self.niryo_robot.get_pose()
        # Forward Kinematics
        joints_target = 0.2, 0.0, -0.4, 0.0, 0.0, 0.0
        pose_target = self.niryo_robot.forward_kinematics(joints_target)
        pose_target_2 = self.niryo_robot.forward_kinematics(JointsPosition(*joints_target))
        self.assertAlmostEqualPose(pose_target, pose_target_2)
        self.assertIsNone(self.niryo_robot.move(pose_target))
        joints_reached = self.niryo_robot.get_joints()
        self.assertAlmostEqualVector(joints_target, joints_reached)
        # Inverse Kinematics
        joints_target_to_initial_pose = self.niryo_robot.inverse_kinematics(initial_pose)
        self.assertIsNone(self.niryo_robot.move_joints(joints_target_to_initial_pose))
        pose_reached = self.niryo_robot.get_pose()
        self.assertAlmostEqualPose(initial_pose, pose_reached)


class TestSavedPose(BaseTestTcpApi):
    # TODO : Check for non-reachable saved pose ?

    def test_creation_delete_pos(self):
        # Get saved pose list & copy it
        base_list = self.niryo_robot.get_saved_pose_list()
        new_list = [v for v in base_list]

        # Create new poses
        list_names_saved = []
        for i in range(3):
            new_name = 'test_{:03d}'.format(i)
            if i == 0:
                self.assertIsNone(self.niryo_robot.save_pose(new_name, [0.2, 0.0, 0.3, 0.0, 0.0, 0.0]))
            elif i == 1:
                self.assertIsNone(self.niryo_robot.save_pose(new_name, 0.2, 0.0, 0.3, 0.0, 0.0, 0.0))
            else:
                self.assertIsNone(
                    self.niryo_robot.save_pose(new_name,
                                               PoseObject(0.2, 0.0, 0.3, 0.0, 0.0, 0.0, metadata=PoseMetadata.v1())))
            if new_name not in new_list:
                new_list.append(new_name)
                list_names_saved.append(new_name)
            self.assertEqual(self.niryo_robot.get_saved_pose_list(), new_list)

        # Delete created poses
        for name in list_names_saved:
            saved_pose = self.niryo_robot.get_pose_saved(name)
            self.assertListEqual(saved_pose.to_list(), [0.2, 0.0, 0.3, 0.0, 0.0, 0.0])
            self.assertIsNone(self.niryo_robot.delete_pose(name))
            new_list.pop(new_list.index(name))
            self.assertEqual(self.niryo_robot.get_saved_pose_list(), new_list)

    def test_execute_pose_saved(self):
        pose_name = "test_pose_save_and_execute"
        pose_target = PoseObject(0.2, 0, 0.3, 0, -1.56, 3.14)
        # Saving pose
        self.assertIsNone(self.niryo_robot.save_pose(pose_name, pose_target))

        # Recovering pose
        pose_recup = self.niryo_robot.get_pose_saved(pose_name)
        self.assertAlmostEqualPose(pose_target, pose_recup)

        # Moving to the pose
        self.assertIsNone(self.niryo_robot.move(pose_recup))

        # Deleting the pose
        self.assertIsNone(self.niryo_robot.delete_pose(pose_name))


# noinspection PyTypeChecker
class TestPickPlaceFunction(BaseTestTcpApi):
    pose_1 = [0.2, 0.1, 0.1, 0., 1.57, 0.]
    pose_2 = [0.2, -0.1, 0.1, 0., 1.57, 0.]

    def test_pick_n_place_individually(self):
        self.assertIsNone(self.niryo_robot.pick_from_pose(PoseObject(*self.pose_1, metadata=PoseMetadata.v1())))
        self.assertIsNone(self.niryo_robot.place_from_pose(*self.pose_2))

        self.assertIsNone(self.niryo_robot.pick(PoseObject(*self.pose_1, metadata=PoseMetadata.v1())))
        self.assertIsNone(self.niryo_robot.place(PoseObject(*self.pose_2, metadata=PoseMetadata.v1())))
        # Testing random values
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.pick_from_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)

    def test_pick_n_place_in_one(self):
        self.assertIsNone(
            self.niryo_robot.pick_and_place(PoseObject(*self.pose_1, metadata=PoseMetadata.v1()), self.pose_2))


class TestTrajectoryMethods(BaseTestTcpApi):
    joints_list = [[-0.493, -0.32, -0.505, -0.814, -0.282, 0], [0.834, -0.319, -0.466, 0.822, -0.275, 0],
                   [1.037, -0.081, 0.248, 1.259, -0.276, 0]]

    robot_poses = [[0.25, 0.1, 0.25, 0., 0., 0., 1.], [0.25, -0.1, 0.25, 0., 0., 0., 1.],
                   [0.25, -0.1, 0.3, 0., 0., 0., 1.], [0.25, 0.1, 0.3, 0., 0., 0., 1.]]

    def test_last_learned_trajectory(self):
        for i in range(3):
            new_name = 'test_{:03d}'.format(i)
            new_description = 'test_description_{:03d}'.format(i)
            self.assertIsNone(self.niryo_robot.save_trajectory(self.joints_list, new_name, new_description))
        self.assertIsNone(self.niryo_robot.clean_trajectory_memory())
        result = self.niryo_robot.get_saved_trajectory_list()
        self.assertEqual(result, [])

        self.assertIsNone(self.niryo_robot.save_trajectory(self.joints_list, "last_executed_trajectory", ""))
        self.assertIsNone(self.niryo_robot.save_last_learned_trajectory("unittest_name", "unittest_description"))
        result = self.niryo_robot.get_saved_trajectory_list()
        self.assertEqual(result, ["unittest_name"])

    def test_creation_delete_trajectory(self):
        # Get saved trajectory list & copy it

        self.assertIsNone(self.niryo_robot.clean_trajectory_memory())
        result = self.niryo_robot.get_saved_trajectory_list()
        self.assertEqual(result, [])

        trajectories = [self.joints_list, [JointsPosition(*joints) for joints in self.joints_list]]
        for trajectory in trajectories:
            # Create new trajectory
            name = 'test_trajectory'
            description = 'test_description'
            self.assertIsNone(self.niryo_robot.save_trajectory(trajectory, name, description))
            result = self.niryo_robot.get_saved_trajectory_list()
            self.assertEqual(result, [name])

            # Update Trajectory
            new_name = 'test_update_pose'
            new_description = 'test_update_description'
            self.assertIsNone(self.niryo_robot.update_trajectory_infos(name, new_name, new_description))
            result = self.niryo_robot.get_saved_trajectory_list()
            self.assertEqual(result, [new_name])

            # Delete created trajectory
            self.assertIsNone(self.niryo_robot.delete_trajectory(new_name))
            result = self.niryo_robot.get_saved_trajectory_list()
            self.assertEqual(result, [])

    def test_execute_trajectory(self):
        robot_positions = []
        robot_positions += [JointsPosition(*joints) for joints in self.joints_list]
        robot_positions += [PoseObject(*pose[:6], metadata=PoseMetadata.v1()) for pose in self.robot_poses]
        self.assertIsNone(self.niryo_robot.execute_trajectory(robot_positions))

    def test_execute_trajectory_from_poses(self):
        # Testing trajectory from poses
        self.assertIsNone(self.niryo_robot.execute_trajectory_from_poses(self.robot_poses))

    def test_save_and_execute_trajectory(self):
        # Create & save a trajectory, then execute it & eventually delete it
        traj_name = "test_trajectory_save_and_execute"
        traj_description = "test_description_trajectory_save_and_execute"
        self.assertIsNone(self.niryo_robot.save_trajectory(self.joints_list, traj_name, traj_description))
        self.assertIsNone(self.niryo_robot.execute_registered_trajectory(traj_name))
        self.assertIsNone(self.niryo_robot.delete_trajectory(traj_name))


class TestDynamicFrame(BaseTestTcpApi):
    robot_poses = [
        [[0.2, 0.2, 0.1, 0, 0, 0], [0.4, 0.3, 0.1, 0, 0, 0], [0.3, 0.4, 0.1, 0, 0, 0]],
        [[-0.2, -0.2, 0.1, 0, 0, 0], [-0.4, -0.3, 0.1, 0, 0, 0], [-0.3, -0.4, 0.1, 0, 0, 0]],
    ]

    robot_point = [
        [[-0.2, 0.2, 0.1], [0.4, 0.3, 0], [0.3, 0.4, 0]],
        [[0.2, -0.2, 0.1], [-0.4, -0.3, 0], [-0.3, -0.4, 0]],
    ]

    def test_main_frame(self):
        self.__test_creation_edition_frame()
        self.__test_move_in_frame()
        self.__test_deletion()

    def __test_creation_edition_frame(self):
        base_list_name, base_list_desc = self.niryo_robot.get_saved_dynamic_frame_list()
        new_list_name = [frame for frame in base_list_name]

        # Create frame by pose
        list_saved = []
        for i in range(4):
            if i < 2:
                # Test creation by poses
                new_name = 'unitTestFramePose_{:03d}'.format(i)
                new_desc = 'descTestFramePose_{:03d}'.format(i)
                pose_o = self.robot_poses[i][0]
                pose_x = self.robot_poses[i][1]
                pose_y = self.robot_poses[i][2]
                self.assertIsNone(
                    self.niryo_robot.save_dynamic_frame_from_poses(new_name,
                                                                   new_desc,
                                                                   pose_o,
                                                                   PoseObject(*pose_x, metadata=PoseMetadata.v1()),
                                                                   PoseObject(*pose_y, metadata=PoseMetadata.v1())))

                # Test edition
                new_edit_name = 'unitEditTestFramePose_{:03d}'.format(i)
                new_edit_desc = 'descEditTestFramePose_{:03d}'.format(i)
                self.assertIsNone(self.niryo_robot.edit_dynamic_frame(new_name, new_edit_name, new_edit_desc))
                self.assertEqual(self.niryo_robot.get_saved_dynamic_frame(new_edit_name)[0], new_edit_name)

                with self.assertRaises(TcpCommandException):
                    self.niryo_robot.get_saved_dynamic_frame(0)

                if new_edit_name not in new_list_name:
                    new_list_name.append(new_edit_name)
                    list_saved.append(new_edit_name)

                new_list_name.sort()

                self.assertEqual(self.niryo_robot.get_saved_dynamic_frame_list()[0], new_list_name)

                with self.assertRaises(TcpCommandException):
                    self.niryo_robot.save_dynamic_frame_from_poses(0, "unittest", pose_o, pose_x, pose_y)

                with self.assertRaises(TcpCommandException):
                    self.niryo_robot.save_dynamic_frame_from_points(0, "unittest", pose_o, pose_x, pose_y)

                with self.assertRaises(TcpCommandException):
                    self.niryo_robot.edit_dynamic_frame("unitTestFramePose_000", 0, 0)

            else:
                # Test creation by points
                new_name = 'unitTestFramePose_{:03d}'.format(i)
                new_desc = 'descTestFramePose_{:03d}'.format(i)
                point_o = self.robot_point[2 - i][0]
                point_x = self.robot_point[2 - i][1]
                point_y = self.robot_point[2 - i][2]
                self.assertIsNone(
                    self.niryo_robot.save_dynamic_frame_from_points(new_name, new_desc, point_o, point_x, point_y))

                # Test edition
                new_edit_name = 'unitEditTestFramePose_{:03d}'.format(i)
                new_edit_desc = 'descEditTestFramePose_{:03d}'.format(i)
                self.assertIsNone(self.niryo_robot.edit_dynamic_frame(new_name, new_edit_name, new_edit_desc))
                self.assertEqual(self.niryo_robot.get_saved_dynamic_frame(new_edit_name)[0], new_edit_name)

                if new_edit_name not in new_list_name:
                    new_list_name.append(new_edit_name)
                    list_saved.append(new_edit_name)

                new_list_name.sort()

                self.assertEqual(self.niryo_robot.get_saved_dynamic_frame_list()[0], new_list_name)

    def __test_move_in_frame(self):
        # Move frame 000
        pose0 = (0, 0, 0, 0, 1.57, 0)
        self.assertIsNone(self.niryo_robot.move_pose(pose0, "unitEditTestFramePose_000"))
        self.assertIsNone(self.niryo_robot.move_linear_pose((0.05, 0.05, 0.05, 0, 1.57, 0),
                                                            "unitEditTestFramePose_000"))

        # Move frame 001
        pose1 = PoseObject(0, 0, 0, 0, 1.57, 0, metadata=PoseMetadata.v1())
        self.assertIsNone(self.niryo_robot.move_pose(pose1, "unitEditTestFramePose_001"))
        self.assertIsNone(self.niryo_robot.move_linear_pose((0.05, 0.05, 0.05, 0, 1.57, 0),
                                                            "unitEditTestFramePose_001"))

        # Move frame 002
        pose2 = (0, 0, 0, 0, 1.57, 0)
        self.assertIsNone(self.niryo_robot.move_pose(pose2, "unitEditTestFramePose_002"))
        self.assertIsNone(self.niryo_robot.move_relative([0.05, 0.05, 0.05, 0.1, 0.1, 0.1],
                                                         "unitEditTestFramePose_002"))
        self.assertIsNone(
            self.niryo_robot.move_linear_relative([-0.05, -0.05, -0.05, 0, 0, 0], "unitEditTestFramePose_002"))

        # Move frame 003
        pose3 = PoseObject(0, 0, 0, 0, 1.57, 0, metadata=PoseMetadata.v1())
        self.assertIsNone(self.niryo_robot.move_pose(pose3, "unitEditTestFramePose_003"))
        self.assertIsNone(self.niryo_robot.move_relative([0.05, 0.05, 0.05, 0.1, 0.1, 0.1],
                                                         "unitEditTestFramePose_003"))
        self.assertIsNone(
            self.niryo_robot.move_linear_relative([-0.05, -0.05, -0.05, 0, 0, 0], "unitEditTestFramePose_003"))

        # Test default world frame
        self.assertIsNone(self.niryo_robot.move_relative([0.1, 0.1, 0.1, 0, 0, 0]))
        self.assertIsNone(self.niryo_robot.move_linear_relative([0, 0, -0.1, 0, 0, 0]))

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_relative([0.05, 0.05, 0.05, 0.1, 0.1, 0.1], 0)

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_linear_relative([0.05, 0.05, 0.05, 0.1, 0.1, 0.1], 0)

    def __test_deletion(self):
        base_list = self.niryo_robot.get_saved_dynamic_frame_list()[0]
        new_list = [frame for frame in base_list]

        for i in range(4):
            name_delete = 'unitEditTestFramePose_{:03d}'.format(i)
            self.assertIsNone(self.niryo_robot.delete_dynamic_frame(name_delete))

            new_list.remove(name_delete)

            self.assertEqual(self.niryo_robot.get_saved_dynamic_frame_list()[0], new_list)


# noinspection PyTypeChecker
class TestTools(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        cls.niryo_robot = NiryoRobot(robot_ip_address)

    # noinspection PyTypeChecker
    def test_select(self):
        # Set tool used and check
        self.assertIsNone(self.niryo_robot.update_tool())
        # wait a bit to wait for the current tool to be updated
        time.sleep(1)

        self.assertEqual(tool_used, self.niryo_robot.tool)
        self.assertEqual(tool_used, self.niryo_robot.get_current_tool_id())
        self.assertNotEqual(self.niryo_robot.get_current_tool_id(), tool_used.value)
        self.assertNotEqual(self.niryo_robot.get_current_tool_id(), ToolID.NONE)

    def test_use_tool(self):
        # Equip tool
        self.assertIsNone(self.niryo_robot.update_tool())

        # Grasp/Release with ID
        self.assertIsNone(self.niryo_robot.grasp_with_tool())
        self.assertIsNone(self.niryo_robot.release_with_tool())

        # Grasp/Release without ID
        self.assertIsNone(self.niryo_robot.grasp_with_tool())
        self.assertIsNone(self.niryo_robot.release_with_tool())

        # Grippers specific functions
        if tool_used in [ToolID.GRIPPER_1, ToolID.GRIPPER_2, ToolID.GRIPPER_3]:
            self.assertIsNone(self.niryo_robot.close_gripper())
            self.assertIsNone(self.niryo_robot.open_gripper())
            self.assertIsNone(self.niryo_robot.open_gripper(speed=500))
            self.assertIsNone(self.niryo_robot.close_gripper(speed=500))
            self.assertIsNone(self.niryo_robot.open_gripper(max_torque_percentage=100, hold_torque_percentage=50))
            self.assertIsNone(self.niryo_robot.close_gripper(max_torque_percentage=100, hold_torque_percentage=50))

    def test_electromagnet(self):
        # Equip tool
        self.assertIsNone(self.niryo_robot.setup_electromagnet(PinID.GPIO_1A))
        self.assertIsNone(self.niryo_robot.setup_electromagnet("1B"))

        # Grasp/Release without ID
        self.assertIsNone(self.niryo_robot.grasp_with_tool())
        self.assertIsNone(self.niryo_robot.release_with_tool())

        # Grasp/Release with ID
        self.assertIsNone(self.niryo_robot.activate_electromagnet(PinID.GPIO_1B))
        self.assertIsNone(self.niryo_robot.deactivate_electromagnet("1B"))


# noinspection PyTypeChecker
class TestIOs(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        cls.niryo_robot = NiryoRobot(robot_ip_address)

    def test_digital_ios(self):
        self.assertIsInstance(self.niryo_robot.get_digital_io_state(), list)
        self.assertIsInstance(self.niryo_robot.get_digital_io_state()[0], DigitalPinObject)
        self.assertIsInstance(self.niryo_robot.get_digital_io_state()[0].pin_id, PinID)
        self.assertIsInstance(self.niryo_robot.get_digital_io_state()[0].name, str)
        self.assertIsInstance(self.niryo_robot.get_digital_io_state()[0].mode, PinMode)
        self.assertIsInstance(self.niryo_robot.get_digital_io_state()[0].state, PinState)

        for index, pin_object in enumerate(self.niryo_robot.get_digital_io_state()):
            if pin_object.name.startswith('DI'):
                continue

            if not (pin_object.name.startswith('SW') or pin_object.name.startswith('DO')):
                self.assertIsNone(self.niryo_robot.set_pin_mode(pin_object.name, PinMode.OUTPUT))
                self.niryo_robot.wait(1)

            self.assertEqual(self.niryo_robot.get_digital_io_state()[index].mode, PinMode.OUTPUT)

            self.assertIsNone(self.niryo_robot.digital_write(pin_object.pin_id, PinState.HIGH))
            self.assertEqual(self.niryo_robot.digital_read(pin_object.pin_id), PinState.HIGH)
            self.assertEqual(self.niryo_robot.get_digital_io_state()[index].state, PinState.HIGH)
            self.assertIsNone(self.niryo_robot.digital_write(pin_object.name, PinState.LOW))
            self.assertEqual(self.niryo_robot.digital_read(pin_object.name), PinState.LOW)
            self.assertEqual(self.niryo_robot.get_digital_io_state()[index].state, PinState.LOW)

            if not (pin_object.name.startswith('SW') or pin_object.name.startswith('DO')):
                self.assertIsNone(self.niryo_robot.set_pin_mode(pin_object.name, PinMode.INPUT))
                self.assertEqual(self.niryo_robot.get_digital_io_state()[index].mode, PinMode.INPUT)

                # with self.assertRaises(NiryoRobotException):
                #    self.niryo_robot.digital_write(pin, PinState.LOW)

    def test_analog_ios(self):
        self.assertIsInstance(self.niryo_robot.get_analog_io_state(), list)
        self.assertIsInstance(self.niryo_robot.get_analog_io_state()[0], AnalogPinObject)
        self.assertIsInstance(self.niryo_robot.get_analog_io_state()[0].pin_id, PinID)
        self.assertIsInstance(self.niryo_robot.get_analog_io_state()[0].name, str)
        self.assertIsInstance(self.niryo_robot.get_analog_io_state()[0].mode, PinMode)
        self.assertIsInstance(self.niryo_robot.get_analog_io_state()[0].value, (float, int))

        for index, pin_object in enumerate(self.niryo_robot.get_analog_io_state()):
            if pin_object.name.startswith('AI'):
                self.assertEqual(self.niryo_robot.get_analog_io_state()[index].mode, PinMode.INPUT)
            else:
                self.assertEqual(self.niryo_robot.get_analog_io_state()[index].mode, PinMode.OUTPUT)

                self.assertIsNone(self.niryo_robot.analog_write(pin_object.pin_id, 5.0))
                self.assertEqual(self.niryo_robot.analog_read(pin_object.pin_id), 5.0)
                self.assertEqual(self.niryo_robot.get_analog_io_state()[index].value, 5.0)

                self.assertIsNone(self.niryo_robot.analog_write(pin_object.pin_id, 2.5))
                self.assertEqual(self.niryo_robot.analog_read(pin_object.pin_id), 2.5)
                self.assertEqual(self.niryo_robot.get_analog_io_state()[index].value, 2.5)

                self.assertIsNone(self.niryo_robot.analog_write(pin_object.pin_id, 0))
                self.assertEqual(self.niryo_robot.analog_read(pin_object.pin_id), 0)
                self.assertEqual(self.niryo_robot.get_analog_io_state()[index].value, 0)

    def test_button(self):
        self.assertIsInstance(self.niryo_robot.get_custom_button_state(), str)


class TestVision(BaseTestTcpApi):
    workspace_name = "workspace_vision_test"
    point_1 = [0.120, -0.085, 0]
    point_2 = [0.120, 0.085, 0]
    point_3 = [0.205, 0.085, 0]
    point_4 = [0.205, -0.085, 0]
    observation_pose = JointsPosition(0, 0.3, -0.8, 0, -1.35, 0)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.niryo_robot.update_tool()
        cls.niryo_robot.save_workspace_from_points(cls.workspace_name,
                                                   cls.point_1,
                                                   cls.point_2,
                                                   cls.point_3,
                                                   cls.point_4)

    @classmethod
    def tearDownClass(cls):
        cls.niryo_robot.delete_workspace(cls.workspace_name)
        super().tearDownClass()

    def test_get_data(self):
        self.assertIsNotNone(self.niryo_robot.get_img_compressed())
        self.assertIsNotNone(self.niryo_robot.get_camera_intrinsics())

    def test_get_target_pose(self):
        self.niryo_robot.move(self.observation_pose)

        object_found, object_rel_pose, shape_a, color_a = self.niryo_robot.detect_object(self.workspace_name,
                                                                                         ObjectShape.ANY,
                                                                                         ObjectColor.ANY)
        self.assertTrue(object_found, 'No object found')
        self.assertEqual(len(object_rel_pose), 3)

        target_pose_a = self.niryo_robot.get_target_pose_from_rel(self.workspace_name, 0.1, *object_rel_pose)

        object_found, target_pose_b, shape_b, color_b = self.niryo_robot.get_target_pose_from_cam(self.workspace_name,
                                                                                                  0.1,
                                                                                                  ObjectShape.ANY,
                                                                                                  ObjectColor.ANY)
        self.assertTrue(object_found, 'No object found')

        # Can't compare the poses because the vision isn't precise enough
        # self.assertAlmostEqualPose(target_pose_a, target_pose_b)
        self.assertEqual(shape_a, shape_b)
        self.assertEqual(color_a, color_b)

    def test_vision_move(self):
        # Test to move to the object
        self.assertIsNotNone(self.niryo_robot.move_to_object(self.workspace_name, 0, ObjectShape.ANY, ObjectColor.ANY))
        # Going back to observation pose
        self.assertIsNone(self.niryo_robot.move(self.observation_pose))
        # Vision Pick
        self.assertIsNotNone(self.niryo_robot.vision_pick(self.workspace_name, 0, ObjectShape.ANY, ObjectColor.ANY))

    def test_pick(self):
        self.assertIsNone(self.niryo_robot.move(self.observation_pose))
        object_found, _, _, _ = self.niryo_robot.detect_object(self.workspace_name, ObjectShape.ANY, ObjectColor.ANY)
        self.assertTrue(object_found, 'No object found')

        # Vision Pick
        self.assertIsNotNone(self.niryo_robot.vision_pick(self.workspace_name, 0, ObjectShape.ANY, ObjectColor.ANY))

        self.assertIsNone(self.niryo_robot.move(self.observation_pose))
        object_found, _, _, _ = self.niryo_robot.detect_object(self.workspace_name, ObjectShape.ANY, ObjectColor.ANY)
        self.assertFalse(object_found, 'The object has not been picked')


class TestWorkspaceMethods(BaseTestTcpApi):
    robot_poses = [[0.3, 0.1, 0.1, 0., 1.57, 0.], [0.3, -0.1, 0.1, 0., 1.57, 0.], [0.1, -0.1, 0.1, 0., 1.57, 0.],
                   [0.1, 0.1, 0.1, 0., 1.57, 0.]]
    points = [[p[0], p[1], p[2] + 0.05] for p in robot_poses]
    robot_poses_obj = [PoseObject(*pose, metadata=PoseMetadata.v1()) for pose in robot_poses]

    def test_creation_delete_workspace(self):
        # Get saved workspace list & copy it
        base_list = self.niryo_robot.get_workspace_list()
        new_list = [v for v in base_list]

        # Create new trajectories
        list_names_saved = []
        for i in range(6):
            new_name = 'test_{:03d}'.format(i)
            if i < 2:
                self.assertIsNone(self.niryo_robot.save_workspace_from_robot_poses(new_name, *self.robot_poses_obj))
            elif i < 4:
                self.assertIsNone(self.niryo_robot.save_workspace_from_robot_poses(new_name, *self.robot_poses))
            else:
                self.assertIsNone(self.niryo_robot.save_workspace_from_points(new_name, *self.points))

            # Checking ratio
            self.assertAlmostEqual(self.niryo_robot.get_workspace_ratio(new_name), 1.0, places=2)

            if new_name not in new_list:
                new_list.append(new_name)
                list_names_saved.append(new_name)
            # Checking workspace has been appended to the list
            self.assertEqual(self.niryo_robot.get_workspace_list(), new_list)

        # Delete created workspaces
        for name in list_names_saved:
            self.assertIsNone(self.niryo_robot.delete_workspace(name))
            new_list.pop(new_list.index(name))
            self.assertEqual(self.niryo_robot.get_workspace_list(), new_list)


class TestSound(BaseTestTcpApi):

    def test_sons(self):
        self.assertIsNotNone(self.niryo_robot.get_sounds())
        self.assertIsInstance(self.niryo_robot.get_sounds(), list)

        sound_name = self.niryo_robot.get_sounds()[0]

        self.assertGreater(self.niryo_robot.get_sound_duration(sound_name), 0)
        sound_duration = self.niryo_robot.get_sound_duration(sound_name)

        self.assertIsNone(self.niryo_robot.set_volume(200))
        self.assertIsNone(self.niryo_robot.set_volume(100))

        self.assertIsNone(self.niryo_robot.play_sound(sound_name, True, 0.1, sound_duration - 0.1))

        self.assertIsNone(self.niryo_robot.play_sound(sound_name, False))
        self.niryo_robot.wait(0.1)
        self.assertIsNone(self.niryo_robot.stop_sound())
        self.assertIsNone(self.niryo_robot.stop_sound())

        self.assertIsNone(self.niryo_robot.say("Test", 0))

        sound_list = self.niryo_robot.get_sounds()
        sound_name_test = "unittest.mp3"
        while sound_name_test + ".mp3" in sound_list:
            sound_name_test += "0"
        sound_name_test += ".mp3"

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.get_sound_duration(sound_name_test)

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.play_sound(sound_name_test, True)

        with self.assertRaises(NiryoRobotException):
            self.niryo_robot.say("Test", -1)

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_volume(-100)

        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_volume(201)


class TestLedRing(BaseTestTcpApi):

    N_LEDS = 30

    CYAN = [0, 255, 255]
    MAGENTA = [255, 0, 255]
    YELLOW = [255, 255, 0]

    def __init__(self, *args, **kwargs):
        self.BLUE_TO_RED_GRADIENT = [[255 * (i / self.N_LEDS), 0, 255 - (255 * i / self.N_LEDS)]
                                     for i in range(self.N_LEDS)]
        super().__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        # The robot status takes some time before changing its status to running autonomous. This will cause the client
        # to crash if the 1st command is a led ring command, because the status must be to autonomous in order to
        # change the led ring. This is a quick and dirty fix to this problem
        time.sleep(0.5)

    def assertBlocking(self, fn, period, iterations, fn_kwargs=None):
        """
        Run an animation function and ensure it blocks until the animation is complete.
        """
        if fn_kwargs is None:
            fn_kwargs = {}
        start_time = time.time()
        self.assertIsNotNone(fn(**fn_kwargs, period=period, iterations=iterations, wait=True))
        elapsed_time = time.time() - start_time
        self.assertGreaterEqual(elapsed_time, period * iterations)

    def test_each_led(self):
        for i, color in enumerate(self.BLUE_TO_RED_GRADIENT):
            self.niryo_robot.set_led_color(i, color)

    def test_set_color(self):
        self.assertIsNotNone(self.niryo_robot.set_led_color(1, self.CYAN))
        self.assertIsNotNone(self.niryo_robot.led_ring_solid(self.MAGENTA))
        self.assertIsNotNone(self.niryo_robot.led_ring_custom(led_colors=self.BLUE_TO_RED_GRADIENT))
        self.assertIsNotNone(self.niryo_robot.led_ring_turn_off())

    def test_animations(self):

        self.assertBlocking(self.niryo_robot.led_ring_flashing,
                            period=0.5,
                            iterations=5,
                            fn_kwargs={'color': self.YELLOW})

        self.assertBlocking(self.niryo_robot.led_ring_alternate,
                            period=0.5,
                            iterations=4,
                            fn_kwargs={'color_list': [self.CYAN, self.MAGENTA]})

        self.assertBlocking(self.niryo_robot.led_ring_chase, period=1, iterations=2, fn_kwargs={'color': self.YELLOW})
        self.assertBlocking(self.niryo_robot.led_ring_go_up, period=0.5, iterations=4, fn_kwargs={'color': self.CYAN})
        self.assertBlocking(self.niryo_robot.led_ring_go_up_down,
                            period=0.5,
                            iterations=4,
                            fn_kwargs={'color': self.MAGENTA})
        self.assertBlocking(self.niryo_robot.led_ring_breath, period=2, iterations=2, fn_kwargs={'color': self.YELLOW})
        self.assertBlocking(self.niryo_robot.led_ring_snake, period=0.5, iterations=4, fn_kwargs={'color': self.CYAN})

    def test_rainbow(self):
        self.assertBlocking(self.niryo_robot.led_ring_rainbow, period=3, iterations=2)
        self.assertBlocking(self.niryo_robot.led_ring_rainbow_cycle, period=3, iterations=2)
        self.assertBlocking(self.niryo_robot.led_ring_rainbow_chase, period=5, iterations=1)


if __name__ == '__main__':
    unittest.main()
