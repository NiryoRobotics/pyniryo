import math
import re
from collections.abc import MutableSequence
from dataclasses import dataclass
from datetime import datetime
from typing import Type

from strenum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from ._internal import transport_models
from .exceptions import PyNiryoError, GenerateTrajectoryError, LoadTrajectoryError, ExecuteTrajectoryError


@dataclass
class BaseDataClass:

    @classmethod
    def from_transport_model(cls, model):
        raise NotImplementedError()

    def to_transport_model(self):
        raise NotImplementedError()


@dataclass
class BaseSequenceDataClass(BaseDataClass, MutableSequence):

    root: MutableSequence[float]

    def insert(self, index, value):
        self.root.insert(index, value)

    def __delitem__(self, index):
        del self[index]

    def __getitem__(self, index: int) -> float:
        return self.root[index]

    def __setitem__(self, index: int, value):
        self.root[index] = value

    def __len__(self):
        return len(self.root)


@dataclass
class Role(BaseDataClass):
    id: int
    name: str

    @classmethod
    def from_transport_model(cls, model: transport_models.Role) -> 'Role':
        return cls(
            id=model.id,
            name=model.name,
        )

    def to_transport_model(self) -> transport_models.Role:
        return transport_models.Role(id=self.id, name=self.name)


@dataclass
class User(BaseDataClass):
    id: str
    email: str
    name: str
    role: Role

    @classmethod
    def from_transport_model(cls, model: transport_models.User) -> 'User':
        return cls(
            id=str(model.id),
            email=str(model.email),
            name=model.name,
            role=Role.from_transport_model(model.role),
        )

    def to_transport_model(self) -> transport_models.User:
        return transport_models.User(id=UUID(self.id),
                                     email=self.email,
                                     name=self.name,
                                     role=self.role.to_transport_model())


@dataclass
class Token(BaseDataClass):
    id: UUID
    expires_at: datetime
    created_at: datetime
    token: str

    @classmethod
    def from_transport_model(cls, model: BaseModel) -> 'Token':
        return cls(
            id=model.id,
            expires_at=model.expires_at,
            created_at=model.created_at,
            token=model.token,
        )

    def to_transport_model(self) -> transport_models.Token:
        return transport_models.Token(id=self.id,
                                      expires_at=self.expires_at,
                                      created_at=self.created_at,
                                      token=self.token)


@dataclass
class UserEvent(BaseDataClass):

    @classmethod
    def from_transport_model(cls, model: transport_models.UserEvent) -> 'UserEvent':
        return cls()

    def to_transport_model(self) -> transport_models.UserEvent:
        return transport_models.UserLoggedIn()


UserLoggedIn = UserEvent
UserLoggedOut = UserEvent


@dataclass
class Joints(BaseSequenceDataClass):

    root: list[float]

    def __init__(self, *joints: float):
        self.root = list(joints)

    @classmethod
    def from_transport_model(cls, model: transport_models.Joints) -> 'Joints':
        return cls(*model.root)

    def to_transport_model(self) -> transport_models.Joints:
        return transport_models.Joints(root=self.root)


@dataclass
class Pose(BaseDataClass):
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float
    rw: float

    @classmethod
    def from_transport_model(cls, model: transport_models.Pose) -> 'Pose':
        return cls(
            x=model.position.x,
            y=model.position.y,
            z=model.position.z,
            rx=model.orientation.x,
            ry=model.orientation.y,
            rz=model.orientation.z,
            rw=model.orientation.w,
        )

    def to_transport_model(self) -> transport_models.Pose:
        return transport_models.Pose(
            position=transport_models.Point(x=self.x, y=self.y, z=self.z),
            orientation=transport_models.Quaternion(x=self.rx, y=self.ry, z=self.rz, w=self.rw),
        )

    @classmethod
    def with_rpy(cls, x, y, z, roll, pitch, yaw) -> 'Pose':
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        rw = cr * cp * cy + sr * sp * sy
        rx = sr * cp * cy - cr * sp * sy
        ry = cr * sp * cy + sr * cp * sy
        rz = cr * cp * sy - sr * sp * cy

        return cls(x, y, z, rx, ry, rz, rw)


MoveTarget = Pose | Joints


