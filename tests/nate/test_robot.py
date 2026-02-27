import unittest
import xml.etree.ElementTree as ET

from unittest.mock import MagicMock, patch
from uuid import uuid4

from pyniryo.nate.models import robot, geometry, motion
from pyniryo.nate._internal import transport_models, paths_gen, topics_gen
from pyniryo.nate.components.robot import Robot, MoveCommand
from pyniryo.nate.exceptions import GenerateTrajectoryError

from .base import BaseTestComponent


class TestRobot(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.robot = Robot(http_client=self.http_client,
                           mqtt_client=self.mqtt_client,
                           correlation_id=self.correlation_id)

    def tearDown(self):
        del self.robot

    def test_get_joints(self):
        """Test getting current joint positions."""
        joint_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.http_client.get.return_value = transport_models.s.Joints(root=joint_values)

        joints = self.robot.get_joints()

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_ROBOT_JOINTS, transport_models.s.Joints)
        self.assertIsInstance(joints, geometry.Joints)
        self.assertEqual(joints.data, joint_values)

    def test_on_joints(self):
        """Test subscribing to joint updates."""
        callback = MagicMock()

        self.robot.on_joints(callback)

        self.mqtt_client.subscribe.assert_called_once()
        topic, internal_callback, model = self.mqtt_client.subscribe.call_args[0]
        self.assertEqual(topic, topics_gen.Robot.JOINTS)
        self.assertEqual(model, transport_models.a.Joints)

        # Simulate receiving joints
        joint_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        internal_callback(topic, transport_models.a.Joints(positions=joint_values, velocities=[0.0] * 6, timestamp=0))

        callback.assert_called_once()
        called_joints = callback.call_args[0][0]
        self.assertIsInstance(called_joints, geometry.Joints)
        self.assertEqual(called_joints.data, joint_values)

    def test_get_all_frames(self):
        """Test getting all frame IDs."""
        frame_ids = ['base_link', 'tcp', 'world']
        self.http_client.get.return_value = transport_models.FrameIdList(root=frame_ids)

        frames = self.robot.get_all_frames()

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_ALL_FRAMES, transport_models.FrameIdList)
        self.assertEqual(frames, frame_ids)

    def test_get_frame_pose(self):
        """Test getting a specific frame's pose."""
        frame_id = 'tcp'
        mock_pose = transport_models.s.Pose(position=transport_models.s.Point(x=0.1, y=0.2, z=0.3),
                                            orientation=transport_models.s.Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        self.http_client.get.return_value = mock_pose

        pose = self.robot.get_frame_pose(frame_id)

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_FRAME_POSE.format(frame_id=frame_id),
                                                     transport_models.s.Pose)
        self.assertIsInstance(pose, geometry.Pose)
        self.assertEqual(pose.position.x, 0.1)

    def test_on_frame_pose(self):
        """Test subscribing to frame pose updates."""
        frame_id = 'tcp'
        callback = MagicMock()

        self.robot.on_frame_pose(frame_id, callback)

        self.mqtt_client.subscribe.assert_called_once()
        topic, internal_callback, model = self.mqtt_client.subscribe.call_args[0]
        self.assertEqual(topic, topics_gen.Robot.FRAME_POSE.format(frame_id=frame_id))
        self.assertEqual(model, transport_models.a.Pose)

        # Simulate receiving pose
        mock_pose = transport_models.s.Pose(position=transport_models.s.Point(x=0.1, y=0.2, z=0.3),
                                            orientation=transport_models.s.Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        internal_callback(topic, mock_pose)

        callback.assert_called_once()
        called_pose = callback.call_args[0][0]
        self.assertIsInstance(called_pose, geometry.Pose)

    def test_move_with_joints(self):
        """Test moving with joint target."""
        command_id = str(uuid4())
        joints = geometry.Joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        move_cmd = self.robot.move(joints)

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Robot.MOVE_ALONG_WAYPOINTS)

        request = call_args[2]
        self.assertEqual(str(request.command_id), move_cmd.command_id)
        self.assertFalse(request.add_start)
        self.assertEqual(len(request.waypoints), 1)

        self.assertIsInstance(move_cmd, MoveCommand)

    def test_move_with_pose(self):
        """Test moving with pose target."""
        command_id = str(uuid4())
        pose = geometry.Pose(position=geometry.Point(x=0.1, y=0.2, z=0.3),
                             orientation=geometry.Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        move_cmd = self.robot.move(pose)

        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.waypoints), 1)
        self.assertIsNotNone(request.waypoints[0].pose)

    def test_move_with_waypoint(self):
        """Test moving with single waypoint target."""
        command_id = str(uuid4())
        waypoint = motion.Waypoint(joints=geometry.Joints(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), velocity_factor=0.5)
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        move_cmd = self.robot.move(waypoint)

        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.waypoints), 1)
        self.assertEqual(request.waypoints[0].velocity_factor, 0.5)

    def test_move_with_waypoints(self):
        """Test moving with multiple waypoints."""
        command_id = str(uuid4())
        waypoints = motion.Waypoints([
            motion.Waypoint(joints=geometry.Joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
            motion.Waypoint(joints=geometry.Joints(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)),
        ])
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        _ = self.robot.move(waypoints)

        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.waypoints), 2)

    def test_move_with_add_start(self):
        """Test moving with add_start=True."""
        command_id = str(uuid4())
        joints = geometry.Joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        _ = self.robot.move(joints, add_start=True)

        request = self.http_client.post.call_args[0][2]
        self.assertTrue(request.add_start)

    def test_move_with_invalid_type(self):
        """Test moving with invalid target type."""
        with self.assertRaises(TypeError):
            self.robot.move("invalid")

    def test_execute_trajectory(self):
        """Test executing a trajectory."""
        command_id = str(uuid4())
        joints_stamped = motion.JointsStamped(joints=geometry.Joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                                              timestamp=0.0,
                                              velocities=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                              accelerations=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        trajectory = motion.Trajectory([joints_stamped])
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=command_id)

        move_cmd = self.robot.execute_trajectory(trajectory)

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Robot.EXECUTE_TRAJECTORY)

        request = call_args[2]
        self.assertEqual(str(request.command_id), move_cmd.command_id)
        self.assertIsInstance(move_cmd, MoveCommand)

    def test_get_urdf(self):
        """Test getting URDF."""
        urdf_content = b'<?xml version="1.0"?><robot name="test"><link name="base"/></robot>'

        def mock_download(path, buffer):
            buffer.write(urdf_content)

        self.http_client.download.side_effect = mock_download

        urdf = self.robot.get_urdf()

        self.http_client.download.assert_called_once()
        self.assertIsInstance(urdf, ET.Element)
        self.assertEqual(urdf.tag, 'robot')
        self.assertEqual(urdf.get('name'), 'test')

    def test_get_configuration(self):
        """Test getting robot configuration."""
        mock_config = transport_models.s.RobotConfig(name='test_robot', number_joints=6, joints=[])
        self.http_client.get.return_value = mock_config

        config = self.robot.get_configuration()

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_ROBOT_CONFIG, transport_models.s.RobotConfig)
        self.assertIsInstance(config, robot.RobotConfiguration)
        self.assertEqual(config.name, 'test_robot')
        self.assertEqual(config.n_joint, 6)

    def test_get_control_mode(self):
        """Test getting control mode."""
        mock_mode = transport_models.s.ControlMode(mode_name=transport_models.s.ModeName.TRAJECTORY,
                                                   mode=transport_models.s.Mode(1))
        self.http_client.get.return_value = mock_mode

        mode = self.robot.get_control_mode()

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_ROBOT_CONTROL_MODE,
                                                     transport_models.s.ControlMode)
        self.assertEqual(mode, robot.ControlMode.TRAJECTORY)

    def test_set_control_mode(self):
        """Test setting control mode."""
        target_mode = robot.ControlMode.JOG
        mock_response = transport_models.s.ControlMode(mode_name=transport_models.s.ModeName.JOG,
                                                       mode=transport_models.s.Mode(2))
        self.http_client.put.return_value = mock_response

        self.robot.set_control_mode(target_mode)

        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Robot.SET_ROBOT_CONTROL_MODE)

    def test_set_control_mode_failure(self):
        """Test setting control mode when it fails to set."""
        target_mode = robot.ControlMode.JOG
        # Return different mode than requested
        mock_response = transport_models.s.ControlMode(mode_name=transport_models.s.ModeName.TRAJECTORY,
                                                       mode=transport_models.s.Mode(1))
        self.http_client.put.return_value = mock_response

        with self.assertRaises(RuntimeError):
            self.robot.set_control_mode(target_mode)

    def test_jog_mode_context_manager(self):
        """Test jog mode context manager."""
        # Mock getting current mode
        initial_mode = robot.ControlMode.TRAJECTORY.to_transport_model()
        jog_mode = robot.ControlMode.JOG.to_transport_model()

        self.http_client.get.return_value = initial_mode
        self.http_client.put.return_value = jog_mode

        with self.robot.jog_mode():
            # Inside context, should be in jog mode
            self.http_client.put.return_value = initial_mode

        # Should call put twice: once to set jog, once to restore
        self.assertEqual(self.http_client.put.call_count, 2)

        # First call should set to jog
        first_call = self.http_client.put.call_args_list[0][0][2]
        self.assertEqual(first_call.mode.value, 2)

    def test_jog_mode_context_manager_with_exception(self):
        """Test jog mode context manager when exception occurs."""
        initial_mode = robot.ControlMode.TRAJECTORY.to_transport_model()
        jog_mode = robot.ControlMode.JOG.to_transport_model()

        self.http_client.get.return_value = initial_mode
        self.http_client.put.return_value = jog_mode

        try:
            with self.robot.jog_mode():
                self.http_client.put.return_value = initial_mode
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should still restore mode even after exception
        self.assertEqual(self.http_client.put.call_count, 2)

    def test_stop_jog(self):
        """Test stopping jog command."""
        self.robot.stop_jog()

        self.mqtt_client.publish.assert_called_once()
        topic, payload = self.mqtt_client.publish.call_args[0]
        self.assertEqual(topic, topics_gen.Cmd.ROBOT_JOG_STOP)
        self.assertIsInstance(payload, transport_models.EmptyPayload)

    def test_jog_joints(self):
        """Test jogging with joint velocities."""
        target_joints = geometry.Joints(0.1, 0.2, 0.3, 0.4, 0.5, 0.6)

        self.robot.jog_joints(target_joints)

        self.mqtt_client.publish.assert_called_once()
        topic, payload = self.mqtt_client.publish.call_args[0]
        self.assertEqual(topic, topics_gen.Cmd.ROBOT_JOG_JOINT)
        self.assertIsInstance(payload, transport_models.a.JogJoint)
        self.assertEqual(payload.velocities, target_joints.data)

    def test_jog_cartesian_without_frame(self):
        """Test jogging in Cartesian space without frame."""
        linear = [0.1, 0.0, 0.0]
        angular = [0.0, 0.0, 0.1]

        self.robot.jog_cartesian(linear, angular)

        self.mqtt_client.publish.assert_called_once()
        topic, payload = self.mqtt_client.publish.call_args[0]
        self.assertEqual(topic, topics_gen.Cmd.ROBOT_JOG_CARTESIAN)
        self.assertIsInstance(payload, transport_models.a.JogCartesian)
        self.assertEqual(payload.linear, linear)
        self.assertEqual(payload.angular, angular)
        self.assertIsNone(payload.frame_id)

    def test_jog_cartesian_with_frame(self):
        """Test jogging in Cartesian space with frame."""
        linear = [0.1, 0.0, 0.0]
        angular = [0.0, 0.0, 0.1]
        frame_id = 'tcp'

        self.robot.jog_cartesian(linear, angular, frame_id)

        payload = self.mqtt_client.publish.call_args[0][1]
        self.assertEqual(payload.frame_id, frame_id)

    def test_executor_status(self):
        """Test getting executor status."""
        self.http_client.get.return_value = transport_models.s.TrajectoryExecutorStatus(
            status=transport_models.s.ExecutorStatus.RUNNING)

        status = self.robot.executor_status()

        self.http_client.get.assert_called_once_with(paths_gen.Robot.GET_TRAJECTORY_EXECUTOR_STATUS,
                                                     transport_models.s.TrajectoryExecutorStatus)
        self.assertEqual(status, robot.ExecutorStatus.RUNNING)

    def test_pause(self):
        """Test pausing trajectory execution."""
        self.http_client.patch.return_value = None

        self.robot.pause()

        self.http_client.patch.assert_called_once()
        call_args = self.http_client.patch.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Robot.UPDATE_TRAJECTORY_EXECUTOR_STATUS)
        request = call_args[2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.PAUSED)

    def test_stop(self):
        """Test stopping trajectory execution."""
        self.http_client.patch.return_value = None

        self.robot.stop()

        request = self.http_client.patch.call_args[0][2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.STOPPED)

    def test_resume(self):
        """Test resuming trajectory execution."""
        self.http_client.patch.return_value = None

        self.robot.resume()

        request = self.http_client.patch.call_args[0][2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.RUNNING)


