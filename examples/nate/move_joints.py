import time

from pyniryo.nate.client import Nate
from pyniryo.nate.exceptions import PyNiryoError
from pyniryo.nate.models import Joints

from .log_utils import get_logger

logger = get_logger(__name__)


def pick_and_place(nate: Nate, desired_time: float = None):
    """
    Perform a pick and place operation with the robot.

    :param nate: The Nate client instance.
    :param desired_time: The time to complete each move.
    """
    while True:
        for joint in [
                Joints(1, -1.5, -1.3),
                Joints(1, -0.5, 0),
                Joints(-1, -0.5, 0),
                Joints(1, -0.5, 0),
        ]:
            try:
                nate.motion.move(joint, desired_time=desired_time).wait()
            except PyNiryoError as e:
                logger.error(f"Error during pick and place operation: {e}")


def basic_poses(nate: Nate):
    joints = [
        Joints(0, -1, 1),
        Joints(0, 0, 0),
        Joints(1, -1, 1),
        Joints(1, 0, 0),
    ]

    for j in joints:
        try:
            cmd = nate.motion.move(j, desired_time=0.5)
            cmd.wait()
            logger.info(f"Move command {cmd.command_id} completed with state: {cmd.state}")
        except PyNiryoError as e:
            logger.error(f"Error moving joints {j}: {e}")
            time.sleep(0.5)


def main():
    n = Nate()
    n.motion.move(Joints(0, 0, 0), desired_time=4).wait()
    input("Press any key to continue...")
    # while True:
    pick_and_place(n)


if __name__ == '__main__':
    main()
