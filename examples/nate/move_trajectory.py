import logging
import math

from pyniryo.nate.client import Nate
from pyniryo.nate.models.geometry import Pose
from pyniryo.nate.models.motion import Waypoint, Planner

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

logger = logging.getLogger("pyniryo.nate.move_poses")


def basic_poses(nate: Nate):
    trajectory = [
        Waypoint(pose=Pose.with_rpy(0.4, 0.5, 0.3, -math.pi, 0, math.pi / 2), planner=Planner.LIN, frame_id='tool0'),
        Waypoint(pose=Pose(0.4, 0.5, 0.5, -0.707, -0.707, 0, 0), planner=Planner.LIN, frame_id='tool0'),
        Waypoint(pose=Pose(0.4, -0.5, 0.5, -0.707, -0.707, 0, 0), planner=Planner.LIN, frame_id='tool0'),
        Waypoint(pose=Pose.with_rpy(0.4, -0.5, 0.3, -math.pi, 0, math.pi / 2), planner=Planner.LIN, frame_id='tool0'),
    ]

    cmd = nate.robot.move(trajectory)
    cmd.wait()
    logger.info(f"Move command {cmd.command_id} completed with state: {cmd.state}")


def main():
    n = Nate()
    while True:
        basic_poses(n)


if __name__ == '__main__':
    main()
