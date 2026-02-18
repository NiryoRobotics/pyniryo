import math
import re
from collections import UserList
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Type, Optional

from strenum import StrEnum
from uuid import UUID

from ._internal import transport_models
from .exceptions import PyNiryoError, GenerateTrajectoryError, LoadTrajectoryError, ExecuteTrajectoryError


@dataclass
class Role:
    """
    Represents a user role in the system.
    
    :param id: The unique identifier of the role.
    :param name: The name of the role.
    """
    id: int
    name: str

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Role) -> 'Role':
        return cls(
            id=model.id,
            name=model.name,
        )

    def to_transport_model(self) -> transport_models.s.Role:
        return transport_models.s.Role(id=self.id, name=self.name)


@dataclass
class User:
    """
    Represents a user in the system.
    
    :param id: The unique identifier of the user.
    :param login: The login/email of the user.
    :param name: The display name of the user.
    :param role: The role assigned to the user.
    """
    id: str
    login: str
    name: str
    role: Role

    @classmethod
    def from_transport_model(cls, model: transport_models.s.User) -> 'User':
        return cls(
            id=str(model.id),
            login=str(model.login),
            name=model.name,
            role=Role.from_transport_model(model.role),
        )

    def to_transport_model(self) -> transport_models.s.User:
        return transport_models.s.User(id=UUID(self.id),
                                       login=self.login,
                                       name=self.name,
                                       role=self.role.to_transport_model())


@dataclass
class Token:
    """
    Represents an authentication token.
    
    :param id: The unique identifier of the token.
    :param expires_at: The expiration date and time of the token.
    :param created_at: The creation date and time of the token.
    :param token: The token string used for authentication.
    """
    id: UUID
    expires_at: datetime
    created_at: datetime
    token: str

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Token) -> 'Token':
        return cls(
            id=model.id,
            expires_at=model.expires_at,
            created_at=model.created_at,
            token=model.token,
        )

    def to_transport_model(self) -> transport_models.s.Token:
        return transport_models.s.Token(id=self.id,
                                        expires_at=self.expires_at,
                                        created_at=self.created_at,
                                        token=self.token)


@dataclass
class UserEvent:
    """
    Represents an event related to user actions (login, logout, etc.).
    
    This class is used to capture user authentication events that occur in the system.
    Events are typically received through MQTT callbacks when monitoring user login
    and logout activities.
    
    Example:
        >>> def on_login(user_id, event):
        ...     print(f"User {user_id} logged in")
        >>> 
        >>> nate.auth.on_user_logged_in(on_login)
    """

    @classmethod
    def from_transport_model(cls, model: transport_models.a.UserEvent) -> 'UserEvent':
        return cls()

    def to_transport_model(self) -> transport_models.a.UserEvent:
        return transport_models.a.UserEvent()


class Joints(UserList[float]):
    """
    Represents joint positions for a robot.
    
    A list of float values representing the position of each joint in radians.
    Can optionally include timestamp and velocity information.
    
    :param joints: Variable number of joint positions (in radians).
    
    Example:
        >>> joints = Joints(0.0, -1.57, 1.57, 0.0, 0.0, 0.0)
        >>> print(joints[0])  # Access first joint
        0.0
    """
    timestamp: int | None = None
    velocities: list[float] | None = None

    def __init__(self, *joints: float):
        if len(joints) > 0 and isinstance(joints[0], list):
            joints = joints[0]
        super().__init__(initlist=joints)

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Joints) -> 'Joints':
        return cls(*model.root)

    def to_transport_model(self) -> transport_models.s.Joints:
        return transport_models.s.Joints(root=self.data)

    @classmethod
    def from_a_transport_model(cls, model: transport_models.a.Joints) -> 'Joints':
        m = cls(*model.positions)
        m.timestamp = model.timestamp
        m.velocities = model.velocities
        return m

    def to_a_transport_model(self) -> transport_models.a.Joints:
        return transport_models.a.Joints(positions=self.data, timestamp=self.timestamp, velocities=self.velocities)


@dataclass
class Point:
    """
    Represents a 3D point in Cartesian space.
    
    :param x: The x-coordinate in meters.
    :param y: The y-coordinate in meters.
    :param z: The z-coordinate in meters.
    """
    x: float
    y: float
    z: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Point) -> 'Point':
        return cls(x=model.x, y=model.y, z=model.z)

    def to_transport_model(self) -> transport_models.s.Point:
        return transport_models.s.Point(x=self.x, y=self.y, z=self.z)


