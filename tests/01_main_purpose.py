import os
import unittest
from sys import version_info

from pyniryo import CalibrateMode, TcpCommandException, PinID, ConveyorID, NiryoRobot
from pyniryo.api.exceptions import ClientNotConnectedException

from .src.base_test import BaseTestTcpApi


class Test01Connection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.robot_ip_address = os.environ.get('ROBOT_IP_ADDRESS')
        cls.niryo_robot: NiryoRobot = NiryoRobot()

    def test_010_connect(self):
        with self.assertLogs() as logs_context:
            self.niryo_robot.connect(self.robot_ip_address)
        self.assertEqual(len(logs_context.output), 1)
        _level, _logger_name, log_msg = logs_context.output[0].split(':')
        expected_output = f'Connected to server ({self.robot_ip_address}) on port 40001'
        self.assertEqual(log_msg, expected_output)

    def test_020_close_connection(self):
        with self.assertLogs() as logs_context:
            self.niryo_robot.close_connection()
        self.assertEqual(len(logs_context.output), 1)
        _level, _logger_name, log_msg = logs_context.output[0].split(':')
        expected_output = 'Disconnected from robot'
        self.assertEqual(log_msg, expected_output)

    def test_030_connect_wrong_ip(self):
        with self.assertRaises(ClientNotConnectedException):
            self.niryo_robot.connect('255.255.255.255')

    if version_info >= (3, 10):

        def test_040_connect_no_verbose(self):
            robot_ip_address = os.environ.get('ROBOT_IP_ADDRESS', '127.0.0.1')
            self.niryo_robot = NiryoRobot(verbose=False)
            with self.assertNoLogs():
                self.niryo_robot.connect(robot_ip_address)

        def test_050_close_connection_no_verbose(self):
            with self.assertNoLogs():
                self.niryo_robot.close_connection()


class Test02Calibration(BaseTestTcpApi):

    def test_010_calibration(self):
        self.assertIsNone(self.niryo_robot.calibrate(CalibrateMode.AUTO))
        self.assertIsNone(self.niryo_robot.calibrate_auto())
        self.assertIsNone(self.niryo_robot.calibrate(CalibrateMode.MANUAL))
        self.assertFalse(self.niryo_robot.need_calibration())

    def test_020_wrong_param(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(PinID)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.calibrate(ConveyorID.ID_1)


class Test03LearningMode(BaseTestTcpApi):

    def test_010_learning_mode(self):
        for b in [True, False]:
            self.assertIsNone(self.niryo_robot.set_learning_mode(b))
            self.assertEqual(self.niryo_robot.learning_mode, b)

    def test_020_setter(self):
        for b in [True, False]:
            self.niryo_robot.learning_mode = b
            self.assertEqual(self.niryo_robot.learning_mode, b)

    def test_030_wrong_param(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_learning_mode(PinID)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_learning_mode(1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_learning_mode(ConveyorID.ID_1)

    def test_040_setter_wrong_param(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.learning_mode = PinID
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.learning_mode = 1
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.learning_mode = ConveyorID.ID_1


class Test04SetArmVelocity(BaseTestTcpApi):

    def test_010_set_arm_velocity(self):
        self.assertIsNone(self.niryo_robot.set_arm_max_velocity(1))
        self.assertIsNone(self.niryo_robot.set_arm_max_velocity(100))

    def test_020_wrong_param(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_arm_max_velocity(-95)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_arm_max_velocity(0)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_arm_max_velocity(101)


if __name__ == '__main__':
    unittest.main()
