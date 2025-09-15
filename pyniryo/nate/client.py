import os
from typing import Type, cast

from .components import Auth, Users, Motion, BaseAPIComponent
from ._internal.http import HttpClient
from ._internal.mqtt import MqttClient
from ._internal.const import HTTP_PORT, MQTT_PORT, API_PREFIX


class Nate:

    def __init__(self, hostname: str | None = None, auth_token: str | None = None, insecure=False):
        """
        Initialize a client to communicate with the Nate API.
        
        :param hostname: The hostname of the Nate API. It can be an IP address or a domain name.
        If None, retrieve it from the environment variable NATE_HOSTNAME. If the environment variable is not set, use localhost.
        :type hostname: str
        :param auth_token: The authentication token to use. If it is a file path, the content of the file will be used.
        """
        hostname = hostname or os.getenv('NATE_HOSTNAME') or 'localhost'
        http_port = os.getenv('NATE_HTTP_PORT') or HTTP_PORT
        mqtt_port = os.getenv('NATE_MQTT_PORT') or MQTT_PORT
        insecure = os.getenv('NATE_INSECURE') is not None

        self.__http_client: HttpClient = HttpClient(hostname, http_port, prefix=API_PREFIX, insecure=insecure)
        self.__mqtt_client: MqttClient = MqttClient(hostname, mqtt_port)

        if auth_token is not None:
            if os.path.exists(auth_token):
                auth_token = open(auth_token).read()
            self.__http_client.set_header('Authorization', f'Bearer {auth_token}')

        # Components are instantiated on demand in order to only create the ones that are used.
        self.__components = {}

    def __get_component(self, cls: Type[BaseAPIComponent]) -> BaseAPIComponent:
        """
        Get a component by name. The components are lazy-loaded, meaning they are created only when first accessed.

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

    @property
    def motion(self) -> Motion:
        """
        Get the motion component.

        :return: The motion component.
        """
        return cast(Motion, self.__get_component(Motion))