@dataclass
class Quaternion:
    """
    Represents orientation using quaternion representation.
    
    :param x: The x component of the quaternion.
    :param y: The y component of the quaternion.
    :param z: The z component of the quaternion.
    :param w: The w (scalar) component of the quaternion.
    """
    x: float
    y: float
    z: float
    w: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Quaternion) -> 'Quaternion':
        return cls(x=model.x, y=model.y, z=model.z, w=model.w)

    def to_transport_model(self) -> transport_models.s.Quaternion:
        return transport_models.s.Quaternion(x=self.x, y=self.y, z=self.z, w=self.w)


@dataclass
class EulerAngles:
    """
    Represents orientation using Euler angles (roll, pitch, yaw).
    
    :param roll: Rotation around the x-axis in radians.
    :param pitch: Rotation around the y-axis in radians.
    :param yaw: Rotation around the z-axis in radians.
    """
    roll: float
    pitch: float
    yaw: float

    def to_quaternion(self) -> Quaternion:
        """
        Convert Euler angles to quaternion representation.
        
        :return: The equivalent Quaternion representation.
        """
        cy = math.cos(self.yaw * 0.5)
        sy = math.sin(self.yaw * 0.5)
        cp = math.cos(self.pitch * 0.5)
        sp = math.sin(self.pitch * 0.5)
        cr = math.cos(self.roll * 0.5)
        sr = math.sin(self.roll * 0.5)
        rw = cr * cp * cy + sr * sp * sy
        rx = sr * cp * cy - cr * sp * sy
        ry = cr * sp * cy + sr * cp * sy
        rz = cr * cp * sy - sr * sp * cy

        return Quaternion(rx, ry, rz, rw)


@dataclass
class Pose:
    """
    Represents a pose in 3D space, defined by a position and an orientation.
     - The position is represented by a Point (x, y, z).
     - The orientation can be represented either as a Quaternion (x, y, z, w) or as Euler angles (roll, pitch, yaw).

     The choice between Quaternion and Euler angles is left to the user.
     Keep in mind that the Nate API expects orientations to be sent as Quaternions, so Euler angles will be
     automatically converted to Quaternions when sending commands to the API.
    """
    position: Point
    orientation: Quaternion | EulerAngles

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Pose) -> 'Pose':
        return cls(
            position=Point.from_transport_model(model.position),
            orientation=Quaternion.from_transport_model(model.orientation),
        )

    def to_transport_model(self) -> transport_models.s.Pose:
        quaternion = self.orientation
        if isinstance(self.orientation, EulerAngles):
            quaternion = self.orientation.to_quaternion()

        return transport_models.s.Pose(position=self.position.to_transport_model(),
                                       orientation=quaternion.to_transport_model())


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
    joints: Optional[Joints] = None
    pose: Optional[Pose] = None
    frame_id: Optional[str] = None
    reference_frame: Optional[str] = None
    planner: Optional[Planner] = None
    blending_radius: Optional[float] = None
    velocity_factor: Optional[float] = None
    acceleration_factor: Optional[float] = None

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Waypoint) -> 'Waypoint':
        return cls(joints=Joints.from_transport_model(model.joints),
                   pose=Pose.from_transport_model(model.pose),
                   frame_id=model.frame_id,
                   reference_frame=model.reference_frame,
                   planner=Planner.from_transport_model(model.planner),
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


class Waypoints(UserList[Waypoint]):
    """
    A list of Waypoint objects representing a sequence of target positions.
    
    This class extends UserList to provide a convenient container for managing
    multiple waypoints in a robot trajectory. It can be used with the robot.move()
    method to execute complex multi-point movements.
    
    Example:
        >>> from pyniryo.nate.models import Waypoint, Waypoints, Joints, Planner
        >>> waypoints = Waypoints([
        ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
        ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0), planner=Planner.LIN),
        ...     Waypoint(joints=Joints(-1, -1, 1, 0, 0, 0))
        ... ])
        >>> cmd = robot.move(waypoints)
        >>> cmd.wait()
    """

    @classmethod
    def from_transport_model(cls, model: list[transport_models.s.Waypoint]) -> 'Waypoints':
        return cls(*[Waypoint.from_transport_model(wp) for wp in model])

    def to_transport_model(self) -> list[transport_models.s.Waypoint]:
        return [wp.to_transport_model() for wp in self]


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


class Trajectory(UserList[JointsStamped]):
    """
    A sequence of JointsStamped objects representing a time-parameterized robot trajectory.
    
    This class represents a complete trajectory with joint positions, velocities, and
    accelerations at each timestep. Trajectories are typically generated by the motion
    planner and can be executed directly on the robot for smooth, optimized motion.
    
    Each element in the trajectory contains:
    - Joint positions at a specific timestamp
    - Optional velocities and accelerations
    - Timing information relative to trajectory start
    
    Example:
        >>> # Generate a trajectory from waypoints
        >>> waypoints = Waypoints([
        ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
        ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0))
        ... ])
        >>> trajectory = motion_planner.generate_trajectory(waypoints)
        >>> 
        >>> # Execute the trajectory
        >>> cmd = robot.execute_trajectory(trajectory)
        >>> cmd.wait()
    """

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Trajectory) -> 'Trajectory':
        return cls(JointsStamped.from_transport_model(js) for js in model.root)

    def to_transport_model(self) -> transport_models.s.Trajectory:
        return transport_models.s.Trajectory(root=[js.to_transport_model() for js in self])


