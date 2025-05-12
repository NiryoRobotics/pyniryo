from typing import Optional, Callable
from datetime import datetime

from .base_api_component import BaseAPIComponent
from ..models import Token, Login, UserLoggedIn
from .._internal import paths_gen
from .._internal.mqtt import MQTTMessage, get_level_from_wildcard

UserLoggedInCallback = Callable[[str, UserLoggedIn], None]


class Auth(BaseAPIComponent):
    """
    Authentication component for the API.
    """

    def login(self, email: str, password: str, expires_at: Optional[datetime] = None) -> Token:
        """
        Log in to the API.
        :param email: The email of the user.
        :param password: The password of the user.
        :param expires_at: The expiration date of the token.
        :return: The token generated for this login session.
        """
        return self._http_client.post(paths_gen.Login.LOGIN,
                                      Login(email=email, password=password, expires_at=expires_at),
                                      Token)

    def on_user_logged_in(self, callback: UserLoggedInCallback) -> None:
        """
        Set the callback to call when a user logs in.
        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        """
        topic = 'users/+/logged-in'

        def callback_wrapper(_, __, message: MQTTMessage):
            user_id = get_level_from_wildcard(topic, message.topic)
            user_logged_in = UserLoggedIn.model_validate_json(message.payload)
            callback(user_id, user_logged_in)

        self._mqtt_client.subscribe(topic, callback_wrapper)
