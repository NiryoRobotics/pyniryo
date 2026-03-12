from dataclasses import dataclass
from typing import Type

from strenum import StrEnum

from .._internal import transport_models
from ..exceptions import PyNiryoError, GenerateTrajectoryError, LoadTrajectoryError, ExecuteTrajectoryError
from .geometry import Joints, Pose


class Planner(StrEnum):
    """
    Enumeration of available motion planners.
    
    - RRT_CONNECT: RRT-Connect planner for complex paths.
    - RRT_STAR: RRT* planner with path optimization.
    - PRM: Probabilistic Roadmap planner.
    - PTP: Point-to-point planner for simple movements.
    - LIN: Linear interpolation planner for straight-line movements.
    - CIRC: Circular interpolation planner for arc movements.
    """
    RRT_CONNECT = "RRTConnect"
    RRT_STAR = "RRT*"
    PRM = "PRM*"
    PTP = "PTP"
    LIN = "LIN"
    CIRC = "CIRC"

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Planner) -> 'Planner':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.Planner:
        return transport_models.s.Planner(self.value)


@dataclass
class Waypoint:
    """
    Represents a waypoint in a robot trajectory.
    
    A waypoint can be defined either in joint space or Cartesian space (or both).
    If both are provided, joint values take priority.
    
    :param joints: Target joint positions (optional).
    :param pose: Target pose in Cartesian space (optional).
    :param frame_id: The reference frame for the pose (optional).
    :param reference_frame: Alternative reference frame specification (optional).
    :param planner: The motion planner to use for reaching this waypoint (optional).
    :param blending_radius: Radius for path blending at this waypoint in meters (optional).
    :param velocity_factor: Scaling factor for velocity (0.0 to 1.0, optional).
    :param acceleration_factor: Scaling factor for acceleration (0.0 to 1.0, optional).
    """
    joints: Joints | None = None
    pose: Pose | None = None
    frame_id: str | None = None
    reference_frame: str | None = None
    planner: Planner | None = None
    blending_radius: float | None = None
    velocity_factor: float | None = None
    acceleration_factor: float | None = None

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Waypoint) -> 'Waypoint':
        return cls(joints=Joints.from_transport_model(model.joints) if model.joints is not None else None,
                   pose=Pose.from_transport_model(model.pose) if model.pose is not None else None,
                   frame_id=model.frame_id,
                   reference_frame=model.reference_frame,
                   planner=Planner.from_transport_model(model.planner) if model.planner is not None else None,
                   blending_radius=model.blending_radius,
                   velocity_factor=model.velocity_factor,
                   acceleration_factor=model.acceleration_factor)

    def to_transport_model(self) -> transport_models.s.Waypoint:
        w = transport_models.s.Waypoint(joints=self.joints.to_transport_model() if self.joints is not None else None,
                                        pose=self.pose.to_transport_model() if self.pose is not None else None,
                                        frame_id=self.frame_id,
                                        reference_frame=self.reference_frame,
                                        planner=self.planner.to_transport_model() if self.planner is not None else None)
        if self.blending_radius is not None:
            w.blending_radius = self.blending_radius
        if self.velocity_factor is not None:
            w.velocity_factor = self.velocity_factor
        if self.acceleration_factor is not None:
            w.acceleration_factor = self.acceleration_factor
        return w


@dataclass
class JointsStamped:
    """
    Represents joint positions with associated timing and dynamic information.
    
    :param joints: The joint positions.
    :param timestamp: Time in seconds since the start of the trajectory.
    :param velocities: Joint velocities at this timestamp (optional).
    :param accelerations: Joint accelerations at this timestamp (optional).
    """
    joints: Joints
    timestamp: float
    velocities: list[float] | None
    accelerations: list[float] | None

    @classmethod
    def from_transport_model(cls, model: transport_models.s.JointsStamped) -> 'JointsStamped':
        return cls(
            joints=Joints.from_transport_model(model.joints),
            timestamp=model.timestamp,
            velocities=model.velocities,
            accelerations=model.accelerations,
        )

    def to_transport_model(self) -> transport_models.s.JointsStamped:
        return transport_models.s.JointsStamped(
            joints=self.joints.to_transport_model(),
            timestamp=self.timestamp,
            velocities=self.velocities,
            accelerations=self.accelerations,
        )


MoveTarget = Pose | Joints | Waypoint | list[Pose | Joints | Waypoint]


class MoveState(StrEnum):
    """
    Enumeration of possible states during a robot move operation.
    
    States prefixed with `ERR_` indicate error conditions.
    """
    UNKNOWN = "unknown"
    IDLE = "idle"
    PREPARING = "preparing"
    ERR_PREPARING = "error_preparing"
    GEN_TRAJ = "generating_trajectory"
    ERR_GEN_TRAJ = "error_generating_trajectory"
    LOAD_TRAJ = "loading_trajectory"
    ERR_LOAD_TRAJ = "error_loading_trajectory"
    EXEC_TRAJ = "executing_trajectory"
    ERR_EXEC_TRAJ = "error_executing_trajectory"
    DONE = "done"
    PAUSED = "paused"

    def is_error(self) -> bool:
        """
        Check if this state represents an error condition.
        
        :return: True if the state is an error state, False otherwise.
        """
        return self.name.startswith("ERR_")

    def is_final(self) -> bool:
        """
        Check if this state represents a final state (done or error).
        
        :return: True if the state is final, False otherwise.
        """
        return self == MoveState.DONE or self.is_error()

    def get_exception(self) -> Type[PyNiryoError]:
        """
        Get the exception class associated with this error state.
        
        :return: The exception class to raise for this error state.
        :raises ValueError: If this state is not an error state.
        """
        if not self.is_error():
            raise ValueError(f"MoveState {self} does not represent an error state.")
        match self:
            case self.ERR_GEN_TRAJ:
                return GenerateTrajectoryError
            case self.ERR_LOAD_TRAJ:
                return LoadTrajectoryError
            case self.ERR_EXEC_TRAJ:
                return ExecuteTrajectoryError
            case _:
                raise ValueError(f"MoveState {self} does not have an associated exception.")


@dataclass
class MoveFeedback:
    """
    Represents feedback information during a move operation.
    
    :param state: The current state of the move operation.
    :param message: A descriptive message about the current state.
    """
    state: MoveState
    message: str

    @classmethod
    def from_transport_model(cls, model: transport_models.a.MoveFeedback) -> 'MoveFeedback':
        return cls(
            state=MoveState(model.state.value),
            message=model.message,
        )

    def to_transport_model(self) -> transport_models.a.MoveFeedback:
        return transport_models.a.MoveFeedback(state=transport_models.a.State(self.state.value), message=self.message)
