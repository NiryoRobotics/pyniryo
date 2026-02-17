DEFAULT_HTTP_PORT = 8080
DEFAULT_MQTT_PORT = 1883

NULL_TOPIC = 'void'


def MQTT_PREFIX(device_id: str) -> str:
    return 'device/{device_id}'.format(device_id=device_id)