MoveTarget = Pose | Joints | Waypoint | Waypoints


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


class ProgramType(StrEnum):
    """
    Enumeration of supported program types and Python versions.
    """
    PYTHON39 = 'python3.9'
    PYTHON310 = 'python3.10'
    PYTHON311 = 'python3.11'
    PYTHON312 = 'python3.12'

    def __key(self):
        pattern = r'^([a-z]+)([\d\.?]+)$'
        match = re.match(pattern, self)
        if not match:
            raise ValueError(f"Invalid ProgramType format: {self}")
        return match.group(1), tuple(int(v) for v in match.group(2).split('.'))

    @classmethod
    def python(cls) -> 'ProgramType':
        """
        Get the latest supported Python version.
        :return: The latest supported Python version.
        """
        return max((e for e in cls if e.__key()[0] == 'python'), key=lambda e: e.__key())

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Type) -> 'ProgramType':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.Type:
        return transport_models.s.Type(str(self))


@dataclass
class Program:
    """
    Represents a program stored on the robot.
    
    :param id: The unique identifier of the program.
    :param name: The name of the program.
    :param type: The type/version of the program.
    """
    id: str
    name: str
    type: ProgramType

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Program) -> 'Program':
        return cls(
            id=str(model.id),
            name=model.name,
            type=ProgramType.from_transport_model(model.type),
        )

    def to_transport_model(self) -> transport_models.s.Program:
        return transport_models.s.Program(
            id=UUID(self.id),
            name=self.name,
            type=transport_models.s.Type(self.type.value),
        )


@dataclass
class ProgramExecutionContext:
    """
    Represents the execution context for a program.
    
    :param environment: Environment variables to set for the program execution.
    :param arguments: Command-line arguments to pass to the program.
    """
    environment: dict[str, str]
    arguments: list[str]

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramExecutionContext) -> 'ProgramExecutionContext':
        return cls(
            environment=model.environment or {},
            arguments=model.arguments or [],
        )

    def to_transport_model(self) -> transport_models.s.ProgramExecutionContext:
        return transport_models.s.ProgramExecutionContext(
            environment=self.environment,
            arguments=self.arguments,
        )


@dataclass
class ProgramExecution:
    """
    Represents a program execution instance.
    
    :param id: The unique identifier of the execution.
    :param program_id: The ID of the program being executed.
    :param context: The execution context (environment variables and arguments).
    :param started_at: When the execution started.
    :param finished_at: When the execution finished.
    :param exit_code: The exit code of the program execution.
    """
    id: str
    program_id: str
    context: ProgramExecutionContext
    started_at: datetime
    finished_at: datetime
    exit_code: int

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramExecution) -> 'ProgramExecution':
        return cls(
            id=str(model.id),
            program_id=str(model.programId),
            context=ProgramExecutionContext.from_transport_model(model.context),
            started_at=model.startedAt,
            finished_at=model.finishedAt,
            exit_code=model.exitCode,
        )

    def to_transport_model(self) -> transport_models.s.ProgramExecution:
        return transport_models.s.ProgramExecution(id=UUID(self.id),
                                                   programId=UUID(self.program_id),
                                                   context=self.context.to_transport_model(),
                                                   startedAt=self.started_at,
                                                   finishedAt=self.finished_at,
                                                   exitCode=self.exit_code)


