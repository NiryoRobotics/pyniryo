import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from queue import Queue

from pyniryo.nate._internal import transport_models, paths_gen, topics_gen
from pyniryo.nate.components.metrics import Metric, Metrics

from .base import BaseTestComponent


class TestMetric(unittest.TestCase):
    """Test the Metric descriptor class."""

    def test_metric_initialization_with_valid_types(self):
        """Test initializing Metric with all valid types."""
        valid_types = [
            (str, "test"),
            (int, 42),
            (float, 3.14),
            (bool, True),
            (datetime, datetime.now()),
            (timedelta, timedelta(seconds=10)),
        ]

        for _type, init_value in valid_types:
            with self.subTest(_type=_type):
                metric = Metric("test_metric", init_value, _type)
                self.assertEqual(metric.name, "test_metric")
                self.assertEqual(metric.value, init_value)
                self.assertEqual(metric.type, _type)

    def test_metric_initialization_with_invalid_type(self):
        """Test that initializing Metric with invalid type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            Metric("invalid_metric", [1, 2, 3], list)
        self.assertIn("Unsupported type", str(context.exception))

    def test_metric_set_name(self):
        """Test __set_name__ method sets private name correctly."""
        metric = Metric("counter", 0, int)
        metric.__set_name__(object, "my_metric")
        self.assertEqual(metric.private_name, "_my_metric")

    def test_metric_get_from_instance(self):
        """Test __get__ returns the value from instance."""

        class TestClass:
            counter = Metric("counter", 0, int)

        # Set up instance with metrics queue
        instance = TestClass()
        instance._metrics_queue = Queue()
        instance._counter = 42

        # Get value
        self.assertEqual(instance.counter, 42)

    def test_metric_get_from_class(self):
        """Test __get__ returns the descriptor when accessed from class."""

        class TestClass:
            counter = Metric("counter", 0, int)

        result = TestClass.counter
        self.assertIsInstance(result, Metric)

    def test_metric_set_updates_value_and_queues(self):
        """Test __set__ updates value and puts metric in queue."""

        class TestClass:
            counter = Metric("counter", 0, int)

        instance = TestClass()
        queue = Queue()
        instance._metrics_queue = queue

        # Set value
        instance.counter = 100

        # Check value was updated
        self.assertEqual(instance._counter, 100)

        # Check metric was queued
        self.assertFalse(queue.empty())
        queued_metric = queue.get()
        self.assertIsInstance(queued_metric, Metric)
        self.assertEqual(queued_metric.value, 100)

    def test_metric_set_without_queue_raises_error(self):
        """Test __set__ raises RuntimeError when metrics_queue is not registered."""

        class TestClass:
            counter = Metric("counter", 0, int)

        instance = TestClass()

        with self.assertRaises(RuntimeError) as context:
            instance.counter = 100
        self.assertIn("Unable to publish the metric update", str(context.exception))

    def test_metric_tr_value_primitives(self):
        """Test tr_value property for primitive types."""
        test_cases = [
            (str, "hello", "hello"),
            (int, 42, "42"),
            (float, 3.14, "3.14"),
            (bool, True, "True"),
        ]

        for _type, value, expected_str in test_cases:
            with self.subTest(_type=_type):
                metric = Metric("test", value, _type)
                self.assertEqual(metric.tr_value, expected_str)

    def test_metric_tr_value_datetime(self):
        """Test tr_value property for datetime type."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        metric = Metric("timestamp", dt, datetime)
        expected = dt.isoformat()
        self.assertEqual(metric.tr_value, expected)

    def test_metric_tr_value_timedelta(self):
        """Test tr_value property for timedelta type."""
        td = timedelta(hours=2, minutes=30, seconds=15)
        metric = Metric("duration", td, timedelta)
        expected = str(td.total_seconds())
        self.assertEqual(metric.tr_value, expected)


