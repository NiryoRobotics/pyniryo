import unittest

from unittest.mock import create_autospec, patch
from pyniryo.nate._internal.mqtt import MqttClient, get_level_from_wildcard

from paho.mqtt.client import Client as PahoClient

CLIENT_PATH_PATH = 'pyniryo.nate._internal.mqtt.Client'


def get_paho_mock():
    return create_autospec(PahoClient, spec_set=True, instance=True)


class TestMqttClient(unittest.TestCase):

    @patch(CLIENT_PATH_PATH)
    def test_connect(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883, '<token>')
        mock_client.return_value.connect.assert_called_once_with("localhost", 1883)
        mock_client.return_value.loop_start.assert_called_once()

    @patch(CLIENT_PATH_PATH)
    def test_disconnect(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883, '<token>')
        client.disconnect()
        mock_client.return_value.loop_stop.assert_called_once()
        mock_client.return_value.disconnect.assert_called_once()

    def __callback(self, _topic, _payload):
        pass

    @patch(CLIENT_PATH_PATH)
    def test_subscribe(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883, '<token>')
        client.subscribe("test/topic", self.__callback)
        mock_client.return_value.subscribe.assert_called_once_with("test/topic")

    @patch(CLIENT_PATH_PATH)
    def test_multi_subscribe(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883, '<token>')
        client.subscribe("test/topic", self.__callback)
        mock_client.return_value.subscribe.assert_called_once_with("test/topic")

        mock_client.return_value.subscribe.reset_mock()
        client.subscribe("test/topic", self.__callback)
        mock_client.return_value.subscribe.assert_not_called()

    @patch(CLIENT_PATH_PATH)
    def test_unsubscribe(self, mock_client):
        mock_client.return_value = get_paho_mock()
        client = MqttClient("localhost", 1883, '<token>')
        client.subscribe("test/topic", self.__callback)

        client.unsubscribe(self.__callback)
        mock_client.return_value.unsubscribe.assert_called_once_with("test/topic")


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
