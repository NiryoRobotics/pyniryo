import logging
import os
from typing import Type, cast

from .components import Auth, Users, Robot, BaseAPIComponent, Device
from ._internal import paths_gen, transport_models
from ._internal.http import HttpClient
from ._internal.mqtt import MqttClient
from ._internal.const import DEFAULT_HTTP_PORT, DEFAULT_MQTT_PORT, HTTP_PREFIX, MQTT_PREFIX

logger = logging.getLogger(__name__)


class Nate:

    def __init__(self, hostname: str | None = None, token: str = None, login: tuple[str, str] = None):
        """
        Initialize a client to communicate with the Nate API.
        
        :param hostname: The hostname of the Nate API. It can be an IP address or a domain name.
        If None, retrieve it from the environment variable NATE_HOSTNAME. If the environment variable is not set, use localhost.
        :type hostname: str
        :param token: The token to use for authentication. If None, retrieve it from the environment variable NATE_TOKEN.
        :type token: str
        :param login: A tuple containing the username and password to use for authentication. Omitted if using an auth token.
        If None, retrieve them from the environment variables NATE_USERNAME and NATE_PASSWORD.
        """
        hostname = hostname or os.getenv('NATE_HOSTNAME') or 'localhost'
        token = token or os.getenv('NATE_TOKEN')
        login = login or (os.getenv('NATE_USERNAME'), os.getenv('NATE_PASSWORD'))

        http_port = os.getenv('NATE_HTTP_PORT') or DEFAULT_HTTP_PORT
        mqtt_port = os.getenv('NATE_MQTT_PORT') or DEFAULT_MQTT_PORT
        insecure = os.getenv('NATE_INSECURE') is not None

        ##########################################################################################
        ## Bootstrap: fetch all needed data to properly initiate the client and its components. ##
        ##########################################################################################

        http_client = HttpClient(hostname, http_port, token, prefix=HTTP_PREFIX, insecure=insecure)

        # Token
        if token is None:
            if len(login) != 2:
                raise ValueError("authentication with username and password requires both username and password")
            username, password = login
            response = http_client.post(
                paths_gen.Auth.LOGIN,
                transport_models.Login(login=username, password=password),
                transport_models.Token,
            )
            token = response.token

        # Device ID
        resp = http_client.get(paths_gen.Device.ID, transport_models.DeviceID)
        device_id = resp.device_id

        # Components are instantiated on demand in order to only create the ones that are used.
        self.__components = {}

        self.__http_client: HttpClient = HttpClient(hostname, http_port, token, prefix=HTTP_PREFIX, insecure=insecure)
        self.__mqtt_client: MqttClient = MqttClient(hostname, mqtt_port, token, prefix=MQTT_PREFIX(device_id))

        self.auth = Auth(self.__http_client, self.__mqtt_client)
        self.users = Users(self.__http_client, self.__mqtt_client)
        self.robot = Robot(self.__http_client, self.__mqtt_client)
        self.device = Device(self.__http_client, self.__mqtt_client)
