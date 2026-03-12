import math
from pyniryo.nate import Nate
from pyniryo.nate.exceptions import PyNiryoError
from pyniryo.nate.models import Joints, Pose, Point, EulerAngles, Quaternion


def main():
    n = Nate()

    print('Example 1: Move with add_start=True')
    """
    add_start allows the user to send move commands without worrying about the current robot position.
    While it ensure the robot will always accept the move request, it's considered unsafe to use as it doesn't guarantee
    the exact path of the robot, which can lead to unexpected collisions. Use with caution and only in controlled environments.
    """

    joints = [
        Joints(0, 0, 0, 0, 0, 0),
        Joints(0, -1, 1, 0, 0, 0),
        Joints(0, 0, 0, 0, 0, 0),
        Joints(1, -1, 1, 0, 0, 0),
        Joints(1, 0, 0, 0, 0, 0),
    ]

    for j in joints:
        try:
            cmd = n.robot.move(j, add_start=True)
            cmd.wait()
        except PyNiryoError as e:
            print(f"Error moving joints {j}: {e}")

    print('Example 2: Move without add_start')
    """
    Without add_start, you have to provide the starting position of the robot. If the robot is not to the given position,
    the move request will fail. This allows for more predictable robot behavior and is safer to use in environments
    where collisions are a concern, but it requires more careful planning of the robot's trajectory.
    """

    joints.insert(0, n.robot.get_joints())
    for i in range(1, len(joints)):
        try:
            cmd = n.robot.move([joints[i - 1], joints[i]])
            cmd.wait()
        except PyNiryoError as e:
            print(f"Error moving joints {joints[i]}: {e}")

    print('Example 3: Move with poses')
    """
    Move requests with poses works the same than for the joints. Note that the starting point still have to be in joints.
    Pose objects can be instantiated in various ways; with a point and either a quaternion or a euler angle,
    or with a flat sequence of floats.
    """

    poses = [
        Pose(Point(0.3, 0.4, 0.3), EulerAngles(-math.pi, 0, math.pi / 2)),
        Pose(Point(0.3, 0.4, 0.5), Quaternion(-0.707, -0.707, 0, 0)),
        Pose.from_sequence(0.3, -0.4, 0.5, -0.707, -0.707, 0, 0),
        Pose.from_sequence(0.3, -0.4, 0.3, -math.pi, 0, math.pi / 2),
    ]

    for p in poses:
        try:
            cmd = n.robot.move([n.robot.get_joints(), p])
            cmd.wait()
        except PyNiryoError as e:
            print(f"Error moving pose {p}: {e}")

    print('Example 4: Move with a sequence')
    """
    Instead of moving point by point, you can pass a sequence of Pose or Joints which will be considered as waypoint for
    the generated trajectory.
    """

    sequence_a = [
        n.robot.get_joints(),
        Joints(0, 0, 0, 0, 0, 0),
        Pose(Point(0.3, 0.4, 0.3), EulerAngles(-math.pi, 0, math.pi / 2)),
        Joints(1, -1, 1, 0, 0, 0),
        Joints(1, 0, 0, 0, 0, 0),
        Pose.from_sequence(0.3, -0.4, 0.3, -math.pi, 0, math.pi / 2),
        Joints(1, -1, 1, 0, 0, 0),
    ]

    sequence_b = [
        sequence_a[-1],
        Joints(1, 0, 0, 0, 0, 0),
        Pose(Point(0.3, -0.4, 0.5), Quaternion(-0.707, -0.707, 0, 0)),
        Joints(1, -1, 1, 0, 0, 0),
        Pose(Point(0.3, 0.4, 0.3), EulerAngles(-math.pi, 0, math.pi / 2)),
    ]

    try:
        cmd = n.robot.move(sequence_a)
        cmd.wait()
    except PyNiryoError as e:
        print(f"Error moving sequence A: {e}")

    try:
        cmd = n.robot.move(sequence_b)
        cmd.wait()
    except PyNiryoError as e:
        print(f"Error moving sequence B: {e}")


if __name__ == '__main__':
    main()
