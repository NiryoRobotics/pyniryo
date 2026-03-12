from pyniryo.nate import Nate
from pyniryo.nate.models import Joints, Pose, Point, Quaternion, Planner, Waypoint


def main():
    n = Nate()

    print("Advanced Move")
    """
    To make highly customizable move request, you can use the Waypoint object. 
    It exposes all the possible configuration for a waypoint.
    """

    traj1 = [
        Waypoint(joints=n.robot.get_joints()),
        Waypoint(pose=Pose(Point(0.519151, -0.007055, 0.745475), Quaternion(0.714187, -0.004785, 0.699922, 0.004849)),
                 frame_id='tool0',
                 planner=Planner.LIN,
                 blending_radius=None),
        Waypoint(pose=Pose(Point(0.42657, -0.387699, 0.207111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=0.05),
        Waypoint(pose=Pose(Point(0.42657, -0.387699, 0.107111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=None),
        Waypoint(joints=Joints(-0.7371640549983692,
                               0.5328665761917746,
                               0.12104067154410136,
                               -0.002080461443569901,
                               0.8948956295127103,
                               -0.00012463593901570835))
    ]

    cmd = n.robot.move(traj1)
    cmd.wait()

    traj2 = [
        traj1[-1],
        Waypoint(pose=Pose(Point(0.42657, -0.387699, 0.207111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=0.05),
        Waypoint(pose=Pose(Point(0.494032, 0, 0.558924), Quaternion(0.999512, 0, 0.031236, 0)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=0.20),
        Waypoint(pose=Pose(Point(0.42657, 0.289767, 0.207111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=0.05),
        Waypoint(pose=Pose(Point(0.42657, 0.289767, 0.107111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=None),
        Waypoint(joints=Joints(0.6032283574561041,
                               0.4012797867309595,
                               0.3370922781378696,
                               -0.02927027090884289,
                               0.8291166158521891,
                               1.3587138954897824)),
    ]
    cmd = n.robot.move(traj2)
    cmd.wait()

    traj3 = [
        traj2[-1],
        Waypoint(pose=Pose(Point(0.42657, 0.289767, 0.207111), Quaternion(0.933043, -0.359598, 0.009869, 0.00471)),
                 frame_id='eef_tcp',
                 planner=Planner.LIN,
                 blending_radius=0.05,
                 velocity_factor=0.5),
        Waypoint(pose=Pose(Point(0.519151, -0.007055, 0.745475), Quaternion(0.714187, -0.004785, 0.699922, 0.004849)),
                 frame_id='tool0',
                 planner=Planner.LIN,
                 blending_radius=None,
                 acceleration_factor=0.2)
    ]
    cmd = n.robot.move(traj3)
    cmd.wait()


if __name__ == '__main__':
    main()
