from pyniryo import NiryoRobot, DigitalPinObject, PinID, PinMode, PinState, AnalogPinObject

from src.base_test import BaseTestTcpApi


class TestIOs(BaseTestTcpApi):

    def test_010_get_digital_io_state(self):
        digital_io_state = self.niryo_robot.get_digital_io_state()
        self.assertIsInstance(digital_io_state, list)
        self.assertGreater(len(digital_io_state), 0)
        for dio in digital_io_state:
            self.assertIsInstance(dio, DigitalPinObject)
            self.assertIsInstance(dio.pin_id, PinID)
            self.assertIsInstance(dio.name, str)
            self.assertIsInstance(dio.mode, PinMode)
            self.assertIsInstance(dio.state, PinState)

    def test_020_digital_io_state(self):
        self.assertEqual(repr(self.niryo_robot.get_digital_io_state()), repr(self.niryo_robot.digital_io_state))

    def test_030_get_analog_ios(self):
        analog_io_state = self.niryo_robot.get_analog_io_state()
        self.assertIsInstance(analog_io_state, list)
        self.assertGreater(len(analog_io_state), 0)
        for aio in analog_io_state:
            self.assertIsInstance(aio, AnalogPinObject)
            self.assertIsInstance(aio.pin_id, PinID)
            self.assertIsInstance(aio.name, str)
            self.assertIsInstance(aio.mode, PinMode)
            self.assertIsInstance(aio.value, (float, int))

    def test_040_analog_io_state(self):
        self.assertEqual(repr(self.niryo_robot.get_analog_io_state()), repr(self.niryo_robot.analog_io_state))

    def test_button(self):
        self.assertIsInstance(self.niryo_robot.get_custom_button_state(), str)
