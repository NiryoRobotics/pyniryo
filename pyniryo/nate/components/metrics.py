import logging
import threading
from queue import Queue
from typing import TypeVar, Type
from datetime import datetime, timedelta

from .. import models
from .._internal import topics_gen, transport_models, paths_gen
from pyniryo.nate.components import BaseAPIComponent
from .._internal.http import HttpClient
from .._internal.mqtt import MqttClient

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=str | int | float | bool | datetime | timedelta)


class Metric:
    """
    Descriptor class for defining custom metrics that can be monitored.
    
    This class is used as a descriptor in user-defined classes to create
    metrics that automatically publish updates when their values change.
    
    :param name: The name of the metric.
    :param init_value: The initial value of the metric.
    :param _type: The Python type of the metric value.
    
    Example:
        >>> class MyMetrics:
        ...     temperature = Metric("temperature", 20.0, float)
        ...     count = Metric("count", 0, int)
        ...     status = Metric("status", "idle", str)
        >>> 
        >>> my_metrics = MyMetrics()
        >>> metrics_component.register_metrics(my_metrics)
        >>> my_metrics.temperature = 25.5  # Automatically publishes update
    """

    def __init__(self, name: str, init_value: T, _type: Type[T]) -> None:
        if _type not in [str, int, float, bool, datetime, timedelta]:
            raise TypeError(f'Unsupported type {_type.__name__} for metric "{name}"')

        if not isinstance(init_value, _type):
            raise TypeError(f'Initial value {init_value} does not match type {_type.__name__} for metric "{name}"')

        self.name = name
        self.value = init_value
        self.type = _type
        self.private_name = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name, self.value)

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
    """
    Metrics component for declaring and publishing custom metrics.
    
    This component allows you to define custom metrics that can be monitored
    and tracked during robot operations. Metrics are automatically published
    when their values change.
    
    Example:
        >>> from pyniryo.nate import Nate
        >>> from pyniryo.nate.components.metrics import Metric
        >>> 
        >>> class RobotMetrics:
        ...     cycle_count = Metric("cycle_count", 0, int)
        ...     success_rate = Metric("success_rate", 0.0, float)
        ...     status = Metric("status", "initializing", str)
        >>> 
        >>> nate = Nate()
        >>> my_metrics = RobotMetrics()
        >>> nate.metrics.register_metrics(my_metrics)
        >>> 
        >>> # Update metrics (automatically publishes)
        >>> my_metrics.cycle_count = 1
        >>> my_metrics.success_rate = 95.5
        >>> my_metrics.status = "running"
    """

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
                self._mqtt_client.publish(
                    self._topic,
                    transport_models.a.CustomMetric(name=metric.name,
                                                    value=metric.tr_value,
                                                    m_type=models.get_mtype(metric.type, a=True)))
            except Exception as e:
                logger.error(f'Failed to publish metric update: {e}')
            finally:
                self._metrics_queue.task_done()

    def register_metrics(self, inst: object) -> None:
        """
        Register custom metrics from an object instance.
        
        This method inspects the provided object for Metric descriptors and registers
        them with the system. After registration, any changes to metric values will
        be automatically published.
        
        :param inst: An object instance containing Metric descriptors.
        
        Example:
            >>> class MyMetrics:
            ...     temperature = Metric("temp", 20.0, float)
            ...     count = Metric("count", 0, int)
            >>> 
            >>> my_metrics = MyMetrics()
            >>> metrics.register_metrics(my_metrics)
            >>> 
            >>> # Now updates are published automatically
            >>> my_metrics.count = 10
        """
        metrics = []
        for m in vars(type(inst)).values():
            if not isinstance(m, Metric):
                continue
            metrics.append(
                transport_models.s.CustomMetric(name=m.name, value=m.tr_value, m_type=models.get_mtype(m.type)))

        self._http_client.post(paths_gen.Metrics.DECLARE_CUSTOM_METRICS,
                               transport_models.EmptyPayload,
                               transport_models.s.CustomMetrics(metrics=metrics, metrics_id=self._correlation_id))

        setattr(inst, '_metrics_queue', self._metrics_queue)

    def get_metrics(self, metrics_id: str) -> list[models.Metric]:
        """
        Retrieve custom metrics by their metrics ID.
        
        :param metrics_id: The ID of the metrics to retrieve.
        :return: A list of Metric objects.
        
        Example:
            >>> metrics_list = metrics.get_metrics("my_metrics_id")
            >>> for metric in metrics_list:
            ...     print(f"{metric.name}: {metric.value}")
        """
        resp = self._http_client.get(paths_gen.Metrics.GET_CUSTOM_METRICS.format(metrics_id=metrics_id),
                                     transport_models.s.CustomMetrics)
        return [models.Metric.from_transport_model(m) for m in resp.metrics]
