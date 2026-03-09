from datetime import datetime

from .base_api_component import BaseAPIComponent

from .._internal import paths_gen, transport_models
from .._internal.transport_models import EmptyPayload
from ..models import User, Token


class Users(BaseAPIComponent):
    """
    Users component for managing user accounts.
    
    This component provides methods for:
    - Creating, retrieving, updating, and deleting users
    - Managing user tokens
    - Updating user passwords
    """

    def get_all(self) -> list[User]:
        """
        Get all the registered users.

        :return: The list of all the users.
        """
        users = self._http_client.get(
            paths_gen.Authentication.GET_ALL_USERS,
            transport_models.UserList,
        )
        return [User.from_transport_model(user) for user in users.root]

    def create(self, email: str, name: str, role_id: int, password: str) -> User:
        """
        Create a new user.

        :param email: The email of the user.
        :param name: The name of the user.
        :param role_id: The role ID of the user.
        :param password: The password of the user.
        :return: The created user.
        """
        user = self._http_client.post(
            paths_gen.Authentication.CREATE_USER,
            transport_models.s.User,
            transport_models.s.NewUser(email=email, name=name, role_id=role_id, password=password),
        )
        return User.from_transport_model(user)

    def get(self, user_id: str) -> User:
        """
        Get a user by its ID.

        :param user_id: The ID of the user.
        :return: The corresponding user.
        """
        user = self._http_client.get(
            paths_gen.Authentication.GET_USER.format(user_id=user_id),
            transport_models.s.User,
        )
        return User.from_transport_model(user)

    def delete(self, user_id: str) -> None:
        """
        Delete a user by its ID.

        :param user_id: The ID of the user.
        :return: None
        """
        self._http_client.delete(
            paths_gen.Authentication.DELETE_USER.format(user_id=user_id),
            EmptyPayload,
        )

    def update(self, user: User) -> User:
        """
        Update a user.

        :param user: The user with its new properties.
        :return: The updated user.
        """
        response = self._http_client.patch(
            paths_gen.Authentication.UPDATE_USER.format(user_id=user.id),
            transport_models.s.User,
            user.to_transport_model(),
        )
        return User.from_transport_model(response)

    def get_tokens(self, user_id: str) -> list[Token]:
        """
        Get all the tokens of a user.

        :param user_id: The ID of the user.
        :return: The list of all the tokens of the user.
        """
        tokens = self._http_client.get(
            paths_gen.Authentication.GET_USER_TOKENS.format(user_id=user_id),
            transport_models.TokenList,
        )
        return [Token.from_transport_model(token) for token in tokens.root]

    def create_token(self, user_id: str, expires_at: datetime) -> Token:
        """
        Create a new token for a user.

        :param user_id: The ID of the user.
        :param expires_at: The expiration date of the token.
        :return: The created token.
        """
        token = self._http_client.post(
            paths_gen.Authentication.CREATE_USER_TOKEN.format(user_id=user_id),
            transport_models.s.Token,
            transport_models.s.TokenCreation(expires_at=expires_at),
        )
        return Token.from_transport_model(token)

    def update_password(self, user_id: str, old_password: str, new_password: str) -> None:
        """
        Update the password of a user.

        :param user_id: The ID of the user.
        :param old_password: The old password of the user.
        :param new_password: The new password of the user.
        :return: None
        """
        self._http_client.patch(
            paths_gen.Authentication.UPDATE_USER_PASSWORD.format(user_id=user_id),
            EmptyPayload,
            transport_models.s.UpdatePassword(old_password=old_password, new_password=new_password),
        )
