from datetime import datetime

from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models, mqtt, utils
from .._internal.compat.typing import Optional, Callable
from .. import models

UserLoggedInCallback = Callable[[str, models.UserLoggedIn], None]
UserLoggedOutCallback = Callable[[str, models.UserLoggedOut], None]


class Auth(BaseAPIComponent):
    """
    Authentication component for the API.
    """

    def login(self, email: str, password: str, expires_at: Optional[datetime] = None) -> models.Token:
        """
        Log in to the API.
        :param email: The email of the user.
        :param password: The password of the user.
        :param expires_at: The expiration date of the token.
        :return: The token generated for this login session.
        """
        token = self._http_client.post(
            paths_gen.Login.LOGIN,
            utils.new_transport_model(
                {
                    'email': email, 'password': password, 'expires_at': expires_at
                },
                transport_models.Login,
            ),
            transport_models.Token)
        return models.Token.from_transport_model(token)

    def on_user_logged_in(self, callback: UserLoggedInCallback, user_id: str = None) -> None:
        """
        Set the callback to call when a user logs in.
        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        :param user_id: The user ID to listen to. If not specified, listen to all users.
        """
        topic = f'users/{user_id or mqtt.SINGLE_LEVEL_WILDCARD}/logged-in'

        def callback_wrapper(received_topic: str, user_logged_in: transport_models.UserLoggedIn):
            user_id = mqtt.get_level_from_wildcard(topic, received_topic)[0]
            callback(user_id, models.UserLoggedIn.from_transport_model(user_logged_in))

        self._mqtt_client.subscribe(topic, callback_wrapper, transport_models.UserLoggedIn)

    def on_user_logged_out(self, callback: UserLoggedOutCallback, user_id: str = None) -> None:
        """
        Set the callback to call when a user logs out.
        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        :param user_id: The user ID to listen to. If not specified, listen to all users.
        """
        topic = f'users/{user_id or mqtt.SINGLE_LEVEL_WILDCARD}/logged-out'

        def callback_wrapper(received_topic: str, user_logged_out: transport_models.UserLoggedOut):
            user_id = mqtt.get_level_from_wildcard(topic, received_topic)[0]
            callback(user_id, models.UserLoggedOut.from_transport_model(user_logged_out))

        self._mqtt_client.subscribe(topic, callback_wrapper, transport_models.UserLoggedOut)