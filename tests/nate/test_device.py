import unittest

from pyniryo.nate._internal import transport_models, paths_gen
from pyniryo.nate.components.device import Device
from pyniryo.nate.exceptions import ServerError

from .base import BaseTestComponent


class TestDevice(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.device = Device(http_client=self.http_client, mqtt_client=self.mqtt_client)

    def tearDown(self):
        del self.device

    def test_id(self):
        """Test getting the device ID."""
        expected_id = "test-device-123"
        self.http_client.get.return_value = transport_models.s.DeviceID(device_id=expected_id)

        device_id = self.device.id()

        self.http_client.get.assert_called_once_with(paths_gen.Device.GET_DEVICE_ID, transport_models.s.DeviceID)
        self.assertEqual(device_id, expected_id)

    def test_is_healthy_success(self):
        """Test health check when robot is healthy."""
        self.http_client.get.return_value = transport_models.HealthCheckResponse(status='healthy')

        is_healthy = self.device.is_healthy()

        self.http_client.get.assert_called_once_with(paths_gen.Device.HEALTH_CHECK,
                                                     transport_models.HealthCheckResponse)
        self.assertTrue(is_healthy)

    def test_is_healthy_failure(self):
        """Test health check when robot is not healthy."""
        self.http_client.get.side_effect = ServerError(500, "Health check failed")

        is_healthy = self.device.is_healthy()

        self.http_client.get.assert_called_once_with(paths_gen.Device.HEALTH_CHECK,
                                                     transport_models.HealthCheckResponse)
        self.assertFalse(is_healthy)

    def test_is_ready_true(self):
        """Test readiness check when robot is ready."""
        self.http_client.get.return_value = transport_models.ReadinessCheckResponse(ready=True)

        is_ready = self.device.is_ready()

        self.http_client.get.assert_called_once_with(paths_gen.Device.READINESS_CHECK,
                                                     transport_models.ReadinessCheckResponse)
        self.assertTrue(is_ready)

    def test_is_ready_false(self):
        """Test readiness check when robot is not ready."""
        self.http_client.get.return_value = transport_models.ReadinessCheckResponse(ready=False)

        is_ready = self.device.is_ready()

        self.http_client.get.assert_called_once_with(paths_gen.Device.READINESS_CHECK,
                                                     transport_models.ReadinessCheckResponse)
        self.assertFalse(is_ready)

    def test_reboot(self):
        """Test rebooting the robot."""
        self.http_client.post.return_value = transport_models.EmptyPayload()

        self.device.reboot()

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Device.REBOOT)
        self.assertEqual(call_args[1], transport_models.EmptyPayload)
        self.assertIsInstance(call_args[2], transport_models.EmptyPayload)

    def test_shutdown(self):
        """Test shutting down the robot."""
        self.http_client.post.return_value = transport_models.EmptyPayload()

        self.device.shutdown()

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Device.SHUTDOWN)
        self.assertEqual(call_args[1], transport_models.EmptyPayload)
        self.assertIsInstance(call_args[2], transport_models.EmptyPayload)


if __name__ == "__main__":
    unittest.main()
