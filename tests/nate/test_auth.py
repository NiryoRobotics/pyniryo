from datetime import datetime, timedelta

from unittest.mock import MagicMock, call, patch
from uuid import uuid4

from pyniryo.nate._internal import paths_gen, transport_models
from pyniryo.nate import models
from pyniryo.nate.components.auth import Auth

from .base import BaseTestComponent


class TestAuth(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.auth = Auth(http_client=self.http_client, mqtt_client=self.mqtt_client)

    def tearDown(self):
        del self.auth

    def test_login(self):
        expire_date = datetime.now() + timedelta(days=1)
        self.http_client.post.return_value = transport_models.Token(
            expires_at=expire_date,
            id=uuid4(),
            created_at=datetime.now(),
            token='generated_token',
        )

        token = self.auth.login('mail@mail.com', 'password', expire_date)
        self.http_client.post.assert_called_once()
        endpoint, login_model, response_model = self.http_client.post.call_args[0]
        self.assertEqual(endpoint, paths_gen.Login.LOGIN)
        self.assertEqual(login_model.email, 'mail@mail.com')
        self.assertEqual(login_model.password, 'password')
        self.assertEqual(login_model.expires_at, expire_date)
        self.assertEqual(response_model, transport_models.Token)
        self.assertEqual(token.token, 'generated_token')

    @patch('pyniryo.nate._internal.mqtt.get_level_from_wildcard')
    def test_on_user_logged_in_specific_user(self, mock_get_level):
        """Test subscribing to login events for a specific user."""
        user_id = str(uuid4())
        mock_get_level.return_value = [user_id]
        user_callback = MagicMock(spec=lambda u_id, u_logged_in: None)

        self.auth.on_user_logged_in(user_callback, user_id)

        self.mqtt_client.subscribe.assert_called_once()
        topic = f'users/{user_id}/logged-in'
        self.assertEqual(self.mqtt_client.subscribe.call_args[0][0], topic)

        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        internal_callback(topic, transport_models.UserLoggedIn())
        user_callback.assert_called_once_with(user_id, models.UserLoggedIn())

    @patch('pyniryo.nate._internal.mqtt.get_level_from_wildcard')
    def test_on_user_logged_in_any_user(self, mock_get_level):
        """Test subscribing to login events for any user."""

        user_callback = MagicMock(spec=lambda u_id, u_logged_in: None)
        self.auth.on_user_logged_in(user_callback)

        self.mqtt_client.subscribe.assert_called_once()
        self.assertEqual(self.mqtt_client.subscribe.call_args[0][0], 'users/+/logged-in')

        expected_calls = []
        for _ in range(3):
            user_id = str(uuid4())
            mock_get_level.return_value = [user_id]
            self.auth.on_user_logged_in(user_callback, user_id)

            internal_callback = self.mqtt_client.subscribe.call_args[0][1]
            internal_callback(f'users/{user_id}/logged-in', transport_models.UserLoggedIn())
            expected_calls.append(call(user_id, models.UserLoggedIn()))

        user_callback.assert_has_calls(expected_calls)

    @patch('pyniryo.nate._internal.mqtt.get_level_from_wildcard')
    def test_on_user_logged_out_specific_user(self, mock_get_level):
        """Test subscribing to logout events for a specific user."""
        user_id = str(uuid4())
        mock_get_level.return_value = [user_id]
        user_callback = MagicMock(spec=lambda u_id, u_logged_out: None)

        self.auth.on_user_logged_out(user_callback, user_id)

        self.mqtt_client.subscribe.assert_called_once()
        topic = f'users/{user_id}/logged-out'
        self.assertEqual(self.mqtt_client.subscribe.call_args[0][0], topic)

        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        internal_callback(topic, transport_models.UserLoggedOut())
        user_callback.assert_called_once_with(user_id, models.UserLoggedOut())

    @patch('pyniryo.nate._internal.mqtt.get_level_from_wildcard')
    def test_on_user_logged_out_any_user(self, mock_get_level):
        """Test subscribing to logout events for any user."""

        user_callback = MagicMock(spec=lambda u_id, u_logged_out: None)
        self.auth.on_user_logged_out(user_callback)

        self.mqtt_client.subscribe.assert_called_once()
        self.assertEqual(self.mqtt_client.subscribe.call_args[0][0], 'users/+/logged-out')

        expected_calls = []
        for _ in range(3):
            user_id = str(uuid4())
            mock_get_level.return_value = [user_id]
            self.auth.on_user_logged_out(user_callback, user_id)

            internal_callback = self.mqtt_client.subscribe.call_args[0][1]
            internal_callback(f'users/{user_id}/logged-out', transport_models.UserLoggedOut())
            expected_calls.append(call(user_id, models.UserLoggedOut()))

        user_callback.assert_has_calls(expected_calls)
