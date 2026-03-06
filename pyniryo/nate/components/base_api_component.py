import logging
from abc import ABC

from .._internal.http import HttpClient
from .._internal.mqtt import MqttClient

logger = logging.getLogger(__name__)


class BaseAPIComponent(ABC):
    """
    Base class for all API components.
    """

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient, correlation_id: str) -> None:
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client
        self._correlation_id = correlation_id
        self._closed = False

    def close(self) -> None:
        """
        Close the component and release any resources if needed.
        """
        if self._closed:
            return
        self._close()
        self._closed = True

    def _close(self) -> None:
        """
        Internal method to be overridden by subclasses for cleanup logic.
        """
        pass
