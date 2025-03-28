import math

from pyniryo import PoseObject, PoseMetadata, TcpCommandException, JointsPosition, NiryoRobotException

from src.base_test import BaseTestTcpApi


class Test01SavedPose(BaseTestTcpApi):
    # TODO : Check for non-reachable saved pose ?

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.poses = [[0.14, 0.00, 0.20, 0.00, 0.75, 0.00],
                     PoseObject(x=0.18, y=0.09, z=0.58, roll=-2.22, pitch=-0.88, yaw=1.35, metadata=PoseMetadata.v1()),
                     PoseObject(x=-0.05, y=-0.16, z=0.06, roll=2.24, pitch=-0.64, yaw=-1.94)]

        # the poses are converted to v2 when saved
        cls.poses_v2 = [
            PoseObject(x=0.14, y=0.00, z=0.20, roll=3.14, pitch=-0.82, yaw=0.00),
            PoseObject(x=0.18, y=0.09, z=0.58, roll=0.58, pitch=0.40, yaw=2.40),
            PoseObject(x=-0.05, y=-0.16, z=0.06, roll=2.24, pitch=-0.64, yaw=-1.94)
        ]

    def test_010_save_pose(self):
        for ix, pose in enumerate(self.poses):
            pose_name = f'test_pose_{ix}'
            self.assertIsNone(self.niryo_robot.save_pose(pose_name, pose))

    def test_020_get_pose_saved(self):
        for ix, pose in enumerate(self.poses_v2):
            pose_name = f'test_pose_{ix}'
            self.assertAlmostEqualPose(self.niryo_robot.get_pose_saved(pose_name), pose)

    def test_030_get_saved_pose_list(self):
        saved_poses = self.niryo_robot.get_saved_pose_list()
        expected_poses = [f'test_pose_{ix}' for ix in range(len(self.poses))]
        self.assertTrue(set(saved_poses).issuperset(expected_poses))

    def test_040_delete_pose(self):
        for ix in range(len(self.poses)):
            pose_name = f'test_pose_{ix}'
            self.assertIsNone(self.niryo_robot.delete_pose(pose_name))
            with self.assertRaises(NiryoRobotException):
                self.niryo_robot.get_pose_saved(pose_name)

    def test_050_get_saved_pose_list_empty(self):
        saved_poses = self.niryo_robot.get_saved_pose_list()
        unexpected_poses = [f'test_pose_{ix}' for ix in range(len(self.poses))]
        self.assertTrue(set(saved_poses).isdisjoint(unexpected_poses))


