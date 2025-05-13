from .base_api_component import BaseAPIComponent

from .. import models
from .._internal import paths_gen


class Users(BaseAPIComponent):

    def get_all(self) -> list[models.User]:
        return self._http_client.get(paths_gen.Users.USERS, models.UserList).root

    def create(self, user: models.NewUser) -> models.User:
        return self._http_client.post(paths_gen.Users.USERS, user, models.User)

    def get(self, user_id: str) -> models.User:
        return self._http_client.get(paths_gen.Users.USER.format(user_id=user_id), models.User)

    def delete(self, user_id: str) -> None:
        return self._http_client.delete(paths_gen.Users.USER.format(user_id=user_id), None, None)

    def update(self, user: models.User) -> models.User:
        return self._http_client.patch(paths_gen.Users.USER.format(user_id=user.id), user, models.User)

    def get_tokens(self, user_id: str) -> list[models.Token]:
        return self._http_client.get(paths_gen.Users.USER_TOKENS.format(user_id=user_id), models.TokenList).root

    def create_token(self, user_id: str, token: models.TokenCreation) -> models.Token:
        return self._http_client.post(paths_gen.Users.USER_TOKENS.format(user_id=user_id), token, models.Token)

    def update_password(self, user_id: str, update_password: models.UpdatePassword) -> None:
        return self._http_client.patch(paths_gen.Users.USER_PASSWORD.format(user_id=user_id), update_password, None)
