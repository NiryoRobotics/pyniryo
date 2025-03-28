from abc import ABC

from ..http import HttpClient
from ..mqtt import MqttClient


class BaseAPIComponent(ABC):

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient):
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client
