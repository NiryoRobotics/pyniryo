#!/usr/bin/env python

import numpy as np
import sys

import unittest

from pyniryo import *

simulation = "-rpi" not in sys.argv
tool_used = ToolID.GRIPPER_1

robot_ip_address_rpi = "192.168.1.202"
robot_ip_address_gazebo = "127.0.0.1"
robot_ip_address = robot_ip_address_gazebo if simulation else robot_ip_address_rpi


class BaseTestTcpApi(unittest.TestCase):
    def setUp(self):
        self.niryo_robot = NiryoRobot(robot_ip_address)

    def tearDown(self):
        self.niryo_robot.close_connection()

    @staticmethod
    def assertAlmostEqualVector(a, b, decimal=1):
        np.testing.assert_almost_equal(a, b, decimal)


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

    def test_others(self):
        self.assertIsNone(self.niryo_robot.set_arm_max_velocity(95))
        self.assertIsNone(self.niryo_robot.set_jog_control(False))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_arm_max_velocity(-95))
        with self.assertRaises(TcpCommandException):
            self.assertIsNone(self.niryo_robot.set_arm_max_velocity(0))
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_jog_control(ConveyorID.ID_1)


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
        self.assertIsNone(self.niryo_robot.move_pose([0.2, 0, 0.25, 0, 0, 0]))
        self.assertIsNone(setter_pose(PoseObject(0.2, 0, 0.3, 0, 0, 0)))
        self.assertAlmostEqualVector(self.niryo_robot.get_pose().to_list(), [0.2, 0.0, 0.3, 0.0, 0.0, 0.0])
        self.assertAlmostEqualVector(self.niryo_robot.pose.to_list(), [0.2, 0.0, 0.3, 0.0, 0.0, 0.0])
        # Shift axis & Jog
        self.assertIsNone(self.niryo_robot.shift_pose(RobotAxis.Y, 0.05))
        self.assertIsNone(self.niryo_robot.jog_pose(-0.02, 0.0, 0.02, 0.1, 0, 0))
        self.niryo_robot.set_jog_control(False)
        # Check Exceptions
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.shift_pose(ToolID.ELECTROMAGNET_1, 0.05)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.move_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)

    def test_kinematics(self):
        initial_pose = self.niryo_robot.get_pose()
        # Forward Kinematics
        joints_target = 0.2, 0.0, -0.4, 0.0, 0.0, 0.0
        pose_target = self.niryo_robot.forward_kinematics(joints_target)
        self.assertIsNone(self.niryo_robot.move_pose(pose_target))
        joints_reached = self.niryo_robot.get_joints()
        self.assertAlmostEqualVector(joints_target, joints_reached)
        # Inverse Kinematics
        joints_target_to_initial_pose = self.niryo_robot.inverse_kinematics(initial_pose)
        self.assertIsNone(self.niryo_robot.move_joints(joints_target_to_initial_pose))
        pose_reached = self.niryo_robot.get_pose()
        self.assertAlmostEqualVector(initial_pose.to_list(), pose_reached.to_list())


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
                self.assertIsNone(self.niryo_robot.save_pose(new_name, PoseObject(0.2, 0.0, 0.3, 0.0, 0.0, 0.0)))
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
        pose_target = [0.2, 0.0, 0.3, 0.0, 0.0, 0.0]
        # Saving pose
        self.assertIsNone(self.niryo_robot.save_pose(pose_name, pose_target))

        # Recovering pose
        pose_recup = self.niryo_robot.get_pose_saved(pose_name)
        self.assertEqual(pose_target, pose_recup.to_list())

        # Moving to the pose
        self.assertIsNone(self.niryo_robot.move_pose(pose_recup))
        self.assertAlmostEqualVector(pose_target, self.niryo_robot.get_pose().to_list())

        # Deleting the pose
        self.assertIsNone(self.niryo_robot.delete_pose(pose_name))


