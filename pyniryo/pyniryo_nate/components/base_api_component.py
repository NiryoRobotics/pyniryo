from abc import ABC

from ..http_client import HttpClient

class BaseAPIComponent(ABC):
    def __init__(self, http_client: HttpClient, mqtt_client):
        self._http_client: HttpClient = http_client
        self._mqtt_client = mqtt_client