from abc import ABC

from .._internal.http import HttpClient
from .._internal.mqtt import MqttClient


class BaseAPIComponent(ABC):
    """
    Base class for all API components.
    """

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient, correlation_id: str) -> None:
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client
        self._correlation_id = correlation_id

    def close(self) -> None:
        """
        Close the component and release any resources if needed.
        """
        pass