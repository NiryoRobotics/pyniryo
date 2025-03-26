from .const import HTTP_PORT, MQTT_PORT

class Nate:
    def __init__(self, ip_address: str):
        self.__ip_address :str = ip_address
        self.__http_client = ...
        self.__mqtt_client = ...