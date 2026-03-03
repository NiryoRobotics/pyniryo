from datetime import datetime
from typing import Callable

from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models, mqtt, topics_gen
from ..models import Token, UserEvent

UserLoggedInCallback = Callable[[str, UserEvent], None]
UserLoggedOutCallback = Callable[[str, UserEvent], None]


class Auth(BaseAPIComponent):
    """
    Authentication component for managing user sessions and monitoring login/logout events.
    
    This component provides methods for:
    - Logging in to obtain authentication tokens
    - Monitoring user login and logout events via callbacks
    """

    def login(self, email: str, password: str, expires_at: datetime | None = None) -> Token:
        """
        Log in to the API.

        :param email: The email of the user.
        :param password: The password of the user.
        :param expires_at: The expiration date of the token.
        :return: The token generated for this login session.
        """
        token = self._http_client.post(
            paths_gen.Authentication.LOGIN,
            transport_models.s.Token,
            transport_models.s.Login(login=email, password=password, expires_at=expires_at),
        )
        return Token.from_transport_model(token)

    def on_user_logged_in(self, callback: UserLoggedInCallback, user_id: str = None) -> None:
        """
        Set the callback to call when a user logs in.

        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        :param user_id: The user ID to listen to. If not specified, listen to all users.
        """
        topic = self._mqtt_client.format(topics_gen.Users.USER_LOGGED_IN, user_id=user_id or mqtt.Wildcard.SINGLE_LEVEL)

        def callback_wrapper(received_topic: str, user_logged_in: transport_models.a.UserEvent):
            user_id = mqtt.get_level_from_wildcard(topic, received_topic)[0]
            callback(user_id, UserEvent.from_transport_model(user_logged_in))

        self._mqtt_client.subscribe(topic, callback_wrapper, transport_models.a.UserEvent)

    def on_user_logged_out(self, callback: UserLoggedOutCallback, user_id: str = None) -> None:
        """
        Set the callback to call when a user logs out.

        :param callback: The callback to call. The callback must take the user ID and the payload as parameters.
        :param user_id: The user ID to listen to. If not specified, listen to all users.
        """
        topic = f'users/{user_id or mqtt.Wildcard.SINGLE_LEVEL}/logged-out'

        def callback_wrapper(received_topic: str, user_logged_out: transport_models.a.UserEvent):
            user_id = mqtt.get_level_from_wildcard(topic, received_topic)[0]
            callback(user_id, UserEvent.from_transport_model(user_logged_out))

        self._mqtt_client.subscribe(topic, callback_wrapper, transport_models.a.UserEvent)