class TestMoveCommand(BaseTestComponent):

    def test_initial_state(self):
        """Test initial state of MoveCommand."""
        command_id = str(uuid4())

        cmd = MoveCommand(self.mqtt_client, command_id)

        self.assertEqual(cmd.command_id, command_id)
        self.assertEqual(cmd.state, motion.MoveState.UNKNOWN)

        # Should subscribe to feedback topic
        self.mqtt_client.subscribe.assert_called_once()
        topic = self.mqtt_client.subscribe.call_args[0][0]
        self.assertEqual(topic, topics_gen.Robot.ROBOT_MOVE_FEEDBACK.format(cmd_id=command_id))

    def test_topic_property(self):
        """Test topic property."""
        command_id = str(uuid4())
        cmd = MoveCommand(self.mqtt_client, command_id)

        expected_topic = topics_gen.Robot.ROBOT_MOVE_FEEDBACK.format(cmd_id=command_id)
        self.assertEqual(cmd.topic, expected_topic)

    def test_feedback_callback_updates_state(self):
        """Test that feedback callback updates state."""
        command_id = str(uuid4())
        cmd = MoveCommand(self.mqtt_client, command_id)

        # Get the internal callback
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate receiving feedback
        feedback = transport_models.a.MoveFeedback(state=transport_models.a.State.PREPARING, message='Preparing move')
        internal_callback(cmd.topic, feedback)

        self.assertEqual(cmd.state, motion.MoveState.PREPARING)

    def test_feedback_callback_unsubscribes_on_final_state(self):
        """Test that feedback callback unsubscribes when reaching final state."""
        command_id = str(uuid4())
        cmd = MoveCommand(self.mqtt_client, command_id)

        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate completing the move
        feedback = transport_models.a.MoveFeedback(state=transport_models.a.State.DONE, message='Move completed')
        internal_callback(cmd.topic, feedback)

        # Should unsubscribe when reaching final state
        self.mqtt_client.unsubscribe.assert_called_once()

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_success(self, mock_monotonic, mock_sleep):
        """Test waiting for move to complete successfully."""
        command_id = str(uuid4())
        mock_monotonic.return_value = 0.0

        cmd = MoveCommand(self.mqtt_client, command_id)

        # Simulate move completion
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        feedback = transport_models.a.MoveFeedback(state=transport_models.a.State.DONE, message='Move completed')
        internal_callback(cmd.topic, feedback)

        # Wait should return without error
        cmd.wait()

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_timeout(self, mock_monotonic, mock_sleep):
        """Test waiting for move with timeout."""
        command_id = str(uuid4())
        mock_monotonic.side_effect = [0.0, 0.5, 1.0, 1.5]

        cmd = MoveCommand(self.mqtt_client, command_id)

        # Don't change state, so it stays in UNKNOWN
        with self.assertRaises(TimeoutError):
            cmd.wait(timeout=1.0)

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_error(self, mock_monotonic, mock_sleep):
        """Test waiting for move that fails."""
        command_id = str(uuid4())
        mock_monotonic.return_value = 0.0

        cmd = MoveCommand(self.mqtt_client, command_id)

        # Simulate move error
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        feedback = transport_models.a.MoveFeedback(state=transport_models.a.State.ERROR_GENERATING_TRAJECTORY,
                                                   message='Failed to generate trajectory')
        internal_callback(cmd.topic, feedback)

        # Wait should raise the appropriate error
        with self.assertRaises(GenerateTrajectoryError):
            cmd.wait()

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_negative_timeout(self, mock_monotonic, mock_sleep):
        """Test waiting with negative timeout (wait indefinitely)."""
        command_id = str(uuid4())
        mock_monotonic.return_value = 0.0

        cmd = MoveCommand(self.mqtt_client, command_id)

        # Complete move immediately
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        feedback = transport_models.a.MoveFeedback(state=transport_models.a.State.DONE, message='Move completed')
        internal_callback(cmd.topic, feedback)

        # Should work with negative timeout (waits indefinitely)
        cmd.wait(timeout=-1)


if __name__ == "__main__":
    unittest.main()
