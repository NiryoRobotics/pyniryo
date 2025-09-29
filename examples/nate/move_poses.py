import logging
import math

from pyniryo.nate.client import Nate
from pyniryo.nate.models import Pose

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

logger = logging.getLogger("pyniryo.nate.move_poses")


def basic_poses(nate: Nate):
    poses = [
        Pose(0.2, 1, 0.5, -0.707, -0.707, 0, 0),
        Pose.with_rpy(0.2, 1, 0.3, -math.pi, 0, math.pi / 2),
    ]

    for p in poses:
        cmd = nate.robot.move(p, frame_id='tool0')
        cmd.wait()
        logger.info(f"Move command {cmd.command_id} completed with state: {cmd.state}")


def main():
    n = Nate()
    while True:
        basic_poses(n)


if __name__ == '__main__':
    main()
