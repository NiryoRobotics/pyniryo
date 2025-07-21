from collections.abc import MutableSequence
from dataclasses import dataclass
from datetime import datetime
from strenum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from ._internal import transport_models, utils


@dataclass
class BaseDataClass:

    @classmethod
    def from_transport_model(cls, model):
        raise NotImplementedError()

    def to_transport_model(self):
        raise NotImplementedError()


@dataclass
class BaseSequenceDataClass(BaseDataClass, MutableSequence):

    root: MutableSequence

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
        return utils.new_transport_model(
            {
                "id": self.id,
                "name": self.name,
            },
            transport_models.Role,
        )


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
        return utils.new_transport_model(
            {
                "id": self.id,
                "email": self.email,
                "name": self.name,
                "role": self.role.to_transport_model(),
            },
            transport_models.User,
        )


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
        return utils.new_transport_model(
            {
                "id": self.id,
                "expires_at": self.expires_at,
                "created_at": self.created_at,
                "token": self.token,
            },
            transport_models.Token,
        )


@dataclass
class UserEvent(BaseDataClass):

    @classmethod
    def from_transport_model(cls, model: transport_models.UserEvent) -> 'UserEvent':
        return cls()

    def to_transport_model(self) -> transport_models.UserEvent:
        return utils.new_transport_model(
            {},
            transport_models.UserLoggedIn,
        )


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
        return utils.new_transport_model(
            {"root": self.root},
            transport_models.Joints,
        )


@dataclass
class Pose(BaseSequenceDataClass):
    ...


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
        return utils.new_transport_model(
            {
                "state": self.state.value,
                "message": self.message,
            },
            transport_models.MoveFeedback,
        )
