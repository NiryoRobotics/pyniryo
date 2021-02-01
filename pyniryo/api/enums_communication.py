from enum import Enum, unique

TCP_PORT = 40001  # Port used for TCP communication
READ_SIZE = 512  # Buffer used for receiving TCP packet
TCP_TIMEOUT = 5  # Time before timeout is raised

# - Infos on the JSON size
# nbr_bytes : number of bytes on which the size is coded
# type : size coding type
DEFAULT_PACKET_SIZE_INFOS = {
    "nbr_bytes": 2,
    "type": '@H',
}


@unique
class CalibrateMode(Enum):
    """
    Enumeration of Calibration Modes
    """
    AUTO = 0
    MANUAL = 1


@unique
class RobotAxis(Enum):
    """
    Enumeration of Robot Axis : it used for Shift command
    """
    X = 0
    Y = 1
    Z = 2
    ROLL = 3
    PITCH = 4
    YAW = 5


@unique
class ToolID(Enum):
    """
    Enumeration of Tools IDs
    """
    NONE = 0
    GRIPPER_1 = 11
    GRIPPER_2 = 12
    GRIPPER_3 = 13
    ELECTROMAGNET_1 = 30
    VACUUM_PUMP_1 = 31


@unique
class PinMode(Enum):
    """
    Enumeration of Pin Modes
    """
    INPUT = 0
    OUTPUT = 1


@unique
class PinState(Enum):
    """
    Pin State is either LOW or HIGH
    """
    LOW = 0
    HIGH = 1


@unique
class PinID(Enum):
    """
    Enumeration of Robot Pins
    """
    GPIO_1A = 0
    GPIO_1B = 1
    GPIO_1C = 2
    GPIO_2A = 3
    GPIO_2B = 4
    GPIO_2C = 5


# - Conveyor

class ConveyorID(Enum):
    """
    Enumeration of Conveyor IDs used for Conveyor control
    """
    NONE = 0
    ID_1 = 12
    ID_2 = 13


@unique
class ConveyorDirection(Enum):
    """
    Enumeration of Conveyor Directions used for Conveyor control
    """
    FORWARD = 1
    BACKWARD = -1


# - Vision

@unique
class ObjectColor(Enum):
    """
    Enumeration of Colors available for image processing
    """
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    ANY = "ANY"


@unique
class ObjectShape(Enum):
    """
    Enumeration of Shapes available for image processing
    """
    SQUARE = "SQUARE"
    CIRCLE = "CIRCLE"
    ANY = "ANY"


@unique
class Command(Enum):
    """
    Enumeration of all commands used
    """
    # Main purpose
    CALIBRATE = 0
    SET_LEARNING_MODE = 1
    GET_LEARNING_MODE = 2
    SET_ARM_MAX_VELOCITY = 3
    SET_JOG_CONTROL = 4

    # - Move
    # Pose

    GET_JOINTS = 10
    GET_POSE = 11
    GET_POSE_QUAT = 12

    MOVE_JOINTS = 20
    MOVE_POSE = 21
    SHIFT_POSE = 22

    MOVE_LINEAR_POSE = 23

    JOG_JOINTS = 25
    JOG_POSE = 26

    FORWARD_KINEMATICS = 27
    INVERSE_KINEMATICS = 28

    # Saved Pose
    GET_POSE_SAVED = 50
    SAVE_POSE = 51
    DELETE_POSE = 52
    GET_SAVED_POSE_LIST = 53

    # Pick & Place

    PICK_FROM_POSE = 60
    PLACE_FROM_POSE = 61
    PICK_AND_PLACE = 62

    # Trajectories
    GET_TRAJECTORY_SAVED = 80
    EXECUTE_TRAJECTORY_FROM_POSES = 81
    EXECUTE_TRAJECTORY_SAVED = 82
    SAVE_TRAJECTORY = 83
    DELETE_TRAJECTORY = 84
    GET_SAVED_TRAJECTORY_LIST = 85

    # - Tools
    UPDATE_TOOL = 120
    OPEN_GRIPPER = 121
    CLOSE_GRIPPER = 122
    PULL_AIR_VACUUM_PUMP = 123
    PUSH_AIR_VACUUM_PUMP = 124
    SETUP_ELECTROMAGNET = 125
    ACTIVATE_ELECTROMAGNET = 126
    DEACTIVATE_ELECTROMAGNET = 127
    GET_CURRENT_TOOL_ID = 128
    GRASP_WITH_TOOL = 129
    RELEASE_WITH_TOOL = 130

    # - Hardware
    SET_PIN_MODE = 150
    DIGITAL_WRITE = 151
    DIGITAL_READ = 152
    GET_DIGITAL_IO_STATE = 153
    GET_HARDWARE_STATUS = 154

    # - Conveyor
    SET_CONVEYOR = 180
    UNSET_CONVEYOR = 181
    CONTROL_CONVEYOR = 182
    GET_CONNECTED_CONVEYORS_ID = 183

    # - Vision
    GET_IMAGE_COMPRESSED = 200
    GET_TARGET_POSE_FROM_REL = 201
    GET_TARGET_POSE_FROM_CAM = 202

    VISION_PICK = 203
    MOVE_TO_OBJECT = 205
    DETECT_OBJECT = 204

    GET_CAMERA_INTRINSICS = 210

    SAVE_WORKSPACE_FROM_POSES = 220
    SAVE_WORKSPACE_FROM_POINTS = 221
    DELETE_WORKSPACE = 222
    GET_WORKSPACE_RATIO = 223
    GET_WORKSPACE_LIST = 224