# noinspection PyTypeChecker
class TestPickPlaceFunction(BaseTestTcpApi):
    pose_1 = [0.2, 0.1, 0.1, 0., 1.57, 0.]
    pose_2 = [0.2, -0.1, 0.1, 0., 1.57, 0.]

    def setUp(self):
        super(TestPickPlaceFunction, self).setUp()
        self.niryo_robot.update_tool()

    def test_pick_n_place_individually(self):
        # Picking
        self.assertIsNone(self.niryo_robot.pick_from_pose(PoseObject(*self.pose_1)))
        # Placing
        self.assertIsNone(self.niryo_robot.place_from_pose(*self.pose_2))
        # Testing random values
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.pick_from_pose(0.54, 0.964, 0.34, "a", "m", ConveyorID.ID_1)

    def test_pick_n_place_in_one(self):
        self.assertIsNone(self.niryo_robot.pick_and_place(PoseObject(*self.pose_2), self.pose_1))


class TestTrajectoryMethods(BaseTestTcpApi):
    robot_poses = [[0.3, 0.1, 0.15, 0., 0., 0., 1.],
                   [0.3, -0.1, 0.15, 0., 0., 0., 1.],
                   [0.3, -0.1, 0.1, 0., 0., 0., 1.],
                   [0.3, 0.1, 0.1, 0., 0., 0., 1.]]

    def test_creation_delete_trajectory(self):
        # Get saved trajectory list & copy it
        base_list = self.niryo_robot.get_saved_trajectory_list()
        new_list = [v for v in base_list]

        # Create new trajectories
        list_names_saved = []
        for i in range(3):
            new_name = 'test_{:03d}'.format(i)
            self.assertIsNone(self.niryo_robot.save_trajectory(new_name, self.robot_poses))
            if new_name not in new_list:
                new_list.append(new_name)
                list_names_saved.append(new_name)
            self.assertEqual(self.niryo_robot.get_saved_trajectory_list(), new_list)

        # Delete created trajectories
        for name in list_names_saved:
            self.assertIsNone(self.niryo_robot.delete_trajectory(name))
            new_list.pop(new_list.index(name))
            self.assertEqual(self.niryo_robot.get_saved_trajectory_list(), new_list)

    def test_execute_trajectory(self):
        # Testing trajectory from poses
        self.assertIsNone(self.niryo_robot.execute_trajectory_from_poses(self.robot_poses))

        # Create & save a trajectory, then execute it & eventually delete it
        traj_name = "test_trajectory_save_and_execute"
        self.assertIsNone(self.niryo_robot.save_trajectory(traj_name, self.robot_poses))
        self.assertIsNone(self.niryo_robot.execute_trajectory_saved(traj_name))
        self.assertIsNone(self.niryo_robot.delete_trajectory(traj_name))


class TestTools(BaseTestTcpApi):
    # noinspection PyTypeChecker
    def test_select(self):
        # Set tool used and check
        self.assertIsNone(self.niryo_robot.update_tool())
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


@unittest.skipIf(simulation, "Hardware is not available in simulation")
class TestHardware(BaseTestTcpApi):
    list_pins = [PinID.GPIO_1A, PinID.GPIO_1B, PinID.GPIO_1C, PinID.GPIO_2A, PinID.GPIO_2B,
                 PinID.GPIO_2C]

    def test_hardware(self):
        for pin in self.list_pins:
            self.assertIsNone(self.niryo_robot.set_pin_mode(pin, PinMode.OUTPUT))
            self.assertIsNone(self.niryo_robot.digital_write(pin, PinState.LOW))
            self.assertEqual(self.niryo_robot.digital_read(pin), PinState.LOW)
            self.assertIsNone(self.niryo_robot.digital_write(pin, PinState.HIGH))
            self.assertEqual(self.niryo_robot.digital_read(pin), PinState.HIGH)

            self.assertIsNone(self.niryo_robot.set_pin_mode(pin, PinMode.INPUT))
            with self.assertRaises(NiryoRobotException):
                self.niryo_robot.digital_write(pin, PinState.LOW)


