DEFAULT_HTTP_PORT = 8443
DEFAULT_MQTT_PORT = 1883

HTTP_PREFIX = '/api'


def MQTT_PREFIX(device_id: str) -> str:
    return 'device/{device_id}'.format(device_id=device_id)
