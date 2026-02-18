from pyniryo.nate import models

from .._internal import paths_gen, transport_models

from . import BaseAPIComponent


class MotionPlanner(BaseAPIComponent):
    """
    Motion planner component for generating robot trajectories.
    
    This component provides methods for generating optimized trajectories from waypoints,
    which can then be executed on the robot for smooth motion.
    
    Example:
        >>> from pyniryo.nate import Nate
        >>> from pyniryo.nate.models import Waypoint, Waypoints, Joints, Planner
        >>> 
        >>> nate = Nate()
        >>> 
        >>> # Define waypoints
        >>> waypoints = Waypoints([
        ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
        ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0), planner=Planner.LIN),
        ...     Waypoint(joints=Joints(-1, -1, 1, 0, 0, 0))
        ... ])
        >>> 
        >>> # Generate trajectory
        >>> trajectory = nate.motion_planner.generate_trajectory(waypoints)
        >>> 
        >>> # Execute the trajectory
        >>> cmd = nate.robot.execute_trajectory(trajectory)
        >>> cmd.wait()
    """

    def generate_trajectory(self, waypoints: models.Waypoints, add_start: bool = False) -> models.Trajectory:
        """
        Generate a trajectory from a sequence of waypoints.
        
        This method computes a smooth trajectory that passes through the specified waypoints,
        taking into account robot kinematics, joint limits, and velocity/acceleration constraints.
        
        :param waypoints: The waypoints to generate the trajectory from.
        :param add_start: If True, add the current robot position as the first waypoint.
        :return: The generated trajectory.
        
        Example:
            >>> from pyniryo.nate.models import Waypoint, Waypoints, Joints, Planner
            >>> 
            >>> # Create waypoints with different planners
            >>> waypoints = Waypoints([
            ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
            ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0), planner=Planner.PTP),
            ...     Waypoint(joints=Joints(0, -1, 1, 0, 0, 0), planner=Planner.LIN, velocity_factor=0.5)
            ... ])
            >>> 
            >>> trajectory = motion_planner.generate_trajectory(waypoints, add_start=True)
            >>> print(f"Generated trajectory with {len(trajectory)} points")
        """
        req = transport_models.s.TrajectoryGeneration(waypoints=[wp.to_transport_model() for wp in waypoints],
                                                    motion_type=transport_models.s.MotionType.WAYPOINTS,
                                                    add_start=add_start)
        resp = self._http_client.post(paths_gen.Robot.GENERATE_TRAJECTORY, transport_models.s.GeneratedTrajectory, req)
        return models.Trajectory.from_transport_model(resp.waypoints)
