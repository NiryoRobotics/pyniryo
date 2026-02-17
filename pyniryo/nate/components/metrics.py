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

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=str | int | float | bool | datetime | timedelta)

_type_bindings = {
    str: transport_models.s.MType.STRING,
    int: transport_models.s.MType.INT,
    float: transport_models.s.MType.FLOAT,
    bool: transport_models.s.MType.BOOL,
    datetime: transport_models.s.MType.DATETIME,
    timedelta: transport_models.s.MType.DURATION
}


class Metric:

    def __init__(self, name: str, init_value: T, _type: Type[T]) -> None:
        self.name = name
        self.value = init_value
        self.type = _type

        if _type not in [str, int, float, bool, datetime, timedelta]:
            raise TypeError(f'Unsupported type {self.type}')

        self.private_name = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        self.value = value
        queue: Queue = getattr(instance, '_metrics_queue', None)
        if queue is None:
            raise RuntimeError(
                "Unable to publish the metric update. Make sure to register the metrics before using it.")
        queue.put(self)

        setattr(instance, self.private_name, self.value)

    @property
    def tr_value(self) -> str:
        if self.type is datetime:
            return self.value.isoformat()
        elif self.type is timedelta:
            return str(self.value.total_seconds())
        else:
            return str(self.value)


class Metrics(BaseAPIComponent):

    _metrics_queue: Queue[Metric | None]

    def __init__(self, http_client: HttpClient, mqtt_client: MqttClient, correlation_id: str) -> None:
        super().__init__(http_client, mqtt_client, correlation_id)
        self._topic = topics_gen.CustomMetrics.CUSTOM_METRIC.format(metrics_id=self._correlation_id)
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
                self._mqtt_client.publish(self._topic,
                                          transport_models.a.CustomMetric(name=metric.name, value=metric.tr_value))
            except Exception as e:
                logger.error(f'Failed to publish metric update: {e}')
            finally:
                self._metrics_queue.task_done()

    def register_metrics(self, inst: object) -> None:
        metrics = []
        for m in vars(type(inst)).values():
            if not isinstance(m, Metric):
                continue
            m_type = _type_bindings.get(m.type)
            if m_type is None:
                raise TypeError(f'Unsupported type {m.type} for metric {m.name}')

            metrics.append(transport_models.s.Metric(name=m.name, value=m.tr_value, m_type=m_type))

        self._http_client.post(
            paths_gen.Metrics.DECLARE_CUSTOM_METRICS,
            transport_models.EmptyPayload,
            transport_models.s.DeclareCustomMetrics(metrics=metrics, metrics_id=self._correlation_id))

        setattr(inst, '_metrics_queue', self._metrics_queue)
