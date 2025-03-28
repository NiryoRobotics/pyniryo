import os
from typing import Optional

from .http_client import HttpClient
from .const import HTTP_PORT, MQTT_PORT, API_PREFIX
from .components.auth import Auth


class Nate:
    """
    Base client for the Nate API.
    """

    def __init__(self, hostname: str, auth_token: Optional[str] = None):
        """
        Initialize a client.
        :param hostname: The hostname of the Nate API. It can be an IP address or a domain name.
        :param auth_token: The authentication token to use. If it is a file path, the content of the file will be used.
        """
        self.__http_client: HttpClient = HttpClient(hostname, HTTP_PORT, prefix=API_PREFIX)

        if auth_token is not None:
            if os.path.exists(auth_token):
                auth_token = open(auth_token).read()
            self.__http_client.set_header('Authorization', f'Bearer {auth_token}')

        self.__mqtt_client = ...

        self.__auth: Optional[Auth] = None

    @property
    def auth(self) -> Auth:
        """
        Get the authentication component.
        :return: The authentication component.
        """
        if self.__auth is None:
            self.__auth = Auth(self.__http_client, self.__mqtt_client)
        return self.__auth
