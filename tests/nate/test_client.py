import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from pyniryo.nate.client import Nate
from pyniryo.nate._internal import transport_models, paths_gen, const
from pyniryo.nate.components import Auth, Users, Robot, Device, Programs
from pyniryo.nate.components.motion_planner import MotionPlanner


class TestNateClient(unittest.TestCase):

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_with_login(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test initializing client with username and password."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http

        # Mock login response
        token_response = transport_models.s.Token(id=uuid4(),
                                                  token='generated-token',
                                                  expires_at=datetime.now() + timedelta(days=1),
                                                  created_at=datetime.now())
        mock_http.post.return_value = token_response
        mock_http.get.return_value = transport_models.s.DeviceID(device_id='test-device-123')

        mock_mqtt = MagicMock()
        mock_mqtt_client_class.return_value = mock_mqtt

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client with login
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify HTTP client was created correctly (without token)
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
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

        # Verify token was set
        mock_http.set_token.assert_called_once_with('generated-token')
        mock_mqtt.set_token.assert_called_once_with('generated-token')

        # Verify device ID was fetched
        mock_http.get.assert_called_once_with(paths_gen.Device.GET_DEVICE_ID, transport_models.s.DeviceID)

        # Verify MQTT client was created
        mock_mqtt_client_class.assert_called_once()

        # Verify TokenRenewer was initialized and started
        mock_token_renewer_class.assert_called_once()
        mock_token_renewer.start.assert_called_once()

        # Verify all components were initialized
        self.assertIsInstance(client.auth, Auth)
        self.assertIsInstance(client.users, Users)
        self.assertIsInstance(client.robot, Robot)
        self.assertIsInstance(client.device, Device)
        self.assertIsInstance(client.programs, Programs)
        self.assertIsInstance(client.motion_planner, MotionPlanner)

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_USERNAME': 'env-user', 'NATE_PASSWORD': 'env-pass'})
    def test_init_from_environment_variables_login(self,
                                                   mock_http_client_class,
                                                   mock_mqtt_client_class,
                                                   mock_token_renewer_class):
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client without parameters
        client = Nate()

        # Verify login was called with env vars
        login_request = mock_http.post.call_args[0][2]
        self.assertEqual(login_request.login, 'env-user')
        self.assertEqual(login_request.password, 'env-pass')

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_defaults_to_localhost(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test that hostname defaults to localhost if not provided."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client with login but no hostname
        client = Nate(login=('user@example.com', 'password123'))

        # Verify localhost was used
        mock_http_client_class.assert_called_once_with('localhost',
                                                       const.DEFAULT_HTTP_PORT,
                                                       insecure=False,
                                                       use_http=False)

    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_init_missing_credentials_raises_error(self, mock_http_client_class, mock_mqtt_client_class):
        """Test that missing credentials raises ValueError."""
        # Setup mocks
        mock_http = MagicMock()
        mock_http_client_class.return_value = mock_http

        # Should raise error when incomplete login
        with self.assertRaises(ValueError) as context:
            client = Nate(hostname='192.168.1.100', login=('user@example.com', None))

        self.assertIn('username and password', str(context.exception))

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_HTTP_PORT': '9000', 'NATE_MQTT_PORT': '2000'})
    def test_init_custom_ports_from_env(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test using custom ports from environment variables."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify custom ports were used
        mock_http_client_class.assert_called_once_with('192.168.1.100', 9000, insecure=False, use_http=False)

        # Check MQTT client was called with custom port
        mqtt_call_args = mock_mqtt_client_class.call_args
        self.assertEqual(mqtt_call_args[0][1], 2000)

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_INSECURE': '1'})
    def test_init_insecure_mode(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test initializing in insecure mode."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify insecure flag was set
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       insecure=True,
                                                       use_http=False)

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_USE_HTTP': '1'})
    def test_init_use_http(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test initializing with HTTP instead of HTTPS."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify use_http flag was set
        mock_http_client_class.assert_called_once_with('192.168.1.100',
                                                       const.DEFAULT_HTTP_PORT,
                                                       insecure=False,
                                                       use_http=True)

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    @patch.dict('os.environ', {'NATE_EXECUTION_TOKEN': 'exec-token-123'})
    def test_init_with_execution_token(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test initializing with execution token header."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

        # Verify execution token header was set
        mock_http.set_header.assert_called_once_with('Execution-Token', 'exec-token-123')

    @patch('pyniryo.nate.client.TokenRenewer')
    @patch('pyniryo.nate.client.MqttClient')
    @patch('pyniryo.nate.client.HttpClient')
    def test_component_initialization(self, mock_http_client_class, mock_mqtt_client_class, mock_token_renewer_class):
        """Test that all components are properly initialized with clients."""
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

        mock_token_renewer = MagicMock()
        mock_token_renewer_class.return_value = mock_token_renewer

        # Create client
        client = Nate(hostname='192.168.1.100', login=('user@example.com', 'password123'))

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