@dataclass
class ExecutionOutput:
    """
    Represents output from a program execution.
    
    :param output: The output text from the program.
    :param eof: Whether this is the end of the output stream.
    """
    output: str
    eof: bool

    @classmethod
    def from_transport_model(cls, model: transport_models.a.ProgramExecutionOutput) -> 'ExecutionOutput':
        return cls(output=model.output, eof=model.eof)

    def to_transport_model(self) -> transport_models.a.ProgramExecutionOutput:
        return transport_models.a.ProgramExecutionOutput(output=self.output, eof=self.eof)


class ExecutionStatusStatus(StrEnum):
    """
    Enumeration of program execution statuses.
    """
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PAUSED = 'paused'
    STOPPED = 'stopped'

    def is_error(self) -> bool:
        """
        Check if this status represents an error condition.
        
        :return: True if the status indicates failure, False otherwise.
        """
        return self == ExecutionStatusStatus.FAILED

    def is_final(self) -> bool:
        """
        Check if this status represents a final state.
        
        :return: True if the status is final (completed or failed), False otherwise.
        """
        return self == ExecutionStatusStatus.COMPLETED or self.is_error()

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ExecutorStatus) -> 'ExecutionStatusStatus':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.ExecutorStatus:
        return transport_models.s.ExecutorStatus(self.value)


@dataclass
class ExecutionStatus:
    """
    Represents the current status of a program execution.
    
    :param status: The current execution status.
    """
    status: ExecutionStatusStatus

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramsExecutorStatus) -> 'ExecutionStatus':
        return cls(status=ExecutionStatusStatus.from_transport_model(model.status))

    def to_transport_model(self) -> transport_models.s.ProgramsExecutorStatus:
        return transport_models.s.ProgramsExecutorStatus(status=self.status.to_transport_model())


@dataclass
class PID:
    """
    Represents PID controller gains.
    
    :param p: Proportional gain.
    :param i: Integral gain.
    :param d: Derivative gain.
    :param ff: Feed-forward gain.
    :param max_i: Maximum integral term value.
    :param max_out: Maximum output value.
    """
    p: float
    i: float
    d: float
    ff: float
    max_i: float
    max_out: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.PIDGains) -> 'PID':
        return cls(p=model.p, i=model.i, d=model.d, ff=model.ff, max_i=model.max_i, max_out=model.max_out)

    def to_transport_model(self) -> transport_models.s.PIDGains:
        return transport_models.s.PIDGains(p=self.p,
                                           i=self.i,
                                           d=self.d,
                                           ff=self.ff,
                                           max_i=self.max_i,
                                           max_out=self.max_out)


@dataclass
class JointConfiguration:
    """
    Represents the configuration of a single robot joint.
    
    :param name: The name of the joint.
    :param type: The type of joint (e.g., revolute, prismatic).
    :param position_limit_min: Minimum position limit.
    :param position_limit_max: Maximum position limit.
    :param velocity_limit: Maximum velocity.
    :param acceleration_limit: Maximum acceleration.
    :param effort_limit: Maximum effort/torque.
    :param pid_position: PID gains for position control (optional).
    :param pid_velocity: PID gains for velocity control (optional).
    """
    name: str
    type: str
    position_limit_min: float
    position_limit_max: float
    velocity_limit: float
    acceleration_limit: float
    effort_limit: float
    pid_position: PID | None
    pid_velocity: PID | None

    @classmethod
    def from_transport_model(cls, model: transport_models.s.JointConfig) -> 'JointConfiguration':
        return cls(
            name=model.name,
            type=model.type,
            position_limit_min=model.position_limit_min,
            position_limit_max=model.position_limit_max,
            velocity_limit=model.velocity_limit,
            acceleration_limit=model.acceleration_limit,
            effort_limit=model.effort_limit,
            pid_position=PID.from_transport_model(model.pid_position) if model.pid_position else None,
            pid_velocity=PID.from_transport_model(model.pid_velocity) if model.pid_velocity else None,
        )

    def to_transport_model(self) -> transport_models.s.JointConfig:
        return transport_models.s.JointConfig(
            name=self.name,
            type=self.type,
            position_limit_min=self.position_limit_min,
            position_limit_max=self.position_limit_max,
            velocity_limit=self.velocity_limit,
            acceleration_limit=self.acceleration_limit,
            effort_limit=self.effort_limit,
            pid_position=self.pid_position.to_transport_model() if self.pid_position else None,
            pid_velocity=self.pid_velocity.to_transport_model() if self.pid_velocity else None,
        )


