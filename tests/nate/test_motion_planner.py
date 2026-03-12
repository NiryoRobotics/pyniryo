import unittest

from pyniryo.nate.models import motion, JointsStamped
from pyniryo.nate._internal import transport_models, paths_gen
from pyniryo.nate.components.motion_planner import MotionPlanner

from .base import BaseTestComponent


class TestMotionPlanner(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.motion_planner = MotionPlanner(http_client=self.http_client,
                                            mqtt_client=self.mqtt_client,
                                            correlation_id=self.correlation_id)

    def tearDown(self):
        del self.motion_planner

    def test_generate_trajectory(self):
        """Test generating trajectory from waypoints."""
        # Create test waypoints
        waypoint1 = motion.Waypoint(joints=motion.Joints(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        waypoint2 = motion.Waypoint(joints=motion.Joints(0.5, 0.5, 0.5, 0.5, 0.5, 0.5))
        waypoints = [waypoint1, waypoint2]

        # Create mock response trajectory
        joints_stamped1 = transport_models.s.JointsStamped(
            joints=transport_models.s.Joints(root=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            timestamp=0.0,
            velocities=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            accelerations=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        joints_stamped2 = transport_models.s.JointsStamped(
            joints=transport_models.s.Joints(root=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
            timestamp=1.0,
            velocities=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            accelerations=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        mock_trajectory = transport_models.s.Trajectory(root=[joints_stamped1, joints_stamped2])
        self.http_client.post.return_value = transport_models.s.GeneratedTrajectory(waypoints=mock_trajectory)

        # Call method
        trajectory = self.motion_planner.generate_trajectory(waypoints, add_start=False)

        # Verify HTTP client was called correctly
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Robot.GENERATE_TRAJECTORY)
        self.assertEqual(call_args[1], transport_models.s.GeneratedTrajectory)

        # Verify request payload
        request = call_args[2]
        self.assertIsInstance(request, transport_models.s.TrajectoryGeneration)
        self.assertEqual(len(request.waypoints), 2)
        self.assertEqual(request.motion_type, transport_models.s.MotionType.WAYPOINTS)
        self.assertFalse(request.add_start)

        # Verify result
        self.assertIsInstance(trajectory, list)
        self.assertEqual(len(trajectory), 2)
        self.assertIsInstance(trajectory[0], JointsStamped)
        self.assertEqual(trajectory[0].joints.data, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(trajectory[1].joints.data, [0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

    def test_generate_trajectory_with_add_start(self):
        """Test generating trajectory with add_start=True."""
        waypoint = motion.Waypoint(joints=motion.Joints(1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
        waypoints = [waypoint]

        joints_stamped = transport_models.s.JointsStamped(
            joints=transport_models.s.Joints(root=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            timestamp=0.0,
            velocities=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            accelerations=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        mock_trajectory = transport_models.s.Trajectory(root=[joints_stamped])
        self.http_client.post.return_value = transport_models.s.GeneratedTrajectory(waypoints=mock_trajectory)

        trajectory = self.motion_planner.generate_trajectory(waypoints, add_start=True)

        # Verify add_start parameter was passed
        request = self.http_client.post.call_args[0][2]
        self.assertTrue(request.add_start)
        self.assertIsInstance(trajectory, list)
        self.assertIsInstance(trajectory[0], JointsStamped)


if __name__ == "__main__":
    unittest.main()
