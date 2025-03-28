from base64 import b64encode
from typing import Callable, Any
from uuid import uuid4

from paho.mqtt.client import Client, MQTTv5, MQTTMessage as PahoMQTTMessage

# This is a type alias to prevent paho imports in the rest of the code.
MQTTMessage = PahoMQTTMessage


class MqttClient:

    def __init__(self, hostname: str, port: int):
        """
        Initialize the MQTT client.
        :param hostname: The hostname of the MQTT broker.
        :param port: The port of the MQTT broker.
        """
        client_id = f'pyniryo-{b64encode(uuid4().bytes).decode()}'
        self.__mqtt_client = Client(client_id=client_id, userdata=None, protocol=MQTTv5)
        self.__mqtt_client.connect(hostname, port)
        self.__mqtt_client.loop_start()

    def __del__(self):
        """
        Disconnect the MQTT client when the object is deleted.
        """
        self.__mqtt_client.loop_stop()
        self.__mqtt_client.disconnect()

    def subscribe(self, topic: str, callback: Callable[[Client, Any, PahoMQTTMessage], None]) -> None:
        """
        Subscribe to a topic.
        :param topic: The topic to subscribe to.
        :param callback: The callback to call when a message is received.
        callback: The callback to call when a message is received.
        """
        self.__mqtt_client.message_callback_add(topic, callback)
        self.__mqtt_client.subscribe(topic)


def get_level_from_wildcard(subscribed_topic: str, received_topic: str, wildcard: str = '+') -> str:
    """
    Get the wildcarded levels by comparing the subscribed topic and the received topic.
    :param subscribed_topic: The topic subscribed to.
    :param received_topic: The topic received.
    :param wildcard: The wildcard to use.
    :return: The level of the received topic.

    Example:
    get_level_from_wildcard('a/+/topic', 'a/fabulous/topic') -> 'fabulous'
    """
    tmp = received_topic
    for x in subscribed_topic.split(wildcard):
        tmp = tmp.replace(x, '')
    return tmp
