import time
from contextlib import contextmanager

from .src.base_test import BaseTestTcpApi


class TestLedRing(BaseTestTcpApi):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        n_leds = 30
        cls.DEFAULT_PERIOD = 0.5
        cls.DEFAULT_ITERATIONS = 5

        cls.CYAN = [0, 255, 255]
        cls.MAGENTA = [255, 0, 255]
        cls.YELLOW = [255, 255, 0]
        cls.BLUE_TO_RED_GRADIENT = [[255 * (i / n_leds), 0, 255 - (255 * i / n_leds)] for i in range(n_leds)]

    def setUp(self):
        super().setUp()
        # The robot status takes some time before changing its status to running autonomous. This will cause the client
        # to crash if the 1st command is a led ring command, because the status must be to autonomous in order to
        # change the led ring. This is a quick and dirty fix to this problem
        time.sleep(0.5)

    @contextmanager
    def assertBlockingAnimation(self, period=None, iterations=None):
        """
        Context manager to ensure an animation function blocks until the animation is complete.

        :param period: The period of the animation.
        :param iterations: The number of iterations of the animation.
        """
        if period is None:
            period = self.DEFAULT_PERIOD
        if iterations is None:
            iterations = self.DEFAULT_ITERATIONS

        start_time = time.time()
        yield
        elapsed_time = time.time() - start_time
        self.assertGreaterEqual(elapsed_time, period * iterations)

    def test_010_set_led_color(self):
        for i, color in enumerate(self.BLUE_TO_RED_GRADIENT):
            self.assertIsNone(self.niryo_robot.set_led_color(i, color))

    def test_020_led_ring_solid(self):
        self.assertIsNone(self.niryo_robot.led_ring_solid(self.CYAN))
        self.assertIsNone(self.niryo_robot.led_ring_solid(self.MAGENTA))
        self.assertIsNone(self.niryo_robot.led_ring_solid(self.YELLOW))

    def test_030_led_ring_custom(self):
        self.assertIsNone(self.niryo_robot.led_ring_custom(led_colors=self.BLUE_TO_RED_GRADIENT))

    def test_040_led_ring_turn_off(self):
        self.assertIsNone(self.niryo_robot.led_ring_turn_off())

    def test_050_test_led_ring_flashing(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_flashing(period=self.DEFAULT_PERIOD,
                                               iterations=self.DEFAULT_ITERATIONS,
                                               color=self.YELLOW,
                                               wait=True)

    def test_060_led_ring_alternate(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_alternate(period=self.DEFAULT_PERIOD,
                                                iterations=self.DEFAULT_ITERATIONS,
                                                color_list=[self.CYAN, self.MAGENTA],
                                                wait=True)

    def test_070_led_ring_chase(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_chase(period=self.DEFAULT_PERIOD,
                                            iterations=self.DEFAULT_ITERATIONS,
                                            color=self.YELLOW,
                                            wait=True)

    def test_080_led_ring_go_up(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_go_up(period=self.DEFAULT_PERIOD,
                                            iterations=self.DEFAULT_ITERATIONS,
                                            color=self.CYAN,
                                            wait=True)

    def test_090_led_ring_go_up_down(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_go_up_down(period=self.DEFAULT_PERIOD,
                                                 iterations=self.DEFAULT_ITERATIONS,
                                                 color=self.MAGENTA,
                                                 wait=True)

    def test_100_led_ring_breath(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_breath(period=self.DEFAULT_PERIOD,
                                             iterations=self.DEFAULT_ITERATIONS,
                                             color=self.YELLOW,
                                             wait=True)

    def test_110_led_ring_snake(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_snake(period=self.DEFAULT_PERIOD,
                                            iterations=self.DEFAULT_ITERATIONS,
                                            color=self.CYAN,
                                            wait=True)

    def test_120_led_ring_rainbow(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_rainbow(period=self.DEFAULT_PERIOD, iterations=self.DEFAULT_ITERATIONS, wait=True)

    def test_130_led_ring_rainbow_cycle(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_rainbow_cycle(period=self.DEFAULT_PERIOD,
                                                    iterations=self.DEFAULT_ITERATIONS,
                                                    wait=True)

    def test_140_led_ring_rainbow_chase(self):
        with self.assertBlockingAnimation():
            self.niryo_robot.led_ring_rainbow_chase(period=self.DEFAULT_PERIOD,
                                                    iterations=self.DEFAULT_ITERATIONS,
                                                    wait=True)
