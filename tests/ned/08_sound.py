import time

from pyniryo import TcpCommandException, NiryoRobotException

from src.base_test import BaseTestTcpApi


class TestSound(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sound_name = 'ready.wav'

    def test_010_get_sounds(self):
        self.assertIsNotNone(self.niryo_robot.get_sounds())
        self.assertIsInstance(self.niryo_robot.get_sounds(), list)

    def test_020_get_sound_duration(self):
        self.assertIsInstance(self.niryo_robot.get_sound_duration(self.sound_name), float)
        self.assertGreater(self.niryo_robot.get_sound_duration(self.sound_name), 0)

    def test_030_set_volume(self):
        self.assertIsNone(self.niryo_robot.set_volume(0))
        self.assertIsNone(self.niryo_robot.set_volume(50))
        self.assertIsNone(self.niryo_robot.set_volume(100))

    def test_040_set_volume_out_of_range(self):
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_volume(-1)
        with self.assertRaises(TcpCommandException):
            self.niryo_robot.set_volume(201)

    def test_050_play_sound(self):
        self.assertIsNone(self.niryo_robot.play_sound(self.sound_name, False))

    def test_060_play_sound_wait_end(self):
        duration = self.niryo_robot.get_sound_duration(self.sound_name)
        start_time = time.time()
        self.assertIsNone(self.niryo_robot.play_sound(self.sound_name, True))
        end_time = time.time()
        self.assertGreater(end_time - start_time, duration)

    def test_070_stop_sound(self):
        self.assertIsNone(self.niryo_robot.play_sound(self.sound_name, False))
        self.assertIsNone(self.niryo_robot.stop_sound())

    def test_080_say(self):
        self.assertIsNone(self.niryo_robot.say("Test", 0))
