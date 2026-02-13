import json
import threading
from base64 import b64encode
from enum import Enum
from typing import List, Dict, Tuple
from uuid import uuid4
import logging

from paho.mqtt.client import Client, MQTTv5
from pydantic import BaseModel, ValidationError

from ..exceptions import InternalError, get_msg_from_errors
from typing import Callable, TypeVar, Type

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
Callback = Callable[[str, T], None]

SINGLE_LEVEL_WILDCARD = '+'
MULTI_LEVEL_WILDCARD = '#'


class Qos(Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class MqttClient:

    def __init__(self, hostname: str, port: int, token: str, prefix: str = ''):
        """
        Initialize the MQTT client.
        :param hostname: The hostname of the MQTT broker.
        :param port: The port of the MQTT broker.
        """
        self.__hostname = hostname
        self.__port = port
        self.__client_id = f'pyniryo-{b64encode(uuid4().bytes).decode()}'
        self.__prefix = prefix

        self.__subscribers_lock = threading.Lock()
        self.__subscribers: Dict[str, Tuple[Type[BaseModel], List[Callback]]] = {}

        self.__mqtt_client = Client(client_id=self.__client_id, userdata=None, protocol=MQTTv5)
        self.__mqtt_client.username_pw_set(username='token', password=token)
        self.__mqtt_client.on_message = self.__on_message
        self.__mqtt_client.connect(self.__hostname, self.__port)
        self.__mqtt_client.loop_start()

    def disconnect(self):
        """
        Disconnect the MQTT client.
        """
        self.__mqtt_client.loop_stop()
        self.__mqtt_client.disconnect()

    def __del__(self):
        try:
            self.__mqtt_client
        except AttributeError:
            return
        if self.__mqtt_client.is_connected():
            self.disconnect()

    def publish(self, topic: str, data: BaseModel, qos: Qos = Qos.AT_MOST_ONCE) -> None:
        """
        Publish a message to a topic.
        :param topic: The topic to publish to.
        :param data: The data to publish.
        :param qos: The QoS level to publish with.
        """
        if self.__prefix != '':
            topic = f'{self.__prefix}/{topic}'

        encoded_data = json.dumps(data.model_dump(mode='json'))

        self.__mqtt_client.publish(topic, encoded_data, qos=qos.value)

    def subscribe(self, topic: str, callback: Callback, payload_model: Type[T]) -> None:
        """
        Subscribe to a topic.
        :param topic: The topic to subscribe to.
        :param callback: The callback to call when a message is received.
        :param payload_model: The model to use for the payload. If None, no model is used.
        """
        if not issubclass(payload_model, BaseModel):
            raise TypeError(f'Invalid type {payload_model.__name__} for response model.')

        if self.__prefix != '':
            topic = f'{self.__prefix}/{topic}'

        with self.__subscribers_lock:
            new_subscriber = topic not in self.__subscribers

            if new_subscriber:
                self.__subscribers[topic] = (payload_model, [])

            self.__subscribers[topic][1].append(callback)

            # subscribe at the end to ensure the callback is registered before receiving messages
            if new_subscriber:
                self.__mqtt_client.subscribe(topic, qos=2)

    def unsubscribe(self, callback: Callable) -> None:
        """
        Unsubscribe a callback from a topic.
        :param callback: The callback to unsubscribe from.
        """
        topics_to_remove = []
        for topic, (payload_model, callbacks) in self.__subscribers.items():
            if callback in callbacks:
                callbacks.remove(callback)
                if len(callbacks) == 0:
                    topics_to_remove.append(topic)

        with self.__subscribers_lock:
            for topic in topics_to_remove:
                del self.__subscribers[topic]
                self.__mqtt_client.unsubscribe(topic)

    def __on_message(self, _client, _userdata, message):
        with self.__subscribers_lock:
            if message.topic not in self.__subscribers:
                logger.warning(f'No subscribers for topic {message.topic}. Message ignored: {message.payload}')
                return

            payload_model, callbacks = self.__subscribers[message.topic]
        try:
            model = payload_model.model_validate_json(message.payload) if payload_model else None
        except ValidationError as e:
            msg = f'Invalid payload for topic {message.topic}: {message.payload}. {get_msg_from_errors(e.errors())}'
            raise InternalError(msg) from e

        for callback in callbacks:
            try:
                callback(message.topic, model)
            except Exception as e:
                logger.error(f'Error in callback {callback.__qualname__} for topic {message.topic}: {e}')


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