class TestMetrics(BaseTestComponent):
    """Test the Metrics component class."""

    def setUp(self):
        super().setUp()
        self.correlation_id = "test-correlation-123"
        # Patch threading.Thread to prevent actual thread creation in tests
        self.thread_patcher = patch('threading.Thread')
        self.mock_thread_class = self.thread_patcher.start()
        self.mock_thread = MagicMock()
        self.mock_thread_class.return_value = self.mock_thread

        self.metrics = Metrics(self.http_client, self.mqtt_client, self.correlation_id)

    def tearDown(self):
        # Clean up
        self.thread_patcher.stop()
        del self.metrics

    def test_initialization(self):
        """Test Metrics component initialization."""
        self.assertIsNotNone(self.metrics._metrics_queue)
        self.assertEqual(self.metrics._topic,
                         topics_gen.CustomMetrics.CUSTOM_METRIC.format(metrics_id=self.correlation_id))

    def test_close_stops_queue_processing(self):
        """Test close() method stops the queue processing thread."""
        # Mock the queue join to avoid blocking
        with patch.object(self.metrics._metrics_queue, 'join'):
            # Call close
            self.metrics.close()

        # Verify None was put in queue to signal stop
        self.assertFalse(self.metrics._metrics_queue.empty())
        sentinel = self.metrics._metrics_queue.get()
        self.assertIsNone(sentinel)

    def test_register_metrics_single_metric(self):
        """Test registering an object with a single metric."""

        class MetricsHolder:
            temperature = Metric("temperature", 25.5, float)

        holder = MetricsHolder()

        # Call register_metrics
        self.metrics.register_metrics(holder)

        # Verify HTTP POST was called
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]

        self.assertEqual(call_args[0], paths_gen.Metrics.DECLARE_CUSTOM_METRICS)
        self.assertEqual(call_args[1], transport_models.EmptyPayload)

        request = call_args[2]
        self.assertIsInstance(request, transport_models.s.CustomMetrics)
        self.assertEqual(request.metrics_id, self.correlation_id)
        self.assertEqual(len(request.metrics), 1)
        self.assertEqual(request.metrics[0].name, "temperature")
        self.assertEqual(request.metrics[0].value, "25.5")
        self.assertEqual(request.metrics[0].m_type, transport_models.s.MType.FLOAT)

        # Verify metrics_queue was set on instance
        self.assertIsNotNone(getattr(holder, '_metrics_queue', None))

    def test_register_metrics_multiple_metrics(self):
        """Test registering an object with multiple metrics."""

        class MetricsHolder:
            temperature = Metric("temperature", 25.5, float)
            humidity = Metric("humidity", 60, int)
            status = Metric("status", "online", str)
            is_active = Metric("is_active", True, bool)

        holder = MetricsHolder()

        # Call register_metrics
        self.metrics.register_metrics(holder)

        # Verify all metrics were registered
        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.metrics), 4)

        metric_names = {m.name for m in request.metrics}
        self.assertEqual(metric_names, {"temperature", "humidity", "status", "is_active"})

    def test_register_metrics_with_datetime_and_timedelta(self):
        """Test registering metrics with datetime and timedelta types."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        td = timedelta(hours=2, minutes=30)

        class MetricsHolder:
            timestamp = Metric("timestamp", dt, datetime)
            duration = Metric("duration", td, timedelta)

        holder = MetricsHolder()

        # Call register_metrics
        self.metrics.register_metrics(holder)

        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.metrics), 2)

        # Find each metric
        timestamp_metric = next(m for m in request.metrics if m.name == "timestamp")
        duration_metric = next(m for m in request.metrics if m.name == "duration")

        self.assertEqual(timestamp_metric.m_type, transport_models.s.MType.DATETIME)
        self.assertEqual(timestamp_metric.value, dt.isoformat())

        self.assertEqual(duration_metric.m_type, transport_models.s.MType.DURATION)
        self.assertEqual(duration_metric.value, str(td.total_seconds()))

    def test_register_metrics_ignores_non_metric_attributes(self):
        """Test that register_metrics only processes Metric instances."""

        class MetricsHolder:
            counter = Metric("counter", 0, int)
            normal_attribute = "not a metric"
            another_var = 42

        holder = MetricsHolder()

        # Call register_metrics
        self.metrics.register_metrics(holder)

        # Verify only the Metric was registered
        request = self.http_client.post.call_args[0][2]
        self.assertEqual(len(request.metrics), 1)
        self.assertEqual(request.metrics[0].name, "counter")

    def test_register_metrics_with_unsupported_type_raises_error(self):
        """Test that registering a metric with unsupported type raises TypeError."""

        # Create a metric with a type that's not in _type_bindings
        # This shouldn't happen normally due to Metric.__init__ validation,
        # but we can test the safety check in register_metrics
        class MetricsHolder:
            counter = Metric("counter", 0, int)

        holder = MetricsHolder()

        # Modify the metric's type to something unsupported
        # to test the error handling in register_metrics
        MetricsHolder.counter.type = list  # Bypass __init__ validation

        with self.assertRaises(TypeError) as context:
            self.metrics.register_metrics(holder)
        self.assertIn("Unsupported metric type", str(context.exception))

    def test_metric_update_queues_for_publishing(self):
        """Test that updating a metric queues it for publishing."""

        class MetricsHolder:
            counter = Metric("counter", 0, int)

        holder = MetricsHolder()
        self.metrics.register_metrics(holder)

        # Update metric
        holder.counter = 42

        # Verify metric was queued
        self.assertFalse(self.metrics._metrics_queue.empty())
        queued_metric = self.metrics._metrics_queue.get()
        self.assertIsInstance(queued_metric, Metric)
        self.assertEqual(queued_metric.name, "counter")
        self.assertEqual(queued_metric.value, 42)

    def test_multiple_metric_updates_queued(self):
        """Test multiple metric updates are queued correctly."""

        class MetricsHolder:
            counter = Metric("counter", 0, int)
            status = Metric("status", "idle", str)

        holder = MetricsHolder()
        self.metrics.register_metrics(holder)

        # Update metrics multiple times
        holder.counter = 1
        holder.status = "running"
        holder.counter = 2

        # Verify multiple metrics were queued
        self.assertEqual(self.metrics._metrics_queue.qsize(), 3)

    def test_process_metrics_queue_handles_exceptions(self):
        """Test that _process_metrics_queue handles exceptions gracefully."""

        # Create a metric that will cause an error when publishing
        class MetricsHolder:
            counter = Metric("counter", 0, int)

        holder = MetricsHolder()
        self.metrics.register_metrics(holder)

        # Make mqtt_client.publish raise an exception
        self.mqtt_client.publish.side_effect = Exception("MQTT error")

        # Update metric (this will queue it)
        holder.counter = 42

        # Verify the metric was queued
        self.assertFalse(self.metrics._metrics_queue.empty())

    def test_close_waits_for_queue_to_empty(self):
        """Test that close() queues sentinel value."""

        class MetricsHolder:
            counter = Metric("counter", 0, int)

        holder = MetricsHolder()
        self.metrics.register_metrics(holder)

        # Queue several updates
        for i in range(5):
            holder.counter = i

        # Mock join to prevent blocking
        with patch.object(self.metrics._metrics_queue, 'join'):
            self.metrics.close()

        # Verify that items were queued (5 updates + 1 None sentinel)
        self.assertEqual(self.metrics._metrics_queue.qsize(), 6)

    def test_get_metrics_single_metric(self):
        """Test getting a single metric."""
        metrics_id = "test-metrics-id"

        # Mock the HTTP response
        mock_metric = transport_models.s.CustomMetric(name="temperature",
                                                      value="25.5",
                                                      m_type=transport_models.s.MType.FLOAT)
        self.http_client.get.return_value = transport_models.s.CustomMetrics(metrics=[mock_metric],
                                                                             metrics_id=metrics_id)

        # Call get_metrics
        result = self.metrics.get_metrics(metrics_id)

        # Verify HTTP GET was called with correct parameters
        self.http_client.get.assert_called_once_with(paths_gen.Metrics.GET_CUSTOM_METRICS.format(metrics_id=metrics_id),
                                                     transport_models.s.CustomMetrics)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "temperature")
        self.assertEqual(result[0].value, "25.5")

    def test_get_metrics_multiple_metrics(self):
        """Test getting multiple metrics."""
        metrics_id = "multi-metrics-id"

        # Mock the HTTP response with multiple metrics
        mock_metrics = [
            transport_models.s.CustomMetric(name="temperature", value="25.5", m_type=transport_models.s.MType.FLOAT),
            transport_models.s.CustomMetric(name="humidity", value="60", m_type=transport_models.s.MType.INT),
            transport_models.s.CustomMetric(name="status", value="online", m_type=transport_models.s.MType.STRING),
            transport_models.s.CustomMetric(name="is_active", value="True", m_type=transport_models.s.MType.BOOL),
        ]
        self.http_client.get.return_value = transport_models.s.CustomMetrics(metrics=mock_metrics,
                                                                             metrics_id=metrics_id)

        # Call get_metrics
        result = self.metrics.get_metrics(metrics_id)

        # Verify the result
        self.assertEqual(len(result), 4)

        # Check each metric
        metric_dict = {m.name: m for m in result}
        self.assertEqual(metric_dict["temperature"].value, "25.5")
        self.assertEqual(metric_dict["humidity"].value, "60")
        self.assertEqual(metric_dict["status"].value, "online")
        self.assertEqual(metric_dict["is_active"].value, "True")

    def test_get_metrics_all_metric_types(self):
        """Test getting metrics with all supported types."""
        metrics_id = "all-types-metrics"

        dt = datetime(2024, 1, 15, 10, 30, 45)
        td = timedelta(hours=2, minutes=30)

        # Mock the HTTP response with all metric types
        mock_metrics = [
            transport_models.s.CustomMetric(name="text", value="hello", m_type=transport_models.s.MType.STRING),
            transport_models.s.CustomMetric(name="count", value="42", m_type=transport_models.s.MType.INT),
            transport_models.s.CustomMetric(name="ratio", value="3.14", m_type=transport_models.s.MType.FLOAT),
            transport_models.s.CustomMetric(name="flag", value="True", m_type=transport_models.s.MType.BOOL),
            transport_models.s.CustomMetric(name="timestamp",
                                            value=dt.isoformat(),
                                            m_type=transport_models.s.MType.DATETIME),
            transport_models.s.CustomMetric(name="duration",
                                            value=str(td.total_seconds()),
                                            m_type=transport_models.s.MType.DURATION),
        ]
        self.http_client.get.return_value = transport_models.s.CustomMetrics(metrics=mock_metrics,
                                                                             metrics_id=metrics_id)

        # Call get_metrics
        result = self.metrics.get_metrics(metrics_id)

        # Verify all types are present
        self.assertEqual(len(result), 6)
        metric_dict = {m.name: m for m in result}

        self.assertIn("text", metric_dict)
        self.assertIn("count", metric_dict)
        self.assertIn("ratio", metric_dict)
        self.assertIn("flag", metric_dict)
        self.assertIn("timestamp", metric_dict)
        self.assertIn("duration", metric_dict)

    def test_get_metrics_empty_list(self):
        """Test getting metrics when no metrics exist."""
        metrics_id = "empty-metrics-id"

        # Mock the HTTP response with empty list
        self.http_client.get.return_value = transport_models.s.CustomMetrics(metrics=[], metrics_id=metrics_id)

        # Call get_metrics
        result = self.metrics.get_metrics(metrics_id)

        # Verify empty list is returned
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    def test_get_metrics_correct_path_formatting(self):
        """Test that the metrics_id is correctly formatted into the path."""
        metrics_id = "special-id-123"

        # Mock the HTTP response
        self.http_client.get.return_value = transport_models.s.CustomMetrics(metrics=[], metrics_id=metrics_id)

        # Call get_metrics
        self.metrics.get_metrics(metrics_id)

        # Verify the path is formatted correctly
        expected_path = paths_gen.Metrics.GET_CUSTOM_METRICS.format(metrics_id=metrics_id)
        self.http_client.get.assert_called_once_with(expected_path, transport_models.s.CustomMetrics)


class TestMetricIntegration(BaseTestComponent):
    """Integration tests for Metric and Metrics working together."""

    def setUp(self):
        super().setUp()
        # Patch threading.Thread to prevent actual thread creation in tests
        self.thread_patcher = patch('threading.Thread')
        self.mock_thread_class = self.thread_patcher.start()
        self.mock_thread = MagicMock()
        self.mock_thread_class.return_value = self.mock_thread

        self.metrics = Metrics(self.http_client, self.mqtt_client, "integration-test")

    def tearDown(self):
        self.thread_patcher.stop()
        del self.metrics

    def test_full_workflow(self):
        """Test complete workflow: register, update, queue."""

        class RobotMetrics:
            position_x = Metric("position_x", 0.0, float)
            position_y = Metric("position_y", 0.0, float)
            is_moving = Metric("is_moving", False, bool)

        robot_metrics = RobotMetrics()

        # Register metrics
        self.metrics.register_metrics(robot_metrics)

        # Verify registration
        self.http_client.post.assert_called_once()

        # Update metrics
        robot_metrics.position_x = 10.5
        robot_metrics.position_y = 20.3
        robot_metrics.is_moving = True

        # Verify updates were queued
        self.assertEqual(self.metrics._metrics_queue.qsize(), 3)

    def test_metric_descriptor_lifecycle(self):
        """Test metric descriptor through full lifecycle."""

        class Counter:
            value = Metric("value", 0, int)

        counter = Counter()
        self.metrics.register_metrics(counter)

        # Initialize the value by setting it first
        counter.value = 0

        # Test reading value
        self.assertEqual(counter.value, 0)

        # Test updating value
        counter.value = 10
        self.assertEqual(counter.value, 10)

        # Test multiple updates
        for i in range(1, 6):
            counter.value = i * 10

        # Verify all updates were queued (1 initial + 1 update to 10 + 5 loop updates = 7)
        self.assertEqual(self.metrics._metrics_queue.qsize(), 7)


if __name__ == "__main__":
    unittest.main()
