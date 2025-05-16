from datetime import datetime

from .base_api_component import BaseAPIComponent

from .._internal import paths_gen, transport_models, utils
from .. import models


class Users(BaseAPIComponent):

    def get_all(self) -> list[models.User]:
        """
        Get all the registered users.

        :return: The list of all the users.
        """
        users = self._http_client.get(
            paths_gen.Users.USERS,
            transport_models.UserList,
        )
        return [models.User.from_transport_model(user) for user in users.root]

    def create(self, email: str, name: str, role_id: int, password: str) -> models.User:
        """
        Create a new user.

        :param email: The email of the user.
        :param name: The name of the user.
        :param role_id: The role ID of the user.
        :param password: The password of the user.
        """
        user = self._http_client.post(
            paths_gen.Users.USERS,
            utils.new_transport_model(
                {
                    'email': email, 'name': name, 'role_id': role_id, 'password': password
                },
                transport_models.NewUser,
            ),
            transport_models.User,
        )
        return models.User.from_transport_model(user)

    def get(self, user_id: str) -> models.User:
        """
        Get a user by its ID.

        :param user_id: The ID of the user.
        :return: The corresponding user.
        """
        user = self._http_client.get(
            paths_gen.Users.USER.format(user_id=user_id),
            transport_models.User,
        )
        return models.User.from_transport_model(user)

    def delete(self, user_id: str) -> None:
        """
        Delete a user by its ID.

        :param user_id: The ID of the user.
        :return: None
        """
        return self._http_client.delete(
            paths_gen.Users.USER.format(user_id=user_id),
        )

    def update(self, user: models.User) -> models.User:
        """
        Update a user.

        :param user: The user with its new properties.
        :return: The updated user.
        """
        user = self._http_client.patch(
            paths_gen.Users.USER.format(user_id=user.id),
            user.to_transport_model(),
            transport_models.User,
        )
        return models.User.from_transport_model(user)

    def get_tokens(self, user_id: str) -> list[models.Token]:
        """
        Get all the tokens of a user.

        :param user_id: The ID of the user.
        :return: The list of all the tokens of the user.
        """
        tokens = self._http_client.get(
            paths_gen.Users.USER_TOKENS.format(user_id=user_id),
            transport_models.TokenList,
        )
        return [models.Token.from_transport_model(token) for token in tokens.root]

    def create_token(self, user_id: str, expires_at: datetime) -> models.Token:
        """
        Create a new token for a user.

        :param user_id: The ID of the user.
        :param expires_at: The expiration date of the token.
        :return: The created token.
        """
        token = self._http_client.post(
            paths_gen.Users.USER_TOKENS.format(user_id=user_id),
            transport_models.TokenCreation(expires_at=expires_at),
            transport_models.Token,
        )
        return models.Token.from_transport_model(token)

    def update_password(self, user_id: str, old_password: str, new_password: str) -> None:
        """
        Update the password of a user.

        :param user_id: The ID of the user.
        :param old_password: The old password of the user.
        :param new_password: The new password of the user.
        :return: None
        """
        return self._http_client.patch(
            paths_gen.Users.USER_PASSWORD.format(user_id=user_id),
            transport_models.UpdatePassword(old_password=old_password, new_password=new_password),
            None,
        )
