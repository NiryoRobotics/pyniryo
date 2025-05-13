from typing import Optional, Callable
from datetime import datetime

from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models, mqtt

UserLoggedInCallback = Callable[[str, transport_models.UserLoggedIn], None]


class Auth(BaseAPIComponent):
    """
    Authentication component for the API.
    """

    def login(self, email: str, password: str, expires_at: Optional[datetime] = None) -> transport_models.Token:
        """
        Log in to the API.
        :param email: The email of the user.
        :param password: The password of the user.
        :param expires_at: The expiration date of the token.
        :return: The token generated for this login session.
        """
        return self._http_client.post(paths_gen.Login.LOGIN,
                                      transport_models.Login(email=email, password=password, expires_at=expires_at),
                                      transport_models.Token)

    def on_user_logged_in(self, callback: UserLoggedInCallback, user_id: str = None) -> None:
        """
        Set the callback to call when a user logs in.
        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        :param user_id: The user ID to listen to. If None, listen to all users.
        """
        topic = f'users/{user_id or "+"}/logged-in'

        def callback_wrapper(_, __, message: mqtt.MQTTMessage):
            user_id = mqtt.get_level_from_wildcard(topic, message.topic)
            user_logged_in = transport_models.UserLoggedIn.model_validate_json(message.payload)
            callback(user_id, user_logged_in)

        self._mqtt_client.subscribe(topic, callback_wrapper)
