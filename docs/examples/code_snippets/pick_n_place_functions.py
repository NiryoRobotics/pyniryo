from pyniryo import NiryoRobot
from tool_action import pick_pose, place_pose


def pick_n_place_version_1(robot: NiryoRobot):
    height_offset = 0.05  # Offset according to Z-Axis to go over pick & place poses

    pick_pose_high = pick_pose.copy_with_offsets(z_offset=height_offset)
    place_pose_high = place_pose.copy_with_offsets(z_offset=height_offset)

    # Going Over Object
    robot.move(pick_pose_high)
    # Opening Gripper
    robot.release_with_tool()
    # Going to picking place and closing gripper
    robot.move(pick_pose)
    robot.grasp_with_tool()
    # Raising
    robot.move(pick_pose_high)

    # Going Over Place pose
    robot.move(place_pose_high)
    # Going to Place pose
    robot.move(place_pose)
    # Opening Gripper
    robot.release_with_tool()
    # Raising
    robot.move(place_pose_high)


def pick_n_place_version_2(robot: NiryoRobot):
    # Pick
    robot.pick(pick_pose)
    # Place
    robot.place(place_pose)


def pick_n_place_version_3(robot: NiryoRobot):
    # Pick & Place
    robot.pick_and_place(pick_pose, place_pose)
