import os

from .components import Auth, Users, BaseAPIComponent
from ._internal.compat.typing import Optional, Type, cast
from ._internal.http import HttpClient
from ._internal.mqtt import MqttClient
from ._internal.const import HTTP_PORT, MQTT_PORT, API_PREFIX


class Nate:

    def __init__(self, hostname: str, auth_token: Optional[str] = None):
        """
        Initialize a client to communicate with the Nate API.
        
        :param hostname: The hostname of the Nate API. It can be an IP address or a domain name.
        :type hostname: str
        :param auth_token: The authentication token to use. If it is a file path, the content of the file will be used.
        """
        self.__http_client: HttpClient = HttpClient(hostname, HTTP_PORT, prefix=API_PREFIX)
        self.__mqtt_client: MqttClient = MqttClient(hostname, MQTT_PORT)

        if auth_token is not None:
            if os.path.exists(auth_token):
                auth_token = open(auth_token).read()
            self.__http_client.set_header('Authorization', f'Bearer {auth_token}')

        # Components are instantiated on demand in order to only create the ones that are used.
        self.__components = {}

    def __get_component(self, cls: Type[BaseAPIComponent]) -> BaseAPIComponent:
        """
        Get a component by name.

        :param cls: The class of the component to get.
        :return: The component.
        """
        if cls.__name__ not in self.__components:
            self.__components[cls.__name__] = cls(self.__http_client, self.__mqtt_client)
        return self.__components[cls.__name__]

    @property
    def auth(self) -> Auth:
        """
        Get the authentication component.

        :return: The authentication component.
        """
        return cast(Auth, self.__get_component(Auth))

    @property
    def users(self) -> Users:
        """
        Get the users component.

        :return: The users component.
        """
        return cast(Users, self.__get_component(Users))