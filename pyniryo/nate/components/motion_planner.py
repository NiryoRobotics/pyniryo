from ..models import Waypoints, Trajectory
from .._internal import paths_gen, transport_models

from . import BaseAPIComponent


class MotionPlanner(BaseAPIComponent):
    """
    Motion planner component for generating robot trajectories.
    
    This component provides methods for generating optimized trajectories from waypoints,
    which can then be executed on the robot for smooth motion.
    """

    def generate_trajectory(self, waypoints: Waypoints, add_start: bool = False) -> Trajectory:
        """
        Generate a trajectory from a sequence of waypoints.
        
        This method computes a smooth trajectory that passes through the specified waypoints,
        taking into account robot kinematics, joint limits, and velocity/acceleration constraints.
        
        :param waypoints: The waypoints to generate the trajectory from.
        :param add_start: If True, add the current robot position as the first waypoint.
        :return: The generated trajectory.
        """
        req = transport_models.s.TrajectoryGeneration(waypoints=[wp.to_transport_model() for wp in waypoints],
                                                      motion_type=transport_models.s.MotionType.WAYPOINTS,
                                                      add_start=add_start)
        resp = self._http_client.post(paths_gen.Robot.GENERATE_TRAJECTORY, transport_models.s.GeneratedTrajectory, req)
        return Trajectory.from_transport_model(resp.waypoints)
