import logging
import threading
from queue import Queue
from typing import TypeVar, Type
from datetime import datetime, timedelta

from .._internal import topics_gen, transport_models, paths_gen
from pyniryo.nate.components import BaseAPIComponent
from .._internal.const import NULL_TOPIC
from .._internal.http import HttpClient
from .._internal.mqtt import MqttClient
from .._internal.transport_models.models_gen import DeclareCustomMetric

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=str | int | float | bool | datetime | timedelta)


def _type_to_mtype(t: type) -> transport_models.s.MType:
    if t is str:
        return transport_models.s.MType.STRING
    elif t is int:
        return transport_models.s.MType.INT
    elif t is float:
        return transport_models.s.MType.FLOAT
    elif t is bool:
        return transport_models.s.MType.BOOL
    elif t is datetime:
        return transport_models.s.MType.DATETIME
    elif t is timedelta:
        return transport_models.s.MType.DURATION
    else:
        raise TypeError(f'Unsupported type {t}')


class Metric:

    def __init__(self, name: str, init_value: T, _type: Type[T]) -> None:
        self._name = name
        self._value = init_value
        self._type = _type

        if _type not in [str, int, float, bool, datetime, timedelta]:
            raise TypeError(f'Unsupported type {self._type}')

        self.private_name = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        queue: Queue = getattr(instance, '_metrics_queue', None)
        if queue is None:
            raise RuntimeError(
                "Unable to publish the metric update. Make sure to register the metrics before using it.")
        queue.put(transport_models.a.CustomMetric(name=self._name, value=str(value)))

        setattr(instance, self.private_name, value)


class Metrics(BaseAPIComponent):

    _metrics_queue: Queue[transport_models.a.CustomMetric | None]

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient) -> None:
        super().__init__(http_client, mqtt_client)
        self._topic = NULL_TOPIC
        self._metrics_queue = Queue()
        threading.Thread(target=self._process_metrics_queue, daemon=True).start()

    def close(self) -> None:
        self._metrics_queue.put(None)
        self._metrics_queue.join()

    def _process_metrics_queue(self) -> None:
        while True:
            metric = self._metrics_queue.get()
            try:
                if metric is None:
                    break
                self._mqtt_client.publish(self._topic, metric)
            except Exception as e:
                logger.error(f'Failed to publish metric update: {e}')
            finally:
                self._metrics_queue.task_done()

    def register_metrics(self, inst: object) -> None:
        if self._topic != NULL_TOPIC:
            raise RuntimeError('Metrics have already been registered.')

        metrics = []
        for m in vars(type(inst)).values():
            if not isinstance(m, Metric):
                continue
            metrics.append(
                transport_models.s.DeclareCustomMetric(name=m._name,
                                                       value=str(m._value),
                                                       m_type=_type_to_mtype(m._type)))

        logger.info(f'metrics: {metrics}')
        resp = self._http_client.post(paths_gen.Metrics.DECLARE_CUSTOM_METRICS,
                                      transport_models.s.FeedbackResponse,
                                      transport_models.s.DeclareCustomMetrics(root=metrics))

        self._topic = topics_gen.CustomMetrics.CUSTOM_METRIC.format(correlation_id=resp.feedback_id)
        setattr(inst, '_metrics_queue', self._metrics_queue)