@unittest.skipUnless(simulation, "Vision test is only coded for Gazebo")
class TestVision(BaseTestTcpApi):
    workspace_name = "gazebo_1"
    workspace_h = 0.001
    point_1 = [0.3369, 0.087, workspace_h]
    point_2 = [point_1[0], -point_1[1], workspace_h]
    point_3 = [0.163, -point_1[1], workspace_h]
    point_4 = [point_3[0], point_1[1], workspace_h]

    def setUp(self):
        super(TestVision, self).setUp()
        self.assertIsNone(self.niryo_robot.move_joints(0.0, 0.0, 0.0, 0.0, -1.57, 0.0))
        self.assertIsNone(self.niryo_robot.update_tool())
        self.assertIsNone(self.niryo_robot.save_workspace_from_points(
            self.workspace_name, self.point_1, self.point_2, self.point_3, self.point_4))

    def tearDown(self):
        self.assertIsNone(self.niryo_robot.delete_workspace(self.workspace_name))
        super(TestVision, self).tearDown()

    def test_vision_detect(self):
        # Getting img compressed & calibration object
        self.assertIsNotNone(self.niryo_robot.get_img_compressed())
        self.assertIsNotNone(self.niryo_robot.get_camera_intrinsics())

        # Getting target pose's from multiple ways
        self.assertIsNotNone(self.niryo_robot.get_target_pose_from_rel(
            self.workspace_name, 0.1, 0.5, 0.5, 0.0))

        self.assertIsNotNone(self.niryo_robot.get_target_pose_from_cam(
            self.workspace_name, 0.1, ObjectShape.ANY, ObjectColor.ANY))

        self.assertIsNotNone(self.niryo_robot.detect_object(self.workspace_name, ObjectShape.ANY, ObjectColor.RED))

    def test_vision_move(self):
        # Test to move to the object
        self.assertIsNotNone(self.niryo_robot.move_to_object(self.workspace_name, 0.1,
                                                             ObjectShape.ANY, ObjectColor.GREEN))
        # Going back to observation pose
        self.assertIsNone(self.niryo_robot.move_joints(0.0, 0.0, 0.0, 0.0, -1.57, 0.0))
        # Vision Pick
        self.assertIsNotNone(self.niryo_robot.vision_pick(self.workspace_name, 0.1,
                                                          ObjectShape.ANY, ObjectColor.BLUE))


class TestWorkspaceMethods(BaseTestTcpApi):
    robot_poses = [[0.3, 0.1, 0.1, 0., 1.57, 0.],
                   [0.3, -0.1, 0.1, 0., 1.57, 0.],
                   [0.1, -0.1, 0.1, 0., 1.57, 0.],
                   [0.1, 0.1, 0.1, 0., 1.57, 0.]]
    points = [[p[0], p[1], p[2] + 0.05] for p in robot_poses]
    robot_poses_obj = [PoseObject(*pose) for pose in robot_poses]

    def test_creation_delete_workspace(self):
        # Get saved workspace list & copy it
        base_list = self.niryo_robot.get_workspace_list()
        new_list = [v for v in base_list]

        # Create new trajectories
        list_names_saved = []
        for i in range(6):
            new_name = 'test_{:03d}'.format(i)
            if i < 2:
                self.assertIsNone(self.niryo_robot.save_workspace_from_robot_poses(new_name,
                                                                                   *self.robot_poses_obj))
            elif i < 4:
                self.assertIsNone(self.niryo_robot.save_workspace_from_robot_poses(new_name,
                                                                                   *self.robot_poses))
            else:
                self.assertIsNone(self.niryo_robot.save_workspace_from_points(new_name, *self.points))

            # Checking ratio
            self.assertAlmostEquals(self.niryo_robot.get_workspace_ratio(new_name), 1.0, places=2)

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


if __name__ == '__main__':
    unittest.main()
