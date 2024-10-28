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
    VACUUM_PUMP_2 = 32


@unique
class PinMode(Enum):
    """
    Enumeration of Pin Modes
    """
    OUTPUT = 0
    INPUT = 1


@unique
class PinState(Enum):
    """
    Pin State is either LOW or HIGH
    """
    LOW = False
    HIGH = True


@unique
class PinID(Enum):
    """
    Enumeration of Robot Pins
    """
    GPIO_1A = "1A"
    GPIO_1B = "1B"
    GPIO_1C = "1C"
    GPIO_2A = "2A"
    GPIO_2B = "2B"
    GPIO_2C = "2C"

    SW_1 = "SW1"
    SW_2 = "SW2"

    DO1 = "DO1"
    DO2 = "DO2"
    DO3 = "DO3"
    DO4 = "DO4"
    DI1 = "DI1"
    DI2 = "DI2"
    DI3 = "DI3"
    DI4 = "DI4"
    DI5 = "DI5"

    AI1 = "AI1"
    AI2 = "AI2"
    AO1 = "AO1"
    AO2 = "AO2"


# - Conveyor
class ConveyorID(Enum):
    """
    Enumeration of Conveyor IDs used for Conveyor control
    """
    NONE = 0
    ID_1 = -1
    ID_2 = -2


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
    GET_COLLISION_DETECTED = 5
    CLEAR_COLLISION_DETECTED = 6
    HANDSHAKE = 7

    # - Move
    # Pose

    GET_JOINTS = 10
    GET_POSE = 11
    GET_POSE_QUAT = 12
    GET_POSE_V2 = 13

    MOVE_JOINTS = 20
    MOVE_POSE = 21
    SHIFT_POSE = 22

    MOVE_LINEAR_POSE = 23
    SHIFT_LINEAR_POSE = 24

    JOG_JOINTS = 25
    JOG_POSE = 26

    FORWARD_KINEMATICS = 27
    INVERSE_KINEMATICS = 28

    MOVE = 29
    JOG = 30

    FORWARD_KINEMATICS_V2 = 31
    INVERSE_KINEMATICS_V2 = 32

    # Saved Pose
    GET_POSE_SAVED = 50
    SAVE_POSE = 51
    DELETE_POSE = 52
    GET_SAVED_POSE_LIST = 53

    # Pick & Place

    PICK_FROM_POSE = 60
    PLACE_FROM_POSE = 61
    PICK_AND_PLACE = 62
    PICK = 63
    PLACE = 64

    # Trajectories
    GET_TRAJECTORY_SAVED = 80
    GET_SAVED_TRAJECTORY_LIST = 81
    EXECUTE_REGISTERED_TRAJECTORY = 82
    EXECUTE_TRAJECTORY_FROM_POSES = 83
    EXECUTE_TRAJECTORY_FROM_POSES_AND_JOINTS = 84
    SAVE_TRAJECTORY = 85
    SAVE_LAST_LEARNED_TRAJECTORY = 86
    UPDATE_TRAJECTORY_INFOS = 87
    DELETE_TRAJECTORY = 88
    CLEAN_TRAJECTORY_MEMORY = 89
    EXECUTE_TRAJECTORY = 90

    # Dynamic frames
    GET_SAVED_DYNAMIC_FRAME_LIST = 95
    GET_SAVED_DYNAMIC_FRAME = 96
    SAVE_DYNAMIC_FRAME_FROM_POSES = 97
    SAVE_DYNAMIC_FRAME_FROM_POINTS = 98
    EDIT_DYNAMIC_FRAME = 99
    DELETE_DYNAMIC_FRAME = 100
    MOVE_RELATIVE = 101
    MOVE_LINEAR_RELATIVE = 102

    # - Tools
    UPDATE_TOOL = 120
    OPEN_GRIPPER = 121
    CLOSE_GRIPPER = 122
    PERCENTAGE_OPEN_GRIPPER = 266
    PULL_AIR_VACUUM_PUMP = 123
    PUSH_AIR_VACUUM_PUMP = 124
    SETUP_ELECTROMAGNET = 125
    ACTIVATE_ELECTROMAGNET = 126
    DEACTIVATE_ELECTROMAGNET = 127
    GET_CURRENT_TOOL_ID = 128
    GRASP_WITH_TOOL = 129
    RELEASE_WITH_TOOL = 130
    ENABLE_TCP = 140
    SET_TCP = 141
    RESET_TCP = 142
    TOOL_REBOOT = 145
    GET_TCP = 146

    # - Hardware
    SET_PIN_MODE = 150
    DIGITAL_WRITE = 151
    DIGITAL_READ = 152
    GET_DIGITAL_IO_STATE = 153
    GET_HARDWARE_STATUS = 154
    ANALOG_WRITE = 155
    ANALOG_READ = 156
    GET_ANALOG_IO_STATE = 157
    CUSTOM_BUTTON_STATE = 158

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

    SET_IMAGE_BRIGHTNESS = 230
    SET_IMAGE_CONTRAST = 231
    SET_IMAGE_SATURATION = 232
    GET_IMAGE_PARAMETERS = 235

    # - Sound
    PLAY_SOUND = 240
    SET_VOLUME = 241
    STOP_SOUND = 242
    DELETE_SOUND = 243
    IMPORT_SOUND = 244
    GET_SOUNDS = 245
    GET_SOUND_DURATION = 246
    SAY = 247

    # Led Ring
    LED_RING_SOLID = 250
    LED_RING_TURN_OFF = 251
    LED_RING_FLASH = 252
    LED_RING_ALTERNATE = 253
    LED_RING_CHASE = 254
    LED_RING_WIPE = 255
    LED_RING_RAINBOW = 256
    LED_RING_RAINBOW_CYCLE = 257
    LED_RING_RAINBOW_CHASE = 258
    LED_RING_GO_UP = 259
    LED_RING_GO_UP_DOWN = 260
    LED_RING_BREATH = 261
    LED_RING_SNAKE = 262
    LED_RING_CUSTOM = 263
    LED_RING_SET_LED = 264


class TcpVersion(Enum):
    LEGACY = 0
    DH_CONVENTION = 1


class LengthUnit(Enum):
    METERS = 0
    MILLIMETERS = 1
