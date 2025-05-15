from base64 import b64encode
from typing import Callable, TypeVar, Optional, Type
from uuid import uuid4

from paho.mqtt.client import Client, MQTTv5, MQTTMessage
from pydantic import BaseModel, ValidationError

from ..exceptions import InternalError, get_msg_from_errors, ClientError

T = TypeVar("T", bound=Optional[BaseModel])

SINGLE_LEVEL_WILDCARD = '+'
MULTI_LEVEL_WILDCARD = '#'


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

    def subscribe(self, topic: str, callback: Callable[[str, T], None], payload_model: Type[T] = None) -> None:
        """
        Subscribe to a topic.
        :param topic: The topic to subscribe to.
        :param callback: The callback to call when a message is received.
        :param payload_model: The model to use for the payload. If None, no model is used.
        """
        if payload_model is not None and not issubclass(payload_model, BaseModel):
            raise TypeError(f'Invalid type {payload_model.__name__} for response model.')

        def callback_wrapper(_, __, message: MQTTMessage):
            if payload_model is None:
                model = None
            else:
                try:
                    model = payload_model.model_validate(message.payload)
                except ValidationError as e:
                    raise InternalError(get_msg_from_errors(e.errors())) from e
            try:
                callback(str(message.payload), model)
            except Exception as e:
                raise ClientError(f'Error in callback for topic {message.payload}: {e}') from e

        self.__mqtt_client.message_callback_add(topic, callback_wrapper)
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
    levels = []
    for s_level, r_level in zip(subscribed_topic.split('/'), received_topic.split('/'), strict=True):
        if s_level == wildcard:
            levels.append(r_level)
    return levels
