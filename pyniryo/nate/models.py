from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Self

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
class Role(BaseDataClass):
    id: int
    name: str

    @classmethod
    def from_transport_model(cls, model: transport_models.Role) -> Self:
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
    def from_transport_model(cls, model: transport_models.User):
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
    def from_transport_model(cls, model: BaseModel):
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
