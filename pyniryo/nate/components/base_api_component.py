from abc import ABC

from pyniryo.nate._internal.http import HttpClient
from pyniryo.nate._internal.mqtt import MqttClient


class BaseAPIComponent(ABC):

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient):
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client