class Test02TrajectoryMethods(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.joints_trajectory = [JointsPosition(i / 10, 0.5, -1.25, 0, 0, 0) for i in range(-20, 20)]

        # Generate a trajectory of poses representing a circle on the YZ plane
        radius = 0.1
        n_points = 50
        start_angle = math.pi / 2
        end_angle = math.pi * 2.5
        angle_step = (end_angle - start_angle) / (n_points - 1)
        x_offset = 0.2
        z_offset = 0.25
        cls.poses_v1_trajectory = [
            PoseObject(x_offset,
                       math.cos(start_angle + i * angle_step) * radius,
                       math.sin(start_angle + i * angle_step) * radius + z_offset,
                       0,
                       0,
                       0,
                       metadata=PoseMetadata.v1()) for i in range(n_points)
        ]
        cls.poses_v2_trajectory = [
            PoseObject(x_offset,
                       math.cos(start_angle + i * angle_step) * radius,
                       math.sin(start_angle + i * angle_step) * radius + z_offset,
                       0,
                       -math.pi / 2,
                       math.pi) for i in range(n_points)
        ]

        cls.mix_trajectory = [[[0, 0, 0, 0, 0, 0], [0.2, 0.1, 0.3, 0, 0, math.pi / 2], [0.2, 0.2, 0.3, 0, 0, 0]],
                              ['joints', 'pose', 'pose']]

        cls.trajectories = [cls.joints_trajectory, cls.poses_v1_trajectory, cls.poses_v2_trajectory]

    def test_010_save_trajectory(self):
        for ix, trajectory in enumerate(self.trajectories):
            trajectory_name = f'test_trajectory_{ix}'
            self.assertIsNone(
                self.niryo_robot.save_trajectory(trajectory, trajectory_name, f'Description for {trajectory_name}'))

    def test_020_get_trajectory_saved(self):
        for ix, _ in enumerate(self.trajectories):
            trajectory_name = f'test_trajectory_{ix}'
            trajectory = self.niryo_robot.get_trajectory_saved(trajectory_name)
            self.assertIsInstance(trajectory, list)
            self.assertGreater(len(trajectory), 0)
            self.assertIsInstance(trajectory[0], JointsPosition)

    def test_030_get_saved_trajectory_list(self):
        saved_trajectories = self.niryo_robot.get_saved_trajectory_list()
        expected_trajectories = [f'test_trajectory_{ix}' for ix in range(len(self.trajectories))]
        self.assertTrue(set(saved_trajectories).issuperset(expected_trajectories))

    def test_040_update_trajectory_infos(self):
        for ix, _ in enumerate(self.trajectories):
            trajectory_name = f'test_trajectory_{ix}'
            new_name = f'test_trajectory_{ix}_updated'
            self.assertIsNone(
                self.niryo_robot.update_trajectory_infos(trajectory_name,
                                                         new_name,
                                                         f'Updated description for {trajectory_name}'))

    def test_050_delete_trajectory(self):
        for ix in range(len(self.trajectories)):
            trajectory_name = f'test_trajectory_{ix}_updated'
            self.assertIsNone(self.niryo_robot.delete_trajectory(trajectory_name))
            with self.assertRaises(NiryoRobotException):
                self.niryo_robot.get_trajectory_saved(trajectory_name)

    def test_060_get_saved_trajectory_list_empty(self):
        saved_trajectories = self.niryo_robot.get_saved_trajectory_list()
        unexpected_trajectories = [f'test_trajectory_{ix}_updated' for ix in range(len(self.trajectories))]
        self.assertTrue(set(saved_trajectories).isdisjoint(unexpected_trajectories))

    def test_070_execute_trajectory(self):
        for trajectory in self.trajectories:
            self.assertIsNone(self.niryo_robot.execute_trajectory(trajectory))

    def test_080_execute_trajectory_from_poses(self):
        with self.assertWarnsDeprecated():
            self.assertIsNone(
                self.niryo_robot.execute_trajectory_from_poses([list(p) for p in self.poses_v1_trajectory]))

    def test_090_execute_trajectory_from_poses_and_joints(self):
        with self.assertWarnsDeprecated():
            self.assertIsNone(
                self.niryo_robot.execute_trajectory_from_poses_and_joints(self.mix_trajectory[0],
                                                                          self.mix_trajectory[1]))

    def test_100_clean_trajectory_memory(self):
        self.assertIsNone(self.niryo_robot.clean_trajectory_memory())


class Test03DynamicFrame(BaseTestTcpApi):
    robot_point = [
        [[-0.2, 0.2, 0.1], [0.4, 0.3, 0], [0.3, 0.4, 0]],
        [[0.2, -0.2, 0.1], [-0.4, -0.3, 0], [-0.3, -0.4, 0]],
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass(needs_move=True)
        cls.poses_frames = [[
            PoseObject(0.2, 0.0, 0.1, 0, 0, 0), PoseObject(0.2, 0.1, 0.1, 0, 0, 0), PoseObject(0.2, 0.0, 0.2, 0, 0, 0)
        ]]
        cls.points_frames = [
            [[0.2, 0.0, 0.3], [0.2, 0.1, 0.3], [0.2, 0.4, 0.4]],
        ]

    def test_010_save_dynamic_frame_from_poses(self):
        for ix, poses in enumerate(self.poses_frames):
            frame_name = f'test_poses_frame_{ix}'
            frame_description = f'Description for {frame_name}'
            self.assertIsNone(self.niryo_robot.save_dynamic_frame_from_poses(frame_name, frame_description, *poses))

    def test_020_save_dynamic_frame_from_points(self):
        for ix, points in enumerate(self.points_frames):
            frame_name = f'test_points_frame_{ix}'
            frame_description = f'Description for {frame_name}'
            self.assertIsNone(self.niryo_robot.save_dynamic_frame_from_points(frame_name, frame_description, *points))

    def test_030_get_saved_dynamic_frame(self):
        for ix, poses in enumerate(self.poses_frames):
            for frame_name in [f'test_poses_frame_{ix}', f'test_points_frame_{ix}']:
                name, description, frame = self.niryo_robot.get_saved_dynamic_frame(frame_name)
                self.assertEqual(name, frame_name)
                self.assertEqual(description, f'Description for {frame_name}')
                self.assertIsInstance(frame, list)
                self.assertGreater(len(frame), 0)
                self.assertIsInstance(frame[0], float)

    def test_040_get_saved_dynamic_frame_list(self):
        names, _descriptions = self.niryo_robot.get_saved_dynamic_frame_list()
        expected_frames = [f'test_poses_frame_{ix}' for ix in range(len(self.poses_frames))]
        expected_frames += [f'test_points_frame_{ix}' for ix in range(len(self.points_frames))]
        self.assertTrue(set(names).issuperset(expected_frames))

    def test_050_move_relative(self):
        for ix, poses in enumerate(self.poses_frames):
            frame_name = f'test_poses_frame_{ix}'
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.move_relative([0, 0, 0, 0, 0, 0], frame_name))

    def test_060_move_linear_relative(self):
        for ix, poses in enumerate(self.poses_frames):
            frame_name = f'test_poses_frame_{ix}'
            with self.assertWarnsDeprecated():
                self.assertIsNone(self.niryo_robot.move_linear_relative([0, 0, 0, 0, 0, 0], frame_name))

    def test_070_move_in_frame(self):
        for ix, poses in enumerate(self.poses_frames):
            frame_name = f'test_poses_frame_{ix}'
            relative_pose = PoseObject(0, 0, 0, 0, 0, 0, metadata=PoseMetadata.v2(frame=frame_name))
            self.assertIsNone(self.niryo_robot.move(relative_pose))

    def test_080_edit_dynamic_frame(self):
        for ix, poses in enumerate(self.poses_frames):
            frame_name = f'test_poses_frame_{ix}'
            new_name = f'test_poses_frame_{ix}_updated'
            self.assertIsNone(
                self.niryo_robot.edit_dynamic_frame(frame_name, new_name, f'Description for {frame_name}_updated'))

    def test_090_delete_dynamic_frame(self):
        for ix in range(len(self.poses_frames)):
            for frame_name in [f'test_poses_frame_{ix}_updated', f'test_points_frame_{ix}']:
                self.assertIsNone(self.niryo_robot.delete_dynamic_frame(frame_name))
                with self.assertRaises(NiryoRobotException):
                    self.niryo_robot.get_saved_dynamic_frame(frame_name)

    def test_100_get_saved_dynamic_frame_list_empty(self):
        names, _descriptions = self.niryo_robot.get_saved_dynamic_frame_list()
        unexpected_frames = [f'test_poses_frame_{ix}' for ix in range(len(self.poses_frames))]
        unexpected_frames += [f'test_points_frame_{ix}' for ix in range(len(self.points_frames))]
        self.assertTrue(set(names).isdisjoint(unexpected_frames))


class Test04Workspaces(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        list_poses = [
            [0.3, 0.1, 0.1, 0., 1.57, 0.],
            [0.3, -0.1, 0.1, 0., 1.57, 0.],
            [0.1, -0.1, 0.1, 0., 1.57, 0.],
            [0.1, 0.1, 0.1, 0., 1.57, 0.],
        ]
        cls.poses = [list_poses, [PoseObject(*pose, metadata=PoseMetadata.v1()) for pose in list_poses]]
        cls.points = [[p[:3] for p in pose] for pose in cls.poses]

    def test_010_save_workspace_from_robot_poses(self):
        for ix, poses in enumerate(self.poses):
            ws_name = f'test_poses_workspace_{ix}'
            self.assertIsNone(self.niryo_robot.save_workspace_from_robot_poses(ws_name, *poses))

    def test_020_save_workspace_from_points(self):
        for ix, points in enumerate(self.points):
            ws_name = f'test_points_workspace_{ix}'
            self.assertIsNone(self.niryo_robot.save_workspace_from_points(ws_name, *points))

    def test_030_get_workspace_poses(self):
        for ix, _ in enumerate(self.poses):
            ws_name = f'test_poses_workspace_{ix}'
            with self.assertRaises(NotImplementedError):
                poses = self.niryo_robot.get_workspace_poses(ws_name)

    def test_040_get_workspace_ratio(self):
        for ix, poses in enumerate(self.poses):
            ws_name = f'test_poses_workspace_{ix}'
            ratio = self.niryo_robot.get_workspace_ratio(ws_name)
            self.assertIsInstance(ratio, float)
            self.assertGreater(ratio, 0.0)

    def test_050_get_workspace_list(self):
        ws_list = self.niryo_robot.get_workspace_list()
        expected_ws = [f'test_poses_workspace_{ix}' for ix in range(len(self.poses))]
        expected_ws += [f'test_points_workspace_{ix}' for ix in range(len(self.points))]
        self.assertTrue(set(ws_list).issuperset(expected_ws), f'Expected {expected_ws} to be in {ws_list}')

    def test_060_get_target_pose_from_rel(self):
        for ix, _ in enumerate(self.poses):
            ws_name = f'test_poses_workspace_{ix}'
            pose = self.niryo_robot.get_target_pose_from_rel(ws_name, 0, 0.1, 0.1, 0.1)
            self.assertIsInstance(pose, PoseObject)

    def test_070_delete_workspace(self):
        workspaces = [f'test_poses_workspace_{ix}' for ix in range(len(self.poses))]
        workspaces += [f'test_points_workspace_{ix}' for ix in range(len(self.points))]
        for ws_name in workspaces:
            self.assertIsNone(self.niryo_robot.delete_workspace(ws_name))

    def test_080_get_workspace_list_empty(self):
        ws_list = self.niryo_robot.get_workspace_list()
        unexpected_ws = [f'test_poses_workspace_{ix}' for ix in range(len(self.poses))]
        unexpected_ws += [f'test_points_workspace_{ix}' for ix in range(len(self.points))]
        self.assertTrue(set(ws_list).isdisjoint(unexpected_ws))