@dataclass
class RobotConfiguration:
    """
    Represents the complete configuration of a robot.
    
    :param name: The name of the robot.
    :param n_joint: The number of joints.
    :param joints: List of configurations for each joint.
    """
    name: str
    n_joint: int
    joints: list[JointConfiguration]

    @classmethod
    def from_transport_model(cls, model: transport_models.s.RobotConfig) -> 'RobotConfiguration':
        return cls(
            name=model.name,
            n_joint=model.number_joints,
            joints=[JointConfiguration.from_transport_model(jc) for jc in model.joints],
        )

    def to_transport_model(self) -> transport_models.s.RobotConfig:
        return transport_models.s.RobotConfig(
            name=self.name,
            number_joints=self.n_joint,
            joints=[jc.to_transport_model() for jc in self.joints],
        )


class ControlMode(Enum):
    """
    Enumeration of robot control modes.
    
    - TRAJECTORY: Follow pre-planned trajectories.
    - JOG: Manual jogging control.
    - SPEED: Direct speed control.
    """
    TRAJECTORY = 1
    JOG = 2
    SPEED = 3

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ControlMode) -> 'ControlMode':
        match model.mode.value:
            case 1:
                return cls.TRAJECTORY
            case 2:
                return cls.JOG
            case 3:
                return cls.SPEED
            case _:
                raise ValueError(f"Unknown ControlMode value: {model.mode.value}")

    def to_transport_model(self) -> transport_models.s.ControlMode:
        return transport_models.s.ControlMode(mode_name=transport_models.s.ModeName(self.name.lower()),
                                              mode=transport_models.s.Mode(self.value))


class ExecutorStatus(StrEnum):
    """
    Enumeration of executor statuses for trajectories and programs.
    """
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PAUSED = 'paused'
    STOPPED = 'stopped'

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ExecutorStatus) -> 'ExecutorStatus':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.ExecutorStatus:
        return transport_models.s.ExecutorStatus(self.value)


def get_mtype(_type: type, a: bool = False) -> transport_models.s.MType:
    """
    Get the MType corresponding to a Python type for metrics.
    
    :param _type: The Python type.
    :param a: Whether to return the asynchronous MType variant.
    :return: The corresponding MType enum value.
    :raises TypeError: If the type is not supported for metrics.
    """
    tr_model = transport_models.a if a else transport_models.s
    if _type is str:
        return tr_model.MType.STRING
    elif _type is int:
        return tr_model.MType.INT
    elif _type is float:
        return tr_model.MType.FLOAT
    elif _type is bool:
        return tr_model.MType.BOOL
    elif _type is datetime:
        return tr_model.MType.DATETIME
    elif _type is timedelta:
        return tr_model.MType.DURATION
    else:
        raise TypeError(f"Unsupported metric type: {_type}")


def parse_mtype(mtype: transport_models.s.MType | transport_models.a.MType) -> type:
    """
    Parse an MType to get the corresponding Python type.
    
    :param mtype: The MType enum value.
    :return: The corresponding Python type.
    :raises TypeError: If the MType is not recognized.
    """
    tr_model = transport_models.a if isinstance(mtype, transport_models.a.MType) else transport_models.s
    if mtype is tr_model.MType.STRING:
        return str
    elif mtype is tr_model.MType.INT:
        return int
    elif mtype is tr_model.MType.FLOAT:
        return float
    elif mtype is tr_model.MType.BOOL:
        return bool
    elif mtype is tr_model.MType.DATETIME:
        return datetime
    elif mtype is tr_model.MType.DURATION:
        return timedelta
    else:
        raise TypeError(f"Unsupported metric type: {mtype}")


@dataclass
class Metric:
    """
    Represents a custom metric.
    
    :param name: The name of the metric.
    :param value: The value of the metric as a string.
    :param type: The Python type of the metric value.
    """
    name: str
    value: str
    type: type

    @classmethod
    def from_transport_model(cls, model: transport_models.a.CustomMetric) -> 'Metric':
        return cls(name=model.name, value=model.value, type=parse_mtype(model.m_type))

    def to_transport_model(self) -> transport_models.a.CustomMetric:
        return transport_models.a.CustomMetric(name=self.name, value=self.value, m_type=get_mtype(self.type, a=True))
