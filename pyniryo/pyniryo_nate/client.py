import os
from typing import Optional

from .http_client import HttpClient
from .const import HTTP_PORT, MQTT_PORT, API_PREFIX
from .components.auth import Auth


class Nate:

    def __init__(self, hostname: str, auth_token: Optional[str] = None):
        self.__http_client: HttpClient = HttpClient(hostname, HTTP_PORT, prefix=API_PREFIX)

        if auth_token is not None:
            if os.path.exists(auth_token):
                auth_token = open(auth_token).read()
            self.__http_client.set_header('Authorization', f'Bearer {auth_token}')

        self.__mqtt_client = ...

        self.__auth: Optional[Auth] = None

    @property
    def auth(self) -> Auth:
        if self.__auth is None:
            self.__auth = Auth(self.__http_client, self.__mqtt_client)
        return self.__auth
