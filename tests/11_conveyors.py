import time

from pyniryo import ConveyorID, ConveyorDirection

from src.base_test import BaseTestTcpApi


class Test01Ids(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conveyor_id = None

    def test_010_set_conveyor(self):
        print()
        conveyor_id = self.niryo_robot.set_conveyor()
        self.assertIsInstance(conveyor_id, ConveyorID)
        type(self).conveyor_id = conveyor_id

    def test_020_get_connected_conveyors_id(self):
        connected_conveyors_id = self.niryo_robot.get_connected_conveyors_id()
        self.assertIsInstance(connected_conveyors_id, list)
        self.assertIn(type(self).conveyor_id, connected_conveyors_id)
        for conveyor_id in connected_conveyors_id:
            self.assertIsInstance(conveyor_id, ConveyorID)

    def test_030_unset_conveyor(self):
        self.assertIsNone(self.niryo_robot.unset_conveyor(type(self).conveyor_id))


class Test02Control(BaseTestTcpApi):

    def setUp(self):
        super().setUp()
        self.conveyor_id = self.niryo_robot.set_conveyor()

    def test_010_run_conveyor(self):
        self.assertIsNone(self.niryo_robot.run_conveyor(self.conveyor_id))

    def test_020_get_conveyors_feedback(self):
        conveyors_feedback = self.niryo_robot.get_conveyors_feedback()
        self.assertIsInstance(conveyors_feedback, list)
        self.assertGreater(len(conveyors_feedback), 0)
        conveyor_feedback = conveyors_feedback[0]
        self.assertIsInstance(conveyor_feedback, dict)

        self.assertIn('conveyor_id', conveyor_feedback)
        self.assertIsInstance(conveyor_feedback['conveyor_id'], ConveyorID)

        self.assertIn('connection_state', conveyor_feedback)
        self.assertIsInstance(conveyor_feedback['connection_state'], bool)

        self.assertIn('speed', conveyor_feedback)
        self.assertIsInstance(conveyor_feedback['speed'], int)

        self.assertIn('direction', conveyor_feedback)
        self.assertIsInstance(conveyor_feedback['direction'], ConveyorDirection)

    def test_030_control_conveyor(self):
        for direction in ConveyorDirection:
            for speed in range(0, 100, 20):
                self.assertIsNone(self.niryo_robot.control_conveyor(self.conveyor_id, True, speed, direction))
                time.sleep(1)

    def test_040_stop_conveyor(self):
        self.assertIsNone(self.niryo_robot.stop_conveyor(self.conveyor_id))
