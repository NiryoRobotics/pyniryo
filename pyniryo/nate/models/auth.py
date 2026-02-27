from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .._internal import transport_models


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
    """

    @classmethod
    def from_transport_model(cls, model: transport_models.a.UserEvent) -> 'UserEvent':
        return cls()

    def to_transport_model(self) -> transport_models.a.UserEvent:
        return transport_models.a.UserEvent()
