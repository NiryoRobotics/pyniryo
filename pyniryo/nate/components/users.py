from datetime import datetime

from .base_api_component import BaseAPIComponent

from .._internal import paths_gen, transport_models, utils
from .. import models


class Users(BaseAPIComponent):

    def get_all(self) -> list[models.User]:
        users = self._http_client.get(
            paths_gen.Users.USERS,
            transport_models.UserList,
        )
        return [models.User.from_transport_model(user) for user in users.root]

    def create(self, email: str, name: str, role_id: int, password: str) -> models.User:
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
        user = self._http_client.get(
            paths_gen.Users.USER.format(user_id=user_id),
            transport_models.User,
        )
        return models.User.from_transport_model(user)

    def delete(self, user_id: str) -> None:
        return self._http_client.delete(
            paths_gen.Users.USER.format(user_id=user_id),
        )

    def update(self, user: models.User) -> models.User:
        user = self._http_client.patch(
            paths_gen.Users.USER.format(user_id=user.id),
            user.to_transport_model(),
            transport_models.User,
        )
        return models.User.from_transport_model(user)

    def get_tokens(self, user_id: str) -> list[models.Token]:
        tokens = self._http_client.get(
            paths_gen.Users.USER_TOKENS.format(user_id=user_id),
            transport_models.TokenList,
        )
        return [models.Token.from_transport_model(token) for token in tokens.root]

    def create_token(self, user_id: str, expires_at: datetime) -> models.Token:
        token = self._http_client.post(
            paths_gen.Users.USER_TOKENS.format(user_id=user_id),
            transport_models.TokenCreation(expires_at=expires_at),
            transport_models.Token,
        )
        return models.Token.from_transport_model(token)

    def update_password(self, user_id: str, old_password: str, new_password: str) -> None:
        return self._http_client.patch(
            paths_gen.Users.USER_PASSWORD.format(user_id=user_id),
            transport_models.UpdatePassword(old_password=old_password, new_password=new_password),
        )
