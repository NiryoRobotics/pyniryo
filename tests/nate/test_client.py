import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from pyniryo.nate.client import Nate
from pyniryo.nate._internal import transport_models, paths_gen, const
from pyniryo.nate.components import Auth, Users, Robot, Device, Programs
from pyniryo.nate.components.motion_planner import MotionPlanner


class TestNateClient(unittest.TestCase):

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_with_token(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing client with authentication token."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client with token
        client = Nate(hostname='192.168.1.100', token='test-token-123')

        # Verify HTTP client was created correctly
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       'test-token-123',
                                                       insecure=False,
                                                       use_http=False)

        # Verify token was set
        mock_http.set_token.assert_called_once_with('test-token-123')

        # Verify device ID was fetched
        mock_http.get.assert_called_once_with(paths_gen.Device.GET_DEVICE_ID, transport_models.s.DeviceID)

        # Verify MQTT client was created
        mock_mqtt_client_class.assert_called_once()

        # Verify all components were initialized
        self.assertIsInstance(client.auth, Auth)
        self.assertIsInstance(client.users, Users)
        self.assertIsInstance(client.robot, Robot)
        self.assertIsInstance(client.device, Device)
        self.assertIsInstance(client.programs, Programs)
        self.assertIsInstance(client.motion_planner, MotionPlanner)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_with_username_password(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing client with username and password."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http

        # Mock login response
        token_response = transport_models.s.Token(id=uuid4(),
                                                  token='generated-token',
                                                  expires_at=datetime.now() + timedelta(days=1),
                                                  created_at=datetime.now())
        # First call to post (login), then get (device ID)
        mock_http.post.return_value = token_response
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client with username/password
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify HTTP client was created without token initially
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       None,
                                                       insecure=False,
                                                       use_http=False)

        # Verify login was called
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Authentication.LOGIN)
        self.assertEqual(call_args[1], transport_models.s.Token)
        login_request = call_args[2]
        self.assertEqual(login_request.login, 'user@example.com')
        self.assertEqual(login_request.password, 'password123')

        # Verify token was set after login
        mock_http.set_token.assert_called_once_with('generated-token')

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_HOSTNAME': 'env-host', 'NATE_TOKEN': 'env-token'})
    def test_init_from_environment_variables(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing client from environment variables."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client without parameters (should use env vars)
        client = Nate()

        # Verify environment variables were used
        mock_http_client_class.assert_called_once_with('env-host',
                                                       const.DEFAULT_HTTP_PORT,
                                                       'env-token',
                                                       insecure=False,
                                                       use_http=False)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_USERNAME': 'env-user', 'NATE_PASSWORD': 'env-pass'})
    def test_init_from_environment_variables_login(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing client with username/password from environment variables."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http

        token_response = transport_models.s.Token(id=uuid4(),
                                                  token='generated-token',
                                                  expires_at=datetime.now() + timedelta(days=1),
                                                  created_at=datetime.now())
        mock_http.post.return_value = token_response
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client without parameters
        client = Nate()

        # Verify login was called with env vars
        login_request = mock_http.post.call_args[0][2]
        self.assertEqual(login_request.login, 'env-user')
        self.assertEqual(login_request.password, 'env-pass')

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_defaults_to_localhost(self, mock_http_client_class, mock_mqtt_client_class):
        """Test that hostname defaults to localhost if not provided."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client with token but no hostname
        client = Nate(token='test-token')

        # Verify localhost was used
        mock_http_client_class.assert_called_once_with('localhost',
                                                       const.DEFAULT_HTTP_PORT,
                                                       'test-token',
                                                       insecure=False,
                                                       use_http=False)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_missing_credentials_raises_error(self, mock_http_client_class, mock_mqtt_client_class):
        """Test that missing credentials raises ValueError."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http

        # Should raise error when no token and incomplete login
        with self.assertRaises(ValueError) as context:
            client = Nate(hostname='192.168.1.100', login=('user@example.com', None))

        self.assertIn('username and password', str(context.exception))

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_HTTP_PORT': '9000', 'NATE_MQTT_PORT': '2000'})
    def test_init_custom_ports_from_env(self, mock_http_client_class, mock_mqtt_client_class):
        """Test using custom ports from environment variables."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client
        client = Nate(hostname='192.168.1.100', token='test-token')

        # Verify custom ports were used
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       '9000',
                                                       'test-token',
                                                       insecure=False,
                                                       use_http=False)

        # Check MQTT client was called with custom port
        mqtt_call_args = mock_mqtt_client_class.call_args
        self.assertEqual(mqtt_call_args[0][1], '2000')

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_INSECURE': '1'})
    def test_init_insecure_mode(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing in insecure mode."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client
        client = Nate(hostname='192.168.1.100', token='test-token')

        # Verify insecure flag was set
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       'test-token',
                                                       insecure=True,
                                                       use_http=False)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_USE_HTTP': '1'})
    def test_init_use_http(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing with HTTP instead of HTTPS."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client
        client = Nate(hostname='192.168.1.100', token='test-token')

        # Verify use_http flag was set
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       'test-token',
                                                       insecure=False,
                                                       use_http=True)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_EXECUTION_TOKEN': 'exec-token-123'})
    def test_init_with_execution_token(self, mock_http_client_class, mock_mqtt_client_class):
        """Test initializing with execution token header."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client
        client = Nate(hostname='192.168.1.100', token='test-token')

        # Verify execution token header was set
        mock_http.set_header.assert_called_once_with('Execution-Token', 'exec-token-123')

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_component_initialization(self, mock_http_client_class, mock_mqtt_client_class):
        """Test that all components are properly initialized with clients."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        # Create client
        client = Nate(hostname='192.168.1.100', token='test-token')

        # Verify all components exist and are of correct type
        self.assertIsInstance(client.auth, Auth)
        self.assertIsInstance(client.users, Users)
        self.assertIsInstance(client.robot, Robot)
        self.assertIsInstance(client.device, Device)
        self.assertIsInstance(client.programs, Programs)
        self.assertIsInstance(client.motion_planner, MotionPlanner)

        # Verify components have access to clients
        # (This is implicit since they're BaseAPIComponent subclasses)
        self.assertIsNotNone(client.auth)
        self.assertIsNotNone(client.robot)


if __name__ == "__main__":
    unittest.main()
