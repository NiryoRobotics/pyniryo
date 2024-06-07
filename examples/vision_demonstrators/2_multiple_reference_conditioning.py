"""
This script shows an example of how to use Ned's vision to
make a conditioning according to the objects' color.

The objects will be conditioned in a grid of dimension grid_dimension. The Y axis corresponds
to the ObjectColor : BLUE / RED / GREEN. It will be 3
The X axis corresponds to how many objects can be put on the same line before increasing
the conditioning height.
Once a line is completed, objects will be pack over the lower level
"""

from pyniryo import NiryoRobot, PoseObject, ObjectColor

# -- MUST Change these variables
robot_ip_address = '<robot_ip_address>'  # IP address of the robot
workspace_name = "workspace_1"  # Robot's Workspace Name

# -- Can change these variables
grid_dimension = (3, 3)

# -- Should Change these variables
# The pose from where the image processing happen
observation_pose = PoseObject(0.2, 0.0, 0.3, 3.14, -0.01, -0.01)

# Center of the conditioning area
first_conditioning_pose = PoseObject(0.0, -0.25, 0.12, 3.14, -0.01, -1.56)


# -- MAIN PROGRAM
def process(niryo_robot: NiryoRobot):
    try_without_success = 0
    count_dict = {
        ObjectColor.BLUE: 0,
        ObjectColor.RED: 0,
        ObjectColor.GREEN: 0,
    }
    # Loop until too many failures
    while try_without_success < 3:
        # Moving to observation pose
        niryo_robot.move(observation_pose)
        # Trying to get object via Vision Pick
        obj_found, _, color = niryo_robot.vision_pick(workspace_name)
        if not obj_found:
            try_without_success += 1
            continue

        # Choose X & Z position according to how the color line is filled
        offset_x_ind = count_dict[color] % grid_dimension[0]
        offset_z_ind = count_dict[color] // grid_dimension[0]

        # Choose Y position according to ObjectColor
        if color == ObjectColor.BLUE:
            offset_y_ind = -1
        elif color == ObjectColor.RED:
            offset_y_ind = 0
        else:
            offset_y_ind = 1
        # Going to place the object
        place_pose = first_conditioning_pose.copy_with_offsets(0.05 * offset_x_ind,
                                                               0.05 * offset_y_ind,
                                                               0.025 * offset_z_ind)
        niryo_robot.place(place_pose)
        # Increment count
        count_dict[color] += 1
        try_without_success = 0


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Changing tool
    robot.update_tool()
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Launching main process
    process(robot)
    # Ending
    robot.go_to_sleep()
    # Releasing connection
    robot.close_connection()
