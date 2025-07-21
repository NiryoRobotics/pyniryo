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
        self._post_init()

    def _post_init(self) -> None:
        """
        Post-initialization method to be called after the component is initialized.
        This can be overridden by subclasses to perform additional setup.
        """
        pass
