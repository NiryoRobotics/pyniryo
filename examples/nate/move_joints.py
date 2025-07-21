import logging

from pyniryo.nate.client import Nate
from pyniryo.nate.models import Joints

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def main():
    n = Nate('127.0.0.1')
    joints = [
        Joints(0, -1, 1, 2, 0, 0),
        Joints(0, 0, 0, 0, 0, 0),
        Joints(1, -1, 1, 2, 0, 0),
        Joints(1, 0, 0, 0, 0, 0),
    ]
    for j in joints:
        n.motion.move(j, desired_time=0.5).wait()


if __name__ == '__main__':
    main()
