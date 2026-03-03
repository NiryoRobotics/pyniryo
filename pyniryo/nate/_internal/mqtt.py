import json
import string
import threading
from base64 import b64encode
from enum import Enum
from typing import Dict, Callable, TypeVar, Type
import logging

from paho.mqtt.client import Client, MQTTv5, CallbackAPIVersion
from pydantic import BaseModel
from strenum import StrEnum

from ..models import Unsubscribe

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
Callback = Callable[[str, T], None]


class Wildcard(StrEnum):
    SINGLE_LEVEL = '+'
    MULTI_LEVEL = '#'


class Qos(Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class TopicFormatter(string.Formatter):

    def __init__(self, **kwargs: str):
        super().__init__()
        self.base_values = kwargs

    @staticmethod
    def has_placeholders_left(topic: str) -> bool:
        return '{' in topic or '}' in topic

    def get_value(self, key, args, kwargs):
        if key in self.base_values:
            return self.base_values[key]

        try:
            return super().get_value(key, args, kwargs)
        except KeyError as e:
            raise ValueError(f'Missing value for placeholder "{key}".') from e


class _Subscription:

    def __init__(self, topic: str, payload_model: Type[BaseModel]):
        self._topic = topic
        self._payload_model = payload_model
        self._callbacks_lock = threading.Lock()
        self._callbacks: Dict[int, Callback] = {}

    def internal_callback(self, _client, _userdata, message):
        received_topic = message.topic
        payload = message.payload

        model = self._payload_model.model_validate_json(payload)
        with self._callbacks_lock:
            for callback in self._callbacks.values():
                try:
                    callback(received_topic, model)
                except Exception:
                    logger.exception(f'Error in callback {callback.__qualname__} for topic {self._topic}')

    def add(self, callback: Callback) -> int:
        with self._callbacks_lock:
            cb_ix = len(self._callbacks)
            self._callbacks[cb_ix] = callback
        return cb_ix

    def rm(self, cb_ix: int) -> None:
        with self._callbacks_lock:
            if cb_ix not in self._callbacks:
                raise ValueError(f'No callback at index {cb_ix} for topic {self._topic}.')
            del self._callbacks[cb_ix]

    @property
    def is_stale(self) -> bool:
        return len(self._callbacks) == 0


class MqttClient:

    def __init__(self, hostname: str, port: int, device_id: str, correlation_id: str):
        """
        Initialize the MQTT client.
        :param hostname: The hostname of the MQTT broker.
        :param port: The port of the MQTT broker.
        """
        self.__hostname = hostname
        self.__port = port

        self.__formatter = TopicFormatter(device_id=device_id)

        self.__client_id = f'pyniryo-{b64encode(correlation_id.encode()).decode()}'

        self.__subscribers_lock = threading.Lock()
        self.__subscribers: Dict[str, _Subscription] = {}

        self.__mqtt_client = Client()

    def __init_client(self, token: str):
        if self.__mqtt_client.is_connected():
            self.disconnect()

        self.__mqtt_client = Client(callback_api_version=CallbackAPIVersion.VERSION2,
                                    client_id=self.__client_id,
                                    protocol=MQTTv5)
        self.__mqtt_client.on_message = lambda _, __, m: logger.error(f'Received message on topic {m.topic} with no '
                                                                      f'subscribers. Message ignored: {m.payload}')
        self.__mqtt_client.username_pw_set(username='token', password=token)
        self.__mqtt_client.connect(self.__hostname, self.__port)
        self.__mqtt_client.loop_start()

        with self.__subscribers_lock:
            old_subscribers = self.__subscribers.copy()
            self.__subscribers = {}

        for topic, (payload_model, callbacks) in old_subscribers.items():
            for callback in callbacks:
                self.subscribe(topic, callback, payload_model)

    def set_token(self, token: str) -> None:
        """
        Set the authentication token for the MQTT client.
        :param token: The token to set.
        """
        self.__init_client(token)

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
        if self.__formatter.has_placeholders_left(topic):
            raise ValueError(f'Topic "{topic}" still have unformatted placeholders.')

        encoded_data = json.dumps(data.model_dump(mode='json'))

        self.__mqtt_client.publish(topic, encoded_data, qos=qos.value)

    def subscribe(self, topic: str, callback: Callback, payload_model: Type[T]) -> Unsubscribe:
        """
        Subscribe to a topic.
        :param topic: The topic to subscribe to.
        :param callback: The callback to call when a message is received.
        :param payload_model: The model to use for the payload. If None, no model is used.
        """
        if not issubclass(payload_model, BaseModel):
            raise TypeError(f'Invalid type {payload_model.__name__} for response model.')

        if self.__formatter.has_placeholders_left(topic):
            raise ValueError(f'Topic "{topic}" still have unformatted placeholders.')

        with self.__subscribers_lock:
            new_subscriber = topic not in self.__subscribers

            if new_subscriber:
                self.__subscribers[topic] = _Subscription(topic, payload_model)
                self.__mqtt_client.message_callback_add(topic, self.__subscribers[topic].internal_callback)

            cb_ix = self.__subscribers[topic].add(callback)

        # subscribe at the end to ensure the callback is registered before receiving messages
        if new_subscriber:
            self.__mqtt_client.subscribe(topic, qos=2)
        return lambda: self.__unsubscribe(topic, cb_ix)

    def __unsubscribe(self, topic: str, cb_ix: int) -> None:
        with self.__subscribers_lock:
            if topic not in self.__subscribers or cb_ix not in self.__subscribers[topic]:
                raise ValueError(f'No subscribers for topic {topic} at index {cb_ix}.')

            self.__subscribers[topic].rm(cb_ix)

            if self.__subscribers[topic].is_stale:
                self.__mqtt_client.unsubscribe(topic)
                del self.__subscribers[topic]
                logger.info(f'subscription to "{topic}" was stale and has been unsubscribed.')

    def format(self, topic: str, **kwargs) -> str:
        """
        Format a topic with the given keyword arguments.
        :param topic: The topic to format.
        :param kwargs: The keyword arguments to use for formatting.
        :return: The formatted topic.
        """
        return self.__formatter.format(topic, **kwargs)


def get_level_from_wildcard(subscribed_topic: str, received_topic: str, wildcard: str = '+') -> list[str]:
    """
    Get the wildcarded levels by comparing the subscribed topic and the received topic.
    :param subscribed_topic: The topic subscribed to.
    :param received_topic: The topic received.
    :param wildcard: The wildcard to use.
    :return: The level of the received topic.

    Example:
    get_level_from_wildcard('a/+/topic', 'a/fabulous/topic') -> ['fabulous']
    get_level_from_wildcard('a/+/and/+/topic', 'a/fabulous/and/mysterious/topic') -> ['fabulous', 'mysterious']
    """
    levels = []
    for s_level, r_level in zip(subscribed_topic.split('/'), received_topic.split('/'), strict=True):
        if s_level == wildcard:
            levels.append(r_level)
    return levels
