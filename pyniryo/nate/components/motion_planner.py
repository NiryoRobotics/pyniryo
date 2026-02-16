from pyniryo.nate import models

from .._internal import paths_gen, transport_models

from . import BaseAPIComponent


class MotionPlanner(BaseAPIComponent):

    def generate_trajectory(self, waypoints: models.Waypoints, add_start: bool = False) -> models.Trajectory:
        req = transport_models.s.TrajectoryGeneration(waypoints=[wp.to_transport_model() for wp in waypoints],
                                                    motion_type=transport_models.s.MotionType.WAYPOINTS,
                                                    add_start=add_start)
        resp = self._http_client.post(paths_gen.Robot.GENERATE_TRAJECTORY, transport_models.s.GeneratedTrajectory, req)
        return models.Trajectory.from_transport_model(resp.waypoints)
