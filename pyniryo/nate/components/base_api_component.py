from abc import ABC

from .._internal.http import HttpClient
from .._internal.mqtt import MqttClient


class BaseAPIComponent(ABC):
    """
    Base class for all API components.
    """

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient):
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client
