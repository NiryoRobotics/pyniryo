from pyniryo import PinID
from .src.base_test import BaseTestTcpApi


class Test01Tool(BaseTestTcpApi):

    def test_010_update_tool(self):
        self.assertIsNone(self.niryo_robot.update_tool())

    def test_020_grasp_with_tool(self):
        self.assertIsNone(self.niryo_robot.grasp_with_tool())

    def test_030_release_with_tool(self):
        self.assertIsNone(self.niryo_robot.release_with_tool())


class Test02Grippers(BaseTestTcpApi):

    def setUp(self):
        self.niryo_robot.update_tool()

    def test_020_open_gripper(self):
        self.assertIsNone(self.niryo_robot.open_gripper())

    def test_030_close_gripper(self):
        self.assertIsNone(self.niryo_robot.close_gripper())

    def test_040_open_gripper_speed(self):
        self.assertIsNone(self.niryo_robot.open_gripper(speed=500))

    def test_050_close_gripper_speed(self):
        self.assertIsNone(self.niryo_robot.close_gripper(speed=500))

    def test_060_open_gripper_torque(self):
        self.assertIsNone(self.niryo_robot.open_gripper(max_torque_percentage=100, hold_torque_percentage=50))

    def test_070_close_gripper_torque(self):
        self.assertIsNone(self.niryo_robot.close_gripper(max_torque_percentage=100, hold_torque_percentage=50))


class Test03Electromagnet(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.electromagnet_pin = PinID.DO4

    def setUp(self):
        self.niryo_robot.update_tool()

    def test_010_setup_electromagnet(self):
        self.assertIsNone(self.niryo_robot.setup_electromagnet(self.electromagnet_pin))

    def test_020_activate_electromagnet(self):
        self.assertIsNone(self.niryo_robot.activate_electromagnet(self.electromagnet_pin))

    def test_030_deactivate_electromagnet(self):
        self.assertIsNone(self.niryo_robot.deactivate_electromagnet(self.electromagnet_pin))


class Test04VacuumPump(BaseTestTcpApi):

    def setUp(self):
        self.niryo_robot.update_tool()

    def test_010_pull_air_vacuum_pump(self):
        self.assertIsNone(self.niryo_robot.pull_air_vacuum_pump())

    def test_020_push_air_vacuum_pump(self):
        self.assertIsNone(self.niryo_robot.push_air_vacuum_pump())
