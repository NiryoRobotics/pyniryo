import unittest
from unittest import mock

from unittest.mock import create_autospec, patch
from pyniryo.nate._internal.mqtt import MqttClient, get_level_from_wildcard

from paho.mqtt.client import Client as PahoClient


def get_paho_mock():
    return create_autospec(PahoClient, spec_set=True, instance=True)


class TestMqttClient(unittest.TestCase):

    @patch("pyniryo.nate._internal.mqtt.Client")
    def test_connect(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883)
        mock_client.return_value.connect.assert_called_once_with("localhost", 1883)
        mock_client.return_value.loop_start.assert_called_once()

    @patch("pyniryo.nate._internal.mqtt.Client")
    def test_disconnect(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883)
        del client
        mock_client.return_value.loop_stop.assert_called_once()
        mock_client.return_value.disconnect.assert_called_once()

    @patch("pyniryo.nate._internal.mqtt.Client")
    def test_subscribe(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883)
        callback = lambda _topic, _t_model: None
        client.subscribe("test/topic", callback)
        mock_client.return_value.message_callback_add.assert_called_once_with("test/topic", mock.ANY)
        mock_client.return_value.subscribe.assert_called_once_with("test/topic")


class TestGetLevelFromWildcard(unittest.TestCase):

    def test_get_level_from_wildcard(self):
        result = get_level_from_wildcard('a/+/topic', 'a/fabulous/topic')
        self.assertEqual(result, ['fabulous'])

    def test_get_level_from_wildcard_with_multiple_levels(self):
        result = get_level_from_wildcard('a/+/topic/+', 'a/fabulous/topic/indeed')
        self.assertEqual(result, ['fabulous', 'indeed'])

    def test_get_level_get_level_without_wildcard(self):
        result = get_level_from_wildcard('a/b/topic', 'a/b/topic')
        self.assertEqual(result, [])
