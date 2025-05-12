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