class MoveState(StrEnum):
    UNKNOWN = "unknown"
    IDLE = "idle"
    GEN_TRAJ = "generating_trajectory"
    ERR_GEN_TRAJ = "error_generating_trajectory"
    LOAD_TRAJ = "loading_trajectory"
    ERR_LOAD_TRAJ = "error_loading_trajectory"
    EXEC_TRAJ = "executing_trajectory"
    ERR_EXEC_TRAJ = "error_executing_trajectory"
    DONE = "done"

    def is_error(self) -> bool:
        return self.name.startswith("ERR_")

    def is_final(self) -> bool:
        return self == MoveState.DONE or self.is_error()

    def get_exception(self) -> Type[PyNiryoError]:
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
class MoveFeedback(BaseDataClass):
    state: MoveState
    message: str

    @classmethod
    def from_transport_model(cls, model: transport_models.MoveFeedback) -> 'MoveFeedback':
        return cls(
            state=MoveState(model.state),
            message=model.message,
        )

    def to_transport_model(self) -> transport_models.MoveFeedback:
        return transport_models.MoveFeedback(state=self.state.value, message=self.message)


class ProgramType(StrEnum):
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

    def __lt__(self, other):
        if not isinstance(other, ProgramType):
            return NotImplemented
        return self.__key() < other.__key()

    @classmethod
    def python(cls) -> 'ProgramType':
        """
        Get the latest supported Python version.
        :return: The latest supported Python version.
        """
        return max(e for e in cls if e.__key()[0] == 'python')

    @classmethod
    def from_transport_model(cls, model: transport_models.Type) -> 'ProgramType':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.Type:
        return transport_models.Type(str(self))


@dataclass
class Program(BaseDataClass):
    id: str
    name: str
    type: ProgramType

    @classmethod
    def from_transport_model(cls, model: transport_models.Program) -> 'Program':
        return cls(
            id=str(model.id),
            name=model.name,
            type=ProgramType.from_transport_model(model.type),
        )

    def to_transport_model(self) -> transport_models.Program:
        return transport_models.Program(
            id=UUID(self.id),
            name=self.name,
            type=transport_models.Type(self.type.value),
        )


@dataclass
class ProgramExecutionContext(BaseDataClass):
    environment: dict[str, str]
    arguments: list[str]

    @classmethod
    def from_transport_model(cls, model: transport_models.ProgramExecutionContext) -> 'ProgramExecutionContext':
        return cls(
            environment=model.environment or {},
            arguments=model.arguments or [],
        )

    def to_transport_model(self) -> transport_models.ProgramExecutionContext:
        return transport_models.ProgramExecutionContext(
            environment=self.environment,
            arguments=self.arguments,
        )


@dataclass
class ProgramExecution(BaseDataClass):
    id: str
    program_id: str
    context: ProgramExecutionContext
    startedAt: datetime
    finishedAt: datetime
    output: str
    exitCode: int

    @classmethod
    def from_transport_model(cls, model: transport_models.ProgramExecution) -> 'ProgramExecution':
        return cls(
            id=str(model.id),
            program_id=str(model.programId),
            context=ProgramExecutionContext.from_transport_model(model.context),
            startedAt=model.startedAt,
            finishedAt=model.finishedAt,
            output=model.output,
            exitCode=model.exitCode,
        )

    def to_transport_model(self) -> transport_models.ProgramExecution:
        return transport_models.ProgramExecution(id=UUID(self.id),
                                                 programId=UUID(self.program_id),
                                                 context=self.context.to_transport_model(),
                                                 startedAt=self.startedAt,
                                                 finishedAt=self.finishedAt,
                                                 output=self.output,
                                                 exitCode=self.exitCode)


@dataclass
class ExecutionOutput:
    output: str

    @classmethod
    def from_transport_model(cls, model: transport_models.ProgramExecutionOutput) -> 'ExecutionOutput':
        return cls(output=model.output)

    def to_transport_model(self) -> transport_models.ProgramExecutionOutput:
        return transport_models.ProgramExecutionOutput(output=self.output)


class ExecutionStatusStatus(StrEnum):
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PAUSED = 'paused'

    def is_error(self) -> bool:
        return self == ExecutionStatusStatus.FAILED

    def is_final(self) -> bool:
        return self == ExecutionStatusStatus.COMPLETED or self.is_error()


@dataclass
class ExecutionStatus:
    status: ExecutionStatusStatus

    @classmethod
    def from_transport_model(cls, model: transport_models.ProgramExecutionStatus) -> 'ExecutionStatus':
        return cls(status=ExecutionStatusStatus(model.status))

    def to_transport_model(self) -> transport_models.ProgramExecutionStatus:
        return transport_models.ProgramExecutionStatus(status=self.status)
