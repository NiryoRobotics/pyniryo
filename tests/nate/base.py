import unittest
from unittest.mock import create_autospec

from pyniryo.nate._internal.http import HttpClient
from pyniryo.nate._internal.mqtt import MqttClient


class BaseTestComponent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.http_client = create_autospec(HttpClient, spec_set=True, instance=True)
        cls.mqtt_client = create_autospec(MqttClient, spec_set=True, instance=True)

    def setUp(self):
        self.http_client.reset_mock()
        self.mqtt_client.reset_mock()
