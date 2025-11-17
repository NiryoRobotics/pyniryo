import time
import socket
import warnings
from contextlib import contextmanager

from typing_extensions import deprecated

from enum import Enum

import numpy as np

# Communication imports
from .enums_communication import (CalibrateMode,
                                  Command,
                                  ConveyorDirection,
                                  ConveyorID,
                                  ObjectColor,
                                  ObjectShape,
                                  PinID,
                                  PinMode,
                                  PinState,
                                  RobotAxis,
                                  TCP_PORT,
                                  TCP_TIMEOUT,
                                  ToolID)
from .communication_functions import dict_to_packet, receive_dict, receive_dict_w_payload

from .exceptions import (ClientNotConnectedException,
                         HostNotReachableException,
                         InvalidAnswerException,
                         NiryoRobotException,
                         TcpCommandException)
from .objects import PoseObject, HardwareStatusObject, DigitalPinObject, AnalogPinObject, JointsPosition, PoseMetadata
from ..utils.logging import get_logger
from ..version import __version__


def get_deprecation_msg(old_method, new_method):
    return (f'`{old_method}` is deprecated and will be deleted in future releases.'
            f' Use `{new_method}` instead.')


class NiryoRobot(object):

    def __init__(self, ip_address=None, verbose=True, logger=None):
        """
        Note that when passing a custom logger you're responsible for the logging
        configuration (Handlers registering).

        :param ip_address: IP address of the robot
        :type ip_address: str
        :param verbose: Enable or disable the information logs
        :type verbose: bool
        :param logger: A custom logger for the NiryoRobot's instance
        :type logger: logging.Logger
        """
        self.__ip_address = None
        self.__port = TCP_PORT
        self.__client_socket = None

        self.__timeout = TCP_TIMEOUT

        self.__is_connected = False

        if logger is None:
            self.__logger = get_logger(self.__class__.__name__)
        else:
            self.__logger = logger
        if not verbose:
            self.__logger.setLevel(logging.WARNING)

        # If user give IP Address, try to connect directly
        if ip_address is not None:
            self.connect(ip_address)

    def __del__(self):
        self.close_connection()

    def __str__(self):
        if self.__is_connected:
            msg = "\nConnected to server ({}) on port: {}\n".format(self.__ip_address, self.__port)
        else:
            msg = "Not Connected"

        return msg

    def __repr__(self):
        return self.__str__()

    def __get_deprecation_msg(self, old_method, new_method):
        return (f'`{self.__class__.__name__}.{old_method}()` is deprecated and will be deleted in future releases.'
                f' Use `{self.__class__.__name__}.{new_method}()` instead.')

    # -- Connection
    def connect(self, ip_address):
        """
        Connect to the TCP Server

        :param ip_address: IP Address
        :type ip_address: str
        :rtype: None
        """
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket.settimeout(self.__timeout)
        try:
            self.__client_socket.connect((ip_address, self.__port))
        except (socket.timeout, socket.error) as e:
            self.__client_socket = None
            raise ClientNotConnectedException("Unable to connect to the robot : {}".format(e))

        self.__is_connected = True
        self.__client_socket.settimeout(None)
        self.__ip_address = ip_address
        self.__logger.info("Connected to server ({}) on port {}".format(ip_address, self.__port))
        self.__handshake()

    def __close_socket(self):
        if self.__client_socket is not None and self.__is_connected is True:
            try:
                self.__client_socket.shutdown(socket.SHUT_RDWR)
                self.__client_socket.close()
            except socket.error:
                pass
            self.__is_connected = False
            self.__logger.info("Disconnected from robot")

    def close_connection(self):
        """
        Close connection with robot

        :rtype: None
        """
        self.__close_socket()
        self.__client_socket = None

    # -- SEND & RECEIVE

    # - Sending phase
    def __send_command(self, command_type, *parameter_list):
        if self.__is_connected is False:
            raise ClientNotConnectedException()
        if self.__client_socket is not None:
            try:
                ret_dict = self.__build_dict(command_type, *parameter_list)
                packet = dict_to_packet(ret_dict)
                self.__client_socket.send(packet)
            except socket.error as e:
                self.__logger.error(e)
                raise HostNotReachableException()

    @staticmethod
    def __build_dict(command_type, *parameter_list):
        command = command_type.name
        new_param_list = []
        for parameter in parameter_list:
            if parameter is None:
                new_param_list.append("None")
            elif isinstance(parameter, Enum):
                new_param_list.append(parameter.name)
            elif isinstance(parameter, bool):
                new_param_list.append(str(parameter).upper())
            else:
                new_param_list.append(parameter)

        return {"command": command, "param_list": new_param_list}

    # - Receiving

    def __receive_answer(self, with_payload):
        try:
            if not with_payload:
                received_dict = receive_dict(sckt=self.__client_socket)
                payload = None
            else:
                received_dict, payload = receive_dict_w_payload(sckt=self.__client_socket)
        except socket.error as e:
            self.__logger.error(e)
            raise HostNotReachableException()
        if not received_dict:
            raise HostNotReachableException()
        answer_status = received_dict["status"]
        if answer_status not in ["OK", "KO"]:
            raise InvalidAnswerException(answer_status)
        if received_dict["status"] != "OK":
            raise NiryoRobotException("Command {} KO : {}".format(received_dict['command'], received_dict["message"]))
        list_ret_param = received_dict["list_ret_param"]
        if len(list_ret_param) == 1:
            list_ret_param = list_ret_param[0]
        if not with_payload:
            return list_ret_param
        else:
            return list_ret_param, payload

    # - Wrapping functions
    def __send_n_receive(self, command_type, *parameter_list, **kwargs):
        with_payload = kwargs.get("with_payload", False)

        self.__send_command(command_type, *parameter_list)
        return self.__receive_answer(with_payload=with_payload)

    # Parameters checker
    def __check_enum_belonging(self, value, enum_):
        """
        Check if a value belong to an enum
        """
        if not isinstance(value, enum_):
            self.__raise_exception_expected_choice([v for v in enum_], value)

    def __check_list_belonging(self, value, list_):
        """
        Check if a value belong to a list
        """
        if value not in list_:
            self.__raise_exception_expected_choice(list_, value)

    def __check_range_belonging(self, value, range_min, range_max):
        """
        Check if a value belong to a range
        """
        if not range_min <= value <= range_max:
            self.__raise_exception_expected_range(range_min, range_max, value)

    def __check_dict_belonging(self, value, dict_):
        """
        Check if a value belong to a dictionary
        """
        if value not in dict_.keys():
            self.__raise_exception_expected_choice(dict_.keys(), value)

    def __check_type(self, value, type_):
        if type(value) is not type_:
            self.__raise_exception_expected_type(type_.__name__, value)

    def __check_instance(self, value, type_):
        if not isinstance(value, type_):
            self.__raise_exception_expected_type(type_.__name__, value)

    def __check_list_type(self, values_list, type_):
        for value in values_list:
            self.__check_type(value, type_)

    def __map_list(self, list_, type_):
        """
        Try to map a list to another type (Very useful for list like joints
        which are acquired as string)
        """
        try:
            map_list = list(map(type_, list_))
            return map_list
        except ValueError:
            self.__raise_exception_expected_type(type_.__name__, list_)

    def __transform_to_type(self, value, type_):
        """
        Try to change value type to another
        """
        try:
            value = type_(value)
            return value
        except ValueError:
            self.__raise_exception_expected_type(type_.__name__, value)

    # Error Handlers
    def __raise_exception_expected_choice(self, expected_choice, given):
        raise TcpCommandException("Expected one of the following: {}.\nGiven: {}".format(expected_choice, given))

    def __raise_exception_expected_type(self, expected_type, given):
        raise TcpCommandException("Expected type: {}.\nGiven: {}".format(expected_type, given))

    def __raise_exception_expected_range(self, range_min, range_max, given):
        raise TcpCommandException("Expected the following condition: {} <= value <= {}\nGiven: {}".format(
            range_min, range_max, given))

    def __raise_exception(self, message):
        raise TcpCommandException("Exception message : {}".format(message))

    # -- Useful functions
    def __args_pose_to_list(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, PoseObject):
                return arg.to_list()
            else:
                pose_list = arg
        else:
            pose_list = args

        pose_list_float = self.__map_list(pose_list, float)
        if len(pose_list_float) != 6:
            self.__raise_exception("A pose should contain 6 elements (x, y, z, roll, pitch, yaw)")
        return pose_list_float

    def __args_joints_to_list(self, *args):
        """
        Convert args into a list
        Either if args = (1.1,5.6,-6.7) or args = ([1.1,5.6,-6.7],) , the
        function will return (1.1,5.6,-6.7)

        :param args: Union[list, tuple]
        :return: list of float
        """
        if len(args) == 1:
            args = args[0]

        joints = self.__map_list(args, float)
        if len(joints) != 6:
            self.__raise_exception("The robot has 6 joints")

        return joints

    def __differentiate_robot_position(self, robot_position):
        if isinstance(robot_position, PoseObject):
            return 'POSE'
        elif isinstance(robot_position, JointsPosition):
            return 'JOINTS'
        else:
            self.__raise_exception_expected_type('PoseObject or JointsPosition', type(robot_position).__name__)

    # --- Public functions --- #

    # - Main purpose

    def __handshake(self):
        try:
            server_info = self.__send_n_receive(Command.HANDSHAKE, __version__)
        except NiryoRobotException as exception:
            if 'Unknown command' in str(exception):
                self.__logger.info(
                    "This PyNiryo version is meant to be used on a more recent version of the Robot's system. "
                    "To fully benefit from the server features it's advised to upgrade your Robot System.")
                return
            else:
                raise exception from None
        if 'message' in server_info:
            self.__logger.info(server_info['message'])
            self.__logger.info('To disable the MOTD, use verbose=False')

    def calibrate(self, calibrate_mode):
        """
        Calibrate (manually or automatically) motors. Automatic calibration will do nothing
        if motors are already calibrated

        :param calibrate_mode: Auto or Manual
        :type calibrate_mode: CalibrateMode
        :rtype: None
        """
        self.__check_enum_belonging(calibrate_mode, CalibrateMode)
        self.__send_n_receive(Command.CALIBRATE, calibrate_mode)

    def calibrate_auto(self):
        """
        Start a automatic motors calibration if motors are not calibrated yet

        :rtype: None
        """
        self.calibrate(CalibrateMode.AUTO)

    def need_calibration(self):
        """
        Return a bool indicating whereas the robot motors need to be calibrate

        :rtype: bool
        """
        hardware_status = self.get_hardware_status()
        return hardware_status.calibration_needed

    @property
    def learning_mode(self):
        """
        Property
        Get learning mode state

        Example: ::

            if robot.learning_mode:
                print("Torque off")
            else:
                print("Torque on")

        :return: ``True`` if learning mode is on
        :rtype: bool
        """
        return self.get_learning_mode()

    def get_learning_mode(self):
        """
        Get learning mode state

        :return: ``True`` if learning mode is on
        :rtype: bool
        """
        return eval(self.__send_n_receive(Command.GET_LEARNING_MODE))

    @learning_mode.setter
    def learning_mode(self, value):
        self.set_learning_mode(value)

    def set_learning_mode(self, enabled):
        """
        Set learning mode if param is ``True``, else turn it off

        :param enabled: ``True`` or ``False``
        :type enabled: bool
        :rtype: None
        """
        self.__check_type(enabled, bool)
        self.__send_n_receive(Command.SET_LEARNING_MODE, enabled)

    def set_arm_max_velocity(self, percentage_speed):
        """
        Limit arm max velocity to a percentage of its maximum velocity

        :param percentage_speed: Should be between 1 & 100
        :type percentage_speed: int
        :rtype: None
        """
        self.__check_range_belonging(percentage_speed, 1, 100)
        self.__send_n_receive(Command.SET_ARM_MAX_VELOCITY, percentage_speed)

    @contextmanager
    def jog_control(self):
        """
        Context manager to enable jog control mode during a block of code

        Example: ::

            with robot.jog_control():
                robot.jog(JointsPosition(0.1, 0.0, 0.0, 0.0, 0.0, 0.0))
        """
        self.set_jog_control(True)
        try:
            yield
        finally:
            self.set_jog_control(False)

    def set_jog_control(self, enabled):
        """
        Set jog control mode if param is True, else turn it off

        :param enabled: ``True`` or ``False``
        :type enabled: bool
        :rtype: None
        """
        self.__check_type(enabled, bool)
        self.__send_n_receive(Command.SET_JOG_CONTROL, enabled)

    @staticmethod
    def wait(duration):
        """
        Wait for a certain time

        :param duration: duration in seconds
        :type duration: float
        :rtype: None
        """
        time.sleep(duration)

    @property
    def collision_detected(self):
        """
        True if a collision has been detected during a previous movement

        :type: bool
        """
        return eval(self.__send_n_receive(Command.GET_COLLISION_DETECTED))

    def clear_collision_detected(self):
        """
        Reset the internal flag ``collision_detected``
        """
        return self.__send_n_receive(Command.CLEAR_COLLISION_DETECTED)

    # - Joints/Pose

    @property
    def joints(self):
        """
        Robot's current joints position

        :type: JointsPosition
        """
        return self.get_joints()

    def get_joints(self):
        """
        Get joints value in radians

        :return: Robot's current joints position
        :rtype: JointsPosition
        """
        return JointsPosition(*self.__send_n_receive(Command.GET_JOINTS))

    @property
    def pose(self):
        """
        Get end effector link pose.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        :type: PoseObject
        """
        return self.get_pose()

    @property
    def pose_v2(self):
        """
        Get end effector link pose.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        :type: PoseObject
        """
        return self.get_pose_v2()

    def get_pose(self):
        """
        Get end effector link pose.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        :rtype: PoseObject
        """
        data = self.__send_n_receive(Command.GET_POSE)
        pose_array = self.__map_list(data, float)
        pose_object = PoseObject(*pose_array, metadata=PoseMetadata.v1())
        return pose_object

    def get_pose_quat(self):
        """
        Get end effector link pose in Quaternion coordinates

        :return: Position and quaternion coordinates concatenated in a list : [x, y, z, qx, qy, qz, qw]
        :rtype: list[float]
        """
        data = self.__send_n_receive(Command.GET_POSE_QUAT)
        pose_array = self.__map_list(data, float)
        return pose_array

    def get_pose_v2(self):
        """
        Get end effector link pose.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        :rtype: PoseObject
        """
        data = self.__send_n_receive(Command.GET_POSE_V2)
        pose_object = PoseObject.from_dict(data)
        return pose_object

    @joints.setter
    def joints(self, *args):
        if len(args) == 1 and isinstance(args, JointsPosition):
            joints_position = args[0]
        else:
            joints = self.__args_joints_to_list(*args)
            joints_position = JointsPosition(*joints)
        self.move(joints_position)

    @deprecated(f'{get_deprecation_msg("move_joints", "move")}')
    def move_joints(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`move` with a :class:`JointsPosition` object.

        Move robot joints. Joints are expressed in radians.

        All lines of the next example realize the same operation: ::

            robot.joints = [0.2, 0.1, 0.3, 0.0, 0.5, 0.0]
            robot.move_joints([0.2, 0.1, 0.3, 0.0, 0.5, 0.0])
            robot.move_joints(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)

        :param args: either 6 args (1 for each joints) or a list of 6 joints
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("move_joints", "move")}', DeprecationWarning, stacklevel=2)

        joints = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.MOVE_JOINTS, *joints)

    @pose.setter
    @deprecated(f'{get_deprecation_msg("pose", "pose_v2")}')
    def pose(self, *args):
        warnings.warn(f'{get_deprecation_msg("pose", "pose_v2")}', DeprecationWarning, stacklevel=2)
        if len(args) == 1 and isinstance(args[0], PoseObject):
            pose = args[0]
        elif len(args) == 1:
            pose = PoseObject(*args[0], metadata=PoseMetadata.v1())
        else:
            pose = PoseObject(*args, metadata=PoseMetadata.v1())
        self.move(pose)

    @pose_v2.setter
    def pose_v2(self, pose):
        self.move(pose)

    @deprecated(f'{get_deprecation_msg("move_pose", "move")}')
    def move_pose(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`move` with a :class:`PoseObject` object.

        Move robot end effector pose to a (x, y, z, roll, pitch, yaw, frame_name) pose
        in a particular frame (frame_name) if defined.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        All lines of the next example realize the same operation: ::

            robot.pose = [0.2, 0.1, 0.3, 0.0, 0.5, 0.0]
            robot.move_pose([0.2, 0.1, 0.3, 0.0, 0.5, 0.0])
            robot.move_pose(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)
            robot.move_pose(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)
            robot.move_pose(PoseObject(0.2, 0.1, 0.3, 0.0, 0.5, 0.0))
            robot.move_pose([0.2, 0.1, 0.3, 0.0, 0.5, 0.0], "frame")
            robot.move_pose(PoseObject(0.2, 0.1, 0.3, 0.0, 0.5, 0.0), "frame")

        :param args: either 7 args (1 for each coordinates and 1 for the name of the frame) or a list of 6 coordinates or a `:class:`PoseObject``
         and 1 for the frame name
        :type args: Union[tuple[float], list[float], PoseObject, [tuple[float], str], [list[float], str], [PoseObject, str]]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("move_pose", "move")}', DeprecationWarning, stacklevel=2)
        if len(args) in [2, 7]:
            pose_list = list(self.__args_pose_to_list(*args[:-1])) + [args[-1]]
        else:
            pose_list = list(self.__args_pose_to_list(*args)) + ['']
        self.__send_n_receive(Command.MOVE_POSE, *pose_list)

    @deprecated(f'{get_deprecation_msg("move_linear_pose", "move")}')
    def move_linear_pose(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`move` with a :class:`PoseObject` object and `move_cmd=Command.MOVE_LINEAR_POSE`

        Move robot end effector pose to a (x, y, z, roll, pitch, yaw) pose with a linear trajectory,
        in a particular frame (frame_name) if defined

        :param args: either 7 args (1 for each coordinates and 1 for the name of the frame) or a list of 6 coordinates or a `:class:`PoseObject``
         and 1 for the frame name
        :type args: Union[tuple[float], list[float], PoseObject, [tuple[float], str], [list[float], str], [PoseObject, str]]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("move_linear_pose", "move")}', DeprecationWarning, stacklevel=2)

        if len(args) in [2, 7]:
            pose_list = list(self.__args_pose_to_list(*args[:-1])) + [args[-1]]
        else:
            pose_list = list(self.__args_pose_to_list(*args)) + ['']
        self.__send_n_receive(Command.MOVE_LINEAR_POSE, *pose_list)

    def move(self, robot_position, linear=False):
        """
        Move the robot to the given position. The position can be expressed in joints or in pose coordinates.
        Distances are expressed in meters, and angles are expressed in radians.
        If a move pose is performed, move_cmd can be specified to move the robot according to the command

        Examples ::

            robot.move(PoseObject(0.2, 0.1, 0.3, 0.0, 0.5, 0.0, metadata=PoseMetadata.v2(frame="frame")))
            robot.move(PoseObject(0.2, 0.1, 0.3, 0.0, 0.5, 0.0), linear=True)
            robot.move(JointsPosition(0.2, 0.1, 0.3, 0.0, 0.5, 0.0))

        :param robot_position: either a joints position or a pose
        :type robot_position: Union[PoseObject, JointsPosition]
        :param linear: do a linear move (works only with a PoseObject)
        :type linear: bool
        :rtype: None
        """
        robot_position_dict = robot_position.to_dict()
        robot_position_dict['obj_type'] = self.__differentiate_robot_position(robot_position)
        self.__send_n_receive(Command.MOVE, robot_position_dict, linear)

    def shift_pose(self, axis, shift_value, linear=False):
        """
        Shift robot end effector pose along one axis

        :param axis: Axis along which the robot is shifted
        :type axis: RobotAxis
        :param shift_value: In meter for X/Y/Z and radians for roll/pitch/yaw
        :type shift_value: float
        :param linear: Whether the movement has to be linear or not
        :type linear: bool
        :rtype: None
        """
        self.__check_enum_belonging(axis, RobotAxis)
        shift_value = self.__transform_to_type(shift_value, float)
        self.__send_n_receive(Command.SHIFT_POSE, axis, shift_value, linear)

    @deprecated(f'{get_deprecation_msg("shift_linear_pose", "shift_pose")}')
    def shift_linear_pose(self, axis, shift_value):
        """
        .. deprecated:: 1.2.0
           You should use :func:`shift_pose` with linear=True.

        Shift robot end effector pose along one axis, with a linear trajectory

        :param axis: Axis along which the robot is shifted
        :type axis: RobotAxis
        :param shift_value: In meter for X/Y/Z and radians for roll/pitch/yaw
        :type shift_value: float
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("shift_linear_pose", "shift_pose")}', DeprecationWarning, stacklevel=2)
        return self.shift_pose(axis, shift_value, linear=True)

    @deprecated(f'{get_deprecation_msg("jog_joints", "jog")}')
    def jog_joints(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`jog` with a :class:`JointsPosition` object.

        Jog robot joints'.
        Jog corresponds to a shift without motion planning.
        Values are expressed in radians.

        :param args: either 6 args (1 for each joints) or a list of 6 joints offset
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("jog_joints", "jog")}', DeprecationWarning, stacklevel=2)
        joints_offset = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.JOG_JOINTS, *joints_offset)

    @deprecated(f'{get_deprecation_msg("jog_pose", "jog")}')
    def jog_pose(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`jog` with a :class:`PoseObject` object.

        Jog robot end effector pose
        Jog corresponds to a shift without motion planning
        Arguments are [dx, dy, dz, d_roll, d_pitch, d_yaw]
        dx, dy & dz are expressed in meters / d_roll, d_pitch & d_yaw are expressed in radians

        :param args: either 6 args (1 for each coordinates) or a list of 6 offset
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("jog_pose", "jog")}', DeprecationWarning, stacklevel=2)
        pose_offset = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.JOG_POSE, *pose_offset)

    def jog(self, robot_position):
        robot_position_dict = robot_position.to_dict()
        robot_position_dict['obj_type'] = self.__differentiate_robot_position(robot_position)
        self.__send_n_receive(Command.JOG, robot_position_dict)

    def move_to_home_pose(self):
        """
        Move to a position where the forearm lays on shoulder

        :rtype: None
        """
        self.move(JointsPosition(0.0, 0.3, -1.3, 0.0, 0.0, 0.0))

    def go_to_sleep(self):
        """
        Go to home pose and activate learning mode

        :rtype: None
        """
        self.move_to_home_pose()
        self.set_learning_mode(True)

    def forward_kinematics(self, *args):
        """
        Compute forward kinematics of a given joints configuration and give the
        associated spatial pose

        :param args: either 6 args (1 for each joints) or a list of 6 joints or a JointsPosition instance
        :type args: Union[list[float], tuple[float], JointsPosition]
        :rtype: PoseObject
        """
        if len(args) == 1 and isinstance(args[0], JointsPosition):
            joints = args[0]
        elif len(args) == 1:
            joints = JointsPosition(*args[0])
        else:
            joints = JointsPosition(*args)

        data = self.__send_n_receive(Command.FORWARD_KINEMATICS, joints.to_dict())

        pose = PoseObject.from_dict(data)
        return pose

    def inverse_kinematics(self, *args):
        """
        Compute inverse kinematics

        :param args: either 6 args (1 for each coordinate) or a list of 6 coordinates or a `:class:`PoseObject``
        :type args: Union[tuple[float], list[float], PoseObject]

        :return: List of joints value
        :rtype: list[float]
        """
        if len(args) == 1 and isinstance(args[0], PoseObject):
            pose = args[0]
        elif len(args) == 1:
            pose = PoseObject(*args[0], metadata=PoseMetadata.v1())
        else:
            pose = PoseObject(*args, metadata=PoseMetadata.v1())

        data = self.__send_n_receive(Command.INVERSE_KINEMATICS, pose.to_dict())
        joints_position = JointsPosition.from_dict(data)
        return joints_position

    def forward_kinematics_v2(self, joints_position):
        """
        Compute forward kinematics of a given joints configuration and give the
        associated spatial pose

        :param joints_position: Joints configuration
        :type joints_position: JointsPosition
        :rtype: PoseObject
        """
        data = self.__send_n_receive(Command.FORWARD_KINEMATICS_V2, joints_position.to_dict())
        pose = PoseObject.from_dict(data)
        return pose

    def inverse_kinematics_v2(self, pose):
        """
        Compute inverse kinematics

        :param pose: Robot pose
        :type pose: PoseObject

        :return: the joint position
        :rtype: JointsPosition
        """
        data = self.__send_n_receive(Command.INVERSE_KINEMATICS_V2, pose.to_dict())
        joints_position = JointsPosition.from_dict(data)
        return joints_position

    # - Saved Pose

    def get_pose_saved(self, pose_name):
        """
        Get pose saved in from Ned's memory

        :param pose_name: Pose name in robot's memory
        :type pose_name: str
        :return: Pose associated to pose_name
        :rtype: PoseObject
        """
        self.__check_type(pose_name, str)

        pose_list = self.__send_n_receive(Command.GET_POSE_SAVED, pose_name)
        return PoseObject.from_dict(pose_list)

    def save_pose(self, pose_name, *args):
        """
        Save pose in robot's memory

        :type pose_name: str
        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[list[float], tuple[float], PoseObject]
        :rtype: None
        """
        self.__check_type(pose_name, str)
        if len(args) == 1 and isinstance(args[0], PoseObject):
            pose = args[0]
        else:
            pose = PoseObject(*self.__args_pose_to_list(*args), metadata=PoseMetadata.v1())

        self.__send_n_receive(Command.SAVE_POSE, pose_name, pose.to_dict())

    def delete_pose(self, pose_name):
        """
        Delete pose from robot's memory

        :type pose_name: str
        :rtype: None
        """
        self.__check_type(pose_name, str)
        self.__send_n_receive(Command.DELETE_POSE, pose_name)

    def get_saved_pose_list(self):
        """
        Get list of poses' name saved in robot memory

        :rtype: list[str]
        """
        return self.__send_n_receive(Command.GET_SAVED_POSE_LIST)

    # - Pick/Place

    @deprecated(f'{get_deprecation_msg("pick_from_pose", "pick")}')
    def pick_from_pose(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`pick` with a :class:`PoseObject` object.

        Execute a picking from a pose.

        A picking is described as : \n
        | * going over the object
        | * going down until height = z
        | * grasping with tool
        | * going back over the object

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[list[float], tuple[float], PoseObject]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("pick_from_pose", "pick")}', DeprecationWarning, stacklevel=2)
        pose = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.PICK_FROM_POSE, *pose)

    @deprecated(f'{get_deprecation_msg("place_from_pose", "place")}')
    def place_from_pose(self, *args):
        """
        .. deprecated:: 1.2.0
           You should use :func:`place` with a :class:`PoseObject` object.

        Execute a placing from a position.

        A placing is described as : \n
        | * going over the place
        | * going down until height = z
        | * releasing the object with tool
        | * going back over the place

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[list[float], tuple[float], PoseObject]
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("place_from_pose", "place")}', DeprecationWarning, stacklevel=2)
        pose = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.PLACE_FROM_POSE, *pose)

    def pick(self, pick_position):
        """
        Execute a picking from a position.

        A picking is described as : \n
        | * going over the object
        | * going down until height = z
        | * grasping with tool
        | * going back over the object

        :param pick_position: a pick position, can be either a Pose or a JointsPosition object
        :type pick_position: Union[JointsPosition, PoseObject]
        :rtype: None
        """
        obj_dict = pick_position.to_dict()
        obj_dict['obj_type'] = self.__differentiate_robot_position(pick_position)
        self.__send_n_receive(Command.PICK, obj_dict)

    def place(self, place_position):
        """
        Execute a placing from a position.

        A placing is described as : \n
        | * going over the place
        | * going down until height = z
        | * releasing the object with tool
        | * going back over the place

        :param place_position: a place position, can be either a Pose or a JointsPosition object
        :type place_position: Union[JointsPosition, PoseObject]
        :rtype: None
        """
        obj_dict = place_position.to_dict()
        obj_dict['obj_type'] = self.__differentiate_robot_position(place_position)
        self.__send_n_receive(Command.PLACE, obj_dict)

    def pick_and_place(self, pick_pose, place_pos, dist_smoothing=0.0):
        """
        Execute a pick then a place

        :param pick_pose: Pick Pose : [x, y, z, roll, pitch, yaw] or PoseObject
        :type pick_pose: Union[list[float], PoseObject]
        :param place_pos: Place Pose : [x, y, z, roll, pitch, yaw] or PoseObject
        :type place_pos: Union[list[float], PoseObject]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        if not isinstance(pick_pose, PoseObject) and not isinstance(pick_pose, JointsPosition):
            pick_pose_list = self.__args_pose_to_list(pick_pose)
            pick_pose = PoseObject(*pick_pose_list, metadata=PoseMetadata.v1())
        if not isinstance(place_pos, PoseObject) and not isinstance(place_pos, JointsPosition):
            place_pos_list = self.__args_pose_to_list(place_pos)
            place_pos = PoseObject(*place_pos_list, metadata=PoseMetadata.v1())

        pick_pose_dict = pick_pose.to_dict()
        pick_pose_dict['obj_type'] = self.__differentiate_robot_position(pick_pose)

        place_pose_dict = place_pos.to_dict()
        place_pose_dict['obj_type'] = self.__differentiate_robot_position(place_pos)

        self.__send_n_receive(Command.PICK_AND_PLACE, pick_pose_dict, place_pose_dict, dist_smoothing)

    # - Trajectories
    def get_trajectory_saved(self, trajectory_name):
        """
        Get trajectory saved in Ned's memory

        :type trajectory_name: str
        :return: Trajectory
        :rtype: list[Joints]
        """
        self.__check_type(trajectory_name, str)
        return [
            JointsPosition.from_dict(d) for d in self.__send_n_receive(Command.GET_TRAJECTORY_SAVED, trajectory_name)
        ]

    def get_saved_trajectory_list(self):
        """
        Get list of trajectories' name saved in robot memory

        :rtype: list[str]
        """
        return self.__send_n_receive(Command.GET_SAVED_TRAJECTORY_LIST)

    def execute_registered_trajectory(self, trajectory_name):
        """
        Execute trajectory from Ned's memory

        :type trajectory_name: str
        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        self.__send_n_receive(Command.EXECUTE_REGISTERED_TRAJECTORY, trajectory_name)

    def execute_trajectory(self, robot_positions, dist_smoothing=0.0):
        """
        Execute trajectory from list of poses and / or joints

        :param robot_positions: List of poses or joints
        :type robot_positions: list[Union[JointsPosition, PoseObject]]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        dict_positions = []
        for robot_position in robot_positions:
            position_dict = robot_position.to_dict()
            position_dict['obj_type'] = self.__differentiate_robot_position(robot_position)
            dict_positions.append(position_dict)
        self.__send_n_receive(Command.EXECUTE_TRAJECTORY, dict_positions, dist_smoothing)

    @deprecated(f'{get_deprecation_msg("execute_trajectory_from_poses", "execute_trajectory")}')
    def execute_trajectory_from_poses(self, list_poses, dist_smoothing=0.0):
        """
        .. deprecated:: 1.2.0
           You should use :func:`execute_trajectory` with :class:`PoseObject` objects.

        Execute trajectory from list of poses

        :param list_poses: List of [x,y,z,qx,qy,qz,qw] or list of [x,y,z,roll,pitch,yaw]
        :type list_poses: list[list[float]]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        [PoseObject(*pose) for pose in list_poses]
        warnings.warn(f'{get_deprecation_msg("execute_trajectory_from_poses", "execute_trajectory")}',
                      DeprecationWarning,
                      stacklevel=2)
        for i, pose in enumerate(list_poses):
            if len(pose) != 7 and len(pose) != 6:
                self.__raise_exception(
                    "7 parameters expected in a pose [x,y,z,qx,qy,qz,qw], or 6 in a pose [x,y,z,roll,pitch,yaw], "
                    "{} parameters given".format(len(pose)))
            list_poses[i] = self.__map_list(pose, float)

        self.__send_n_receive(Command.EXECUTE_TRAJECTORY_FROM_POSES, list_poses, dist_smoothing)

    @deprecated(f'{get_deprecation_msg("execute_trajectory_from_poses_and_joints", "execute_trajectory")}')
    def execute_trajectory_from_poses_and_joints(self, list_pose_joints, list_type=None, dist_smoothing=0.0):
        """
        .. deprecated:: 1.2.0
           You should use :func:`execute_trajectory` with :class:`PoseObject` and :class:`JointsPosition` objects.

        Execute trajectory from list of poses and joints

        Example: ::

            robot.execute_trajectory_from_poses_and_joints(
               list_pose_joints = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.25, 0.0, 0.0, 0.0, 0.0, 0.0]],
               list_type = ['joint', 'pose'],
               dist_smoothing = 0.01
            )

        :param list_pose_joints: List of [x,y,z,qx,qy,qz,qw] or list of [x,y,z,roll,pitch,yaw]
                                        or a list of [j1,j2,j3,j4,j5,j6]
        :type list_pose_joints: list[list[float]]
        :param list_type: List of string 'pose' or 'joint', or ['pose'] (if poses only) or ['joint'] (if joints only).
                        If None, it is assumed there are only poses in the list.
        :type list_type: list[string]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        warnings.warn(f'{get_deprecation_msg("execute_trajectory_from_poses_and_joints", "execute_trajectory")}',
                      DeprecationWarning,
                      stacklevel=2)
        if list_type is None:
            list_type = ['pose']
        for i, pose_or_joint in enumerate(list_pose_joints):
            if not (6 <= len(pose_or_joint) <= 7):
                self.__raise_exception(
                    "7 parameters expected in a pose [x,y,z,qx,qy,qz,qw], or 6 in a pose [x,y,z,roll,pitch,yaw], "
                    "or 6 in a joint [j1,j2,j3,j4,j5,j6]"
                    "{} parameters given".format(len(pose_or_joint)))
            list_pose_joints[i] = self.__map_list(pose_or_joint, float)
        self.__send_n_receive(Command.EXECUTE_TRAJECTORY_FROM_POSES_AND_JOINTS,
                              list_pose_joints,
                              list_type,
                              dist_smoothing)

    def save_trajectory(self, trajectory, trajectory_name, trajectory_description):
        """
        Save trajectory in robot memory

        :param trajectory: list of Joints [j1, j2, j3, j4, j5, j6] as waypoints to create the trajectory
        :type trajectory: list[list[float] | JointsPosition | PoseObject]
        :param trajectory_name: Name you want to give to the trajectory
        :type trajectory_name: str
        :param trajectory_description: Description you want to give to the trajectory

        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        self.__check_type(trajectory_description, str)
        self.__check_type(trajectory, list)
        dict_joints = []
        for joints in trajectory:
            if isinstance(joints, JointsPosition):
                dict_joints.append(joints.to_dict())
            else:
                dict_joints.append(JointsPosition(*joints).to_dict())

        self.__send_n_receive(Command.SAVE_TRAJECTORY, dict_joints, trajectory_name, trajectory_description)

    def save_last_learned_trajectory(self, name, description):
        """
        Save last user executed trajectory

        :type name: str
        :type description: str
        :rtype: None
        """
        self.__check_type(name, str)
        self.__check_type(description, str)
        self.__send_n_receive(Command.SAVE_LAST_LEARNED_TRAJECTORY, name, description)

    def update_trajectory_infos(self, name, new_name, new_description):
        """"
        Update trajectory infos

        :param name: current name of the trajectory you want to update infos
        :type name: str
        :param new_name: new name you want to give the trajectory
        :type new_name: str
        :param new_description: new description you want to give the trajectory
        :type new_description: str
        :rtype: None
        """
        self.__check_type(name, str)
        self.__check_type(new_name, str)
        self.__check_type(new_description, str)
        self.__send_n_receive(Command.UPDATE_TRAJECTORY_INFOS, name, new_name, new_description)

    def delete_trajectory(self, trajectory_name):
        """
        Delete trajectory from robot's memory

        :type trajectory_name: str
        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        self.__send_n_receive(Command.DELETE_TRAJECTORY, trajectory_name)

    def clean_trajectory_memory(self):
        """
        Delete trajectory from robot's memory

        :rtype: None
        """
        self.__send_n_receive(Command.CLEAN_TRAJECTORY_MEMORY)

    # -- Tools

    @property
    def tool(self):
        return self.get_current_tool_id()

    def get_current_tool_id(self):
        """
        Get equipped tool Id

        :rtype: ToolID
        """
        tool_id = self.__send_n_receive(Command.GET_CURRENT_TOOL_ID)
        return ToolID[tool_id]

    def update_tool(self):
        """
        Update equipped tool

        :rtype: None
        """
        self.__send_n_receive(Command.UPDATE_TOOL)

    def grasp_with_tool(self):
        """
        Grasp with tool
        | This action correspond to
        | - Close gripper for Grippers
        | - Pull Air for Vacuum pump
        | - Activate for Electromagnet

        :rtype: None
        """
        self.__send_n_receive(Command.GRASP_WITH_TOOL)

    def release_with_tool(self):
        """
        Release with tool
        | This action correspond to
        | - Open gripper for Grippers
        | - Push Air for Vacuum pump
        | - Deactivate for Electromagnet

        :rtype: None
        """
        self.__send_n_receive(Command.RELEASE_WITH_TOOL)

    # - Gripper
    def open_gripper(self, speed=500, max_torque_percentage=100, hold_torque_percentage=30):
        """
        Open gripper

        :param speed: Between 100 & 1000 (only for Niryo One and Ned1)
        :type speed: int
        :param max_torque_percentage: Closing torque percentage (only for Ned2)
        :type max_torque_percentage: int
        :param hold_torque_percentage: Hold torque percentage after closing (only for Ned2)
        :type hold_torque_percentage: int
        :rtype: None
        """
        speed = self.__transform_to_type(speed, int)
        max_torque_percentage = self.__transform_to_type(max_torque_percentage, int)
        hold_torque_percentage = self.__transform_to_type(hold_torque_percentage, int)

        self.__send_n_receive(Command.OPEN_GRIPPER, speed, max_torque_percentage, hold_torque_percentage)

    def close_gripper(self, speed=500, max_torque_percentage=100, hold_torque_percentage=20):
        """
        Close gripper

        :param speed: Between 100 & 1000 (only for Niryo One and Ned1)
        :type speed: int
        :param max_torque_percentage: Opening torque percentage (only for Ned2)
        :type max_torque_percentage: int
        :param hold_torque_percentage: Hold torque percentage after opening (only for Ned2)
        :type hold_torque_percentage: int
        :rtype: None
        """
        speed = self.__transform_to_type(speed, int)
        max_torque_percentage = self.__transform_to_type(max_torque_percentage, int)
        hold_torque_percentage = self.__transform_to_type(hold_torque_percentage, int)

        self.__send_n_receive(Command.CLOSE_GRIPPER, speed, max_torque_percentage, hold_torque_percentage)

    # - Vacuum
    def pull_air_vacuum_pump(self):
        """
        Pull air of vacuum pump

        :rtype: None
        """
        self.__send_n_receive(Command.PULL_AIR_VACUUM_PUMP)

    def push_air_vacuum_pump(self):
        """
        Push air of vacuum pump

        :rtype: None
        """
        self.__send_n_receive(Command.PUSH_AIR_VACUUM_PUMP)

    # - Electromagnet
    def setup_electromagnet(self, pin_id):
        """
        Setup electromagnet on pin

        :param pin_id:
        :type pin_id: PinID or str
        :rtype: None
        """
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id
        self.__send_n_receive(Command.SETUP_ELECTROMAGNET, pin_id_str)

    def activate_electromagnet(self, pin_id):
        """
        Activate electromagnet associated to electromagnet_id on pin_id

        :param pin_id:
        :type pin_id: PinID or str
        :rtype: None
        """
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id
        self.__send_n_receive(Command.ACTIVATE_ELECTROMAGNET, pin_id_str)

    def deactivate_electromagnet(self, pin_id):
        """
        Deactivate electromagnet associated to electromagnet_id on pin_id

        :param pin_id:
        :type pin_id: PinID or str
        :rtype: None
        """
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id
        self.__send_n_receive(Command.DEACTIVATE_ELECTROMAGNET, pin_id_str)

    def enable_tcp(self, enable=True):
        """
        Enables or disables the TCP function (Tool Center Point).
        If activation is requested, the last recorded TCP value will be applied.
        The default value depends on the gripper equipped.
        If deactivation is requested, the TCP will be coincident with the tool_link.

        :param enable: True to enable, False otherwise.
        :type enable: Bool
        :rtype: None
        """
        self.__check_instance(enable, bool)
        self.__send_n_receive(Command.ENABLE_TCP, enable)

    def set_tcp(self, *args):
        """
        Activates the TCP function (Tool Center Point)
        and defines the transformation between the tool_link frame and the TCP frame.

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[list[float], tuple[float], PoseObject]
        :rtype: None
        """
        tcp_transform = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.SET_TCP, *tcp_transform)

    def reset_tcp(self):
        """
        Reset the TCP (Tool Center Point) transformation.
        The TCP will be reset according to the tool equipped.

        :rtype: None
        """
        self.__send_n_receive(Command.RESET_TCP)

    def tool_reboot(self):
        """
        Reboot the motor of the tool equparam_list = [workspace_name]

        Example: ::

            for pose in (pose_origin, pose_2, pose_3, pose_4):
                pose_list = self.__args_pose_to_list(pose)
                param_list.append(pose_list)ipped. Useful when an Overload error occurs. (cf HardwareStatus)

        :rtype: None
        """
        self.__send_n_receive(Command.TOOL_REBOOT)

    def get_tcp(self):
        return self.__send_n_receive(Command.GET_TCP)

    # - Hardware

    def set_pin_mode(self, pin_id, pin_mode):
        """
        Set pin number pin_id to mode pin_mode

        :param pin_id:
        :type pin_id: PinID or str
        :param pin_mode:
        :type pin_mode: PinMode
        :rtype: None
        """
        self.__check_enum_belonging(pin_mode, PinMode)
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id

        self.__send_n_receive(Command.SET_PIN_MODE, pin_id_str, pin_mode)

    @property
    def digital_io_state(self):
        return self.get_digital_io_state()

    def get_digital_io_state(self):
        """
        Get Digital IO state : Names, modes, states.

        Example: ::

            digital_io_state = robot.digital_io_state
            digital_io_state = robot.get_digital_io_state()

        :return: List of DigitalPinObject instance
        :rtype: list[DigitalPinObject]
        """
        data = self.__send_n_receive(Command.GET_DIGITAL_IO_STATE)
        digital_pin_array = []
        for pin_info in data:
            name, mode, value = pin_info
            digital_pin_array.append(DigitalPinObject(PinID(name), name, PinMode(mode), PinState(bool(value))))
        return digital_pin_array

    def digital_write(self, pin_id, digital_state):
        """
        Set pin_id state to digital_state

        :param pin_id:
        :type pin_id: PinID or str
        :param digital_state:
        :type digital_state: PinState
        :rtype: None
        """
        self.__check_enum_belonging(digital_state, PinState)
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id

        self.__send_n_receive(Command.DIGITAL_WRITE, pin_id_str, digital_state)

    def digital_read(self, pin_id):
        """
        Read pin number pin_id and return its state

        :param pin_id:
        :type pin_id: PinID or str
        :rtype: PinState
        """
        self.__check_instance(pin_id, (PinID, str))
        pin_id_str = pin_id.value if isinstance(pin_id, PinID) else pin_id

        state_id = self.__send_n_receive(Command.DIGITAL_READ, pin_id_str)
        return PinState[state_id]

    @property
    def analog_io_state(self):
        return self.get_analog_io_state()

    def get_analog_io_state(self):
        """
        Get Analog IO state : Names, modes, states

        Example: ::

            analog_io_state = robot.analog_io_state
            analog_io_state = robot.get_analog_io_state()


        :return: List of AnalogPinObject instance
        :rtype: list[AnalogPinObject]
        """
        data = self.__send_n_receive(Command.GET_ANALOG_IO_STATE)

        analog_pin_array = []
        for pin_info in data:
            name, mode, value = pin_info
            analog_pin_array.append(AnalogPinObject(PinID(name), name, PinMode(mode), value))
        return analog_pin_array

    def analog_write(self, pin_id, value):
        """
        Set and analog pin_id state to a value

        :param pin_id:
        :type pin_id: PinID or str
        :param value: voltage between 0 and 5V
        :type value: float
        :rtype: None
        """
        self.__check_instance(pin_id, (PinID, str))
        self.__check_range_belonging(value, 0, 5)

        self.__send_n_receive(Command.ANALOG_WRITE, pin_id, value)

    def analog_read(self, pin_id):
        """
        Read the analog pin value

        :param pin_id:
        :type pin_id: PinID or str
        :rtype: float
        """
        self.__check_instance(pin_id, (PinID, str))

        return self.__send_n_receive(Command.ANALOG_READ, pin_id)

    @property
    def custom_button_state(self):
        return self.get_custom_button_state()

    def get_custom_button_state(self):
        """
        Get the Ned2's custom button state

        :return: True if pressed, False else
        :rtype: bool
        """
        return self.__send_n_receive(Command.CUSTOM_BUTTON_STATE)

    @property
    def hardware_status(self):
        return self.get_hardware_status()

    def get_hardware_status(self):
        """
        Get hardware status : Temperature, Hardware version, motors names & types ...

        :return: Infos contains in a HardwareStatusObject
        :rtype: HardwareStatusObject
        """
        data = self.__send_n_receive(Command.GET_HARDWARE_STATUS)

        rpi_temperature = float(data[0])
        hardware_version = data[1]
        connection_up = eval(data[2])
        error_message = data[3]
        calibration_needed = eval(data[4])
        calibration_in_progress = eval(data[5])

        motor_names = data[6]
        motor_types = data[7]
        temperatures = self.__map_list(data[8], float)
        voltages = self.__map_list(data[9], float)
        hardware_errors = data[10]

        hardware_status = HardwareStatusObject(rpi_temperature,
                                               hardware_version,
                                               connection_up,
                                               error_message,
                                               calibration_needed,
                                               calibration_in_progress,
                                               motor_names,
                                               motor_types,
                                               temperatures,
                                               voltages,
                                               hardware_errors)
        return hardware_status

    # - Conveyor

    def set_conveyor(self):
        """
        Activate a new conveyor and return its ID

        :return: New conveyor ID
        :rtype: ConveyorID
        """
        conveyor_id_str = self.__send_n_receive(Command.SET_CONVEYOR)
        conveyor_id = ConveyorID[conveyor_id_str]

        # If new conveyor has been found
        if conveyor_id != ConveyorID.NONE:
            return conveyor_id

        connected_conveyors_id = self.get_connected_conveyors_id()
        if not connected_conveyors_id:
            self.__logger.error("No conveyor connected !")
            return ConveyorID.NONE
        else:
            self.__logger.warning("No new conveyor detected, returning last connected conveyor")
            return connected_conveyors_id[-1]

    def unset_conveyor(self, conveyor_id):
        """
        Remove specific conveyor.

        :param conveyor_id: Basically, ConveyorID.ONE or ConveyorID.TWO
        :type conveyor_id: ConveyorID
        """
        self.__send_n_receive(Command.UNSET_CONVEYOR, conveyor_id)

    def run_conveyor(self, conveyor_id, speed=50, direction=ConveyorDirection.FORWARD):
        """
        Run conveyor at id 'conveyor_id'

        :param conveyor_id:
        :type conveyor_id: ConveyorID
        :param speed:
        :type speed: int
        :param direction:
        :type direction: ConveyorDirection
        :rtype: None
        """
        self.control_conveyor(conveyor_id, control_on=True, speed=speed, direction=direction)

    def stop_conveyor(self, conveyor_id):
        """
        Stop conveyor at id 'conveyor_id'

        :param conveyor_id:
        :type conveyor_id: ConveyorID
        :rtype: None
        """
        self.control_conveyor(conveyor_id, control_on=False, speed=50, direction=ConveyorDirection.FORWARD)

    def control_conveyor(self, conveyor_id, control_on, speed, direction):
        """
        Control conveyor at id 'conveyor_id'

        :param conveyor_id:
        :type conveyor_id: ConveyorID
        :param control_on:
        :type control_on: bool
        :param speed: New speed which is a percentage of maximum speed
        :type speed: int
        :param direction: Conveyor direction
        :type direction: ConveyorDirection
        :rtype: None
        """
        self.__check_enum_belonging(conveyor_id, ConveyorID)
        self.__check_type(control_on, bool)
        self.__transform_to_type(speed, int)
        self.__check_enum_belonging(direction, ConveyorDirection)

        self.__send_n_receive(Command.CONTROL_CONVEYOR, conveyor_id, control_on, speed, direction)

    def get_connected_conveyors_id(self):
        """

        :return: List of the connected conveyors' ID
        :rtype: list[ConveyorID]
        """
        conveyors_list_str = self.__send_n_receive(Command.GET_CONNECTED_CONVEYORS_ID)
        conveyors_list = [ConveyorID[conveyor] for conveyor in conveyors_list_str]

        return conveyors_list

    def get_conveyors_feedback(self):
        """
        Get the feedback of the conveyors
        - conveyor id
        - direction
        - connection state
        - running
        - speed

        :return: List of the conveyors' feedback
        :rtype: list[ConveyorFeedback]
        """
        conveyors_feedback = self.__send_n_receive(Command.GET_CONVEYORS_FEEDBACK)
        for i in range(len(conveyors_feedback)):
            conveyors_feedback[i]['conveyor_id'] = ConveyorID[conveyors_feedback[i]['conveyor_id']]
            conveyors_feedback[i]['direction'] = ConveyorDirection(conveyors_feedback[i]['direction'])
            conveyors_feedback[i]['connection_state'] = eval(conveyors_feedback[i]['connection_state'])

        return conveyors_feedback

    # - Vision
    def get_img_compressed(self):
        """
        Get image from video stream in a compressed format.
        Use ``uncompress_image`` from the vision package to uncompress it

        :return: string containing a JPEG compressed image
        :rtype: str
        """
        _, img = self.__send_n_receive(Command.GET_IMAGE_COMPRESSED, with_payload=True)
        return img

    def set_brightness(self, brightness_factor):
        """
        Modify video stream brightness

        :param brightness_factor: How much to adjust the brightness. 0.5 will
            give a darkened image, 1 will give the original image while
            2 will enhance the brightness by a factor of 2.
        :type brightness_factor: float
        :rtype: None
        """
        self.__transform_to_type(brightness_factor, float)
        self.__check_range_belonging(brightness_factor, 0.0, np.inf)
        self.__send_n_receive(Command.SET_IMAGE_BRIGHTNESS, brightness_factor)

    def set_contrast(self, contrast_factor):
        """
        Modify video stream contrast

        :param contrast_factor: While a factor of 1 gives original image.
            Making the factor towards 0 makes the image greyer, while factor>1 increases the contrast of the image.
        :type contrast_factor: float
        :rtype: None
        """
        self.__transform_to_type(contrast_factor, float)
        self.__check_range_belonging(contrast_factor, 0.0, np.inf)
        self.__send_n_receive(Command.SET_IMAGE_CONTRAST, contrast_factor)

    def set_saturation(self, saturation_factor):
        """
        Modify video stream saturation

        :param saturation_factor: How much to adjust the saturation. 0 will
            give a black and white image, 1 will give the original image while
            2 will enhance the saturation by a factor of 2.
        :type saturation_factor: float
        :rtype: None
        """
        self.__transform_to_type(saturation_factor, float)
        self.__check_range_belonging(saturation_factor, 0.0, np.inf)
        self.__send_n_receive(Command.SET_IMAGE_SATURATION, saturation_factor)

    def get_image_parameters(self):
        """
        Get last stream image parameters: Brightness factor, Contrast factor, Saturation factor.

        Brightness factor: How much to adjust the brightness. 0.5 will give a darkened image,
        1 will give the original image while 2 will enhance the brightness by a factor of 2.

        Contrast factor: A factor of 1 gives original image.
        Making the factor towards 0 makes the image greyer, while factor>1 increases the contrast of the image.

        Saturation factor: 0 will give a black and white image, 1 will give the original image while
        2 will enhance the saturation by a factor of 2.

        :return:  Brightness factor, Contrast factor, Saturation factor
        :rtype: float, float, float
        """
        brightness_factor, contrast_factor, saturation_factor = self.__send_n_receive(Command.GET_IMAGE_PARAMETERS)
        return brightness_factor, contrast_factor, saturation_factor

    def get_target_pose_from_rel(self, workspace_name, height_offset, x_rel, y_rel, yaw_rel):
        """
        Given a pose (x_rel, y_rel, yaw_rel) relative to a workspace, this function
        returns the robot pose in which the current tool will be able to pick an object at this pose.

        The height_offset argument (in m) defines how high the tool will hover over the workspace. If height_offset = 0,
        the tool will nearly touch the workspace.

        :param workspace_name: name of the workspace
        :type workspace_name: str
        :param height_offset: offset between the workspace and the target height
        :type height_offset: float
        :param x_rel: x relative pose (between 0 and 1)
        :type x_rel: float
        :param y_rel: y relative pose (between 0 and 1)
        :type y_rel: float
        :param yaw_rel: Angle in radians
        :type yaw_rel: float

        :return: target_pose
        :rtype: PoseObject
        """
        self.__check_type(workspace_name, str)
        self.__check_range_belonging(x_rel, 0.0, 1.0)
        self.__check_range_belonging(y_rel, 0.0, 1.0)

        height_offset, x_rel, y_rel, yaw_rel = self.__map_list([height_offset, x_rel, y_rel, yaw_rel], float)
        pose_array = self.__send_n_receive(Command.GET_TARGET_POSE_FROM_REL,
                                           workspace_name,
                                           height_offset,
                                           x_rel,
                                           y_rel,
                                           yaw_rel)
        pose_object = PoseObject(*pose_array)
        return pose_object

    def get_target_pose_from_cam(self, workspace_name, height_offset=0.0, shape=ObjectShape.ANY, color=ObjectColor.ANY):
        """
        First detects the specified object using the camera and then returns the robot pose in which the object can
        be picked with the current tool

        :param workspace_name: name of the workspace
        :type workspace_name: str
        :param height_offset: offset between the workspace and the target height
        :type height_offset: float
        :param shape: shape of the target
        :type shape: ObjectShape
        :param color: color of the target
        :type color: ObjectColor
        :return: object_found, object_pose, object_shape, object_color
        :rtype: (bool, PoseObject, ObjectShape, ObjectColor)
        """
        self.__check_type(workspace_name, str)
        height_offset = self.__transform_to_type(height_offset, float)
        self.__check_enum_belonging(shape, ObjectShape)
        self.__check_enum_belonging(color, ObjectColor)

        data_array = self.__send_n_receive(Command.GET_TARGET_POSE_FROM_CAM,
                                           workspace_name,
                                           height_offset,
                                           shape,
                                           color)
        obj_found = eval(data_array[0])
        if obj_found:
            pose_object = PoseObject(*data_array[1])
            shape_ret = data_array[2]
            color_ret = data_array[3]
        else:
            pose_object = PoseObject(0, 0, 0, 0, 0, 0)
            shape_ret = "ANY"
            color_ret = 'ANY'
        return obj_found, pose_object, ObjectShape[shape_ret], ObjectColor[color_ret]

    def __move_with_vision(self, command, workspace_name, height_offset, shape, color, **kwargs):
        self.__check_type(workspace_name, str)
        height_offset = self.__transform_to_type(height_offset, float)
        self.__check_enum_belonging(shape, ObjectShape)
        self.__check_enum_belonging(color, ObjectColor)

        data_array = self.__send_n_receive(command, workspace_name, height_offset, shape, color, **kwargs)

        obj_found = eval(data_array[0])
        if obj_found is True:
            shape_ret = data_array[1]
            color_ret = data_array[2]
        else:
            shape_ret = "ANY"
            color_ret = 'ANY'
        return obj_found, ObjectShape[shape_ret], ObjectColor[color_ret]

    def vision_pick(self,
                    workspace_name,
                    height_offset=0.0,
                    shape=ObjectShape.ANY,
                    color=ObjectColor.ANY,
                    obs_pose=None):
        """
        Picks the specified object from the workspace. This function has multiple phases: \n
        | 1. detect object using the camera
        | 2. prepare the current tool for picking
        | 3. approach the object
        | 4. move down to the correct picking pose
        | 5. actuate the current tool
        | 6. lift the object

        Example::

            robot = NiryoRobot(ip_address="x.x.x.x")
            robot.calibrate_auto()
            robot.move_pose(<observation_pose>)
            obj_found, shape_ret, color_ret = robot.vision_pick(<workspace_name>,
                                                                height_offset=0.0,
                                                                shape=ObjectShape.ANY,
                                                                color=ObjectColor.ANY)

        :param workspace_name: name of the workspace
        :type workspace_name: str
        :param height_offset: offset between the workspace and the target height
        :type height_offset: float
        :param shape: shape of the target
        :type shape: ObjectShape
        :param color: color of the target
        :type color: ObjectColor
        :param obs_pose: An optional observation pose
        :type obs_pose: PoseObject
        :return: object_found, object_shape, object_color
        :rtype: (bool, ObjectShape, ObjectColor)
        """
        return self.__move_with_vision(Command.VISION_PICK,
                                       workspace_name,
                                       height_offset,
                                       shape,
                                       color,
                                       obs_pose=obs_pose)

    def move_to_object(self, workspace_name, height_offset, shape, color):
        """
        Same as `get_target_pose_from_cam` but directly moves to this position

        :param workspace_name: name of the workspace
        :type workspace_name: str
        :param height_offset: offset between the workspace and the target height
        :type height_offset: float
        :param shape: shape of the target
        :type shape: ObjectShape
        :param color: color of the target
        :type color: ObjectColor
        :return: object_found, object_shape, object_color
        :rtype: (bool, ObjectShape, ObjectColor)
        """
        return self.__move_with_vision(Command.MOVE_TO_OBJECT, workspace_name, height_offset, shape, color)

    def detect_object(self, workspace_name, shape=ObjectShape.ANY, color=ObjectColor.ANY):
        """
        Detect object in workspace and return its pose and characteristics

        :param workspace_name: name of the workspace
        :type workspace_name: str
        :param shape: shape of the target
        :type shape: ObjectShape
        :param color: color of the target
        :type color: ObjectColor
        :return: object_found, object_rel_pose, object_shape, object_color
        :rtype: (bool, list, str, str)
        """
        self.__check_type(workspace_name, str)
        self.__check_enum_belonging(shape, ObjectShape)
        self.__check_enum_belonging(color, ObjectColor)

        data_array = self.__send_n_receive(Command.DETECT_OBJECT, workspace_name, shape, color)
        obj_found = eval(data_array[0])
        if not obj_found:
            rel_pose_array = 3 * [0.0]
            shape = "ANY"
            color = "ANY"
        else:
            rel_pose_array = data_array[1:4]
            shape = data_array[4]
            color = data_array[5]

        return obj_found, rel_pose_array, ObjectShape[shape], ObjectColor[color]

    def get_camera_intrinsics(self):
        """
        Get calibration object: camera intrinsics, distortions coefficients

        :return: camera intrinsics, distortions coefficients
        :rtype: (list[list[float]], list[list[float]])
        """
        data = self.__send_n_receive(Command.GET_CAMERA_INTRINSICS)

        mtx = np.reshape(data[0], (3, 3))
        dist = np.expand_dims(data[1], axis=0)
        return mtx, dist

    # - Workspace
    def save_workspace_from_robot_poses(self, workspace_name, pose_origin, pose_2, pose_3, pose_4):
        """
        Save workspace by giving the poses of the robot to point its 4 corners
        with the calibration Tip. Corners should be in the good order.
        Markers' pose will be deduced from these poses

        Poses should be either a list [x, y, z, roll, pitch, yaw] or a PoseObject

        :param workspace_name: workspace name, maximum length 30 char.
        :type workspace_name: str
        :param pose_origin:
        :type pose_origin: Union[list[float], PoseObject]
        :param pose_2:
        :type pose_2: Union[list[float], PoseObject]
        :param pose_3:
        :type pose_3: Union[list[float], PoseObject]
        :param pose_4:
        :type pose_4: Union[list[float], PoseObject]

        :rtype: None
        """
        self.__check_type(workspace_name, str)

        param_list = [workspace_name]
        for pose in (pose_origin, pose_2, pose_3, pose_4):
            if isinstance(pose, PoseObject):
                param_list.append(pose.to_dict())
            else:
                pose_list = self.__args_pose_to_list(pose)
                param_list.append(pose_list)
        self.__send_n_receive(Command.SAVE_WORKSPACE_FROM_POSES, *param_list)

    def save_workspace_from_points(self, workspace_name, point_origin, point_2, point_3, point_4):
        """
        Save workspace by giving the points of worskpace's 4 corners. Points are written as [x, y, z]
        Corners should be in the good order.

        :param workspace_name: workspace name, maximum length 30 char.
        :type workspace_name: str
        :param point_origin:
        :type point_origin: list[float]
        :param point_2:
        :type point_2: list[float]
        :param point_3:
        :type point_3: list[float]
        :param point_4:
        :type point_4: list[float]
        :rtype: None
        """
        self.__check_type(workspace_name, str)

        param_list = [workspace_name]
        for point in (point_origin, point_2, point_3, point_4):
            param_list.append(self.__map_list(point, float))
        self.__send_n_receive(Command.SAVE_WORKSPACE_FROM_POINTS, *param_list)

    def delete_workspace(self, workspace_name):
        """
        Delete workspace from robot's memory

        :param workspace_name:
        :type workspace_name: str
        :rtype: None
        """
        self.__check_type(workspace_name, str)

        self.__send_n_receive(Command.DELETE_WORKSPACE, workspace_name)

    def get_workspace_poses(self, workspace_name):
        raise NotImplementedError

    def get_workspace_ratio(self, workspace_name):
        """
        Get workspace ratio from robot's memory

        :param workspace_name:
        :type workspace_name: str
        :rtype: float
        """
        self.__check_type(workspace_name, str)
        return self.__send_n_receive(Command.GET_WORKSPACE_RATIO, workspace_name)

    def get_workspace_list(self):
        """
        Get list of workspaces' name store in robot's memory

        :rtype: list[str]
        """
        return self.__send_n_receive(Command.GET_WORKSPACE_LIST)

    # Dynamic frames

    def get_saved_dynamic_frame_list(self):
        """
        Get list of saved dynamic frames

        Example: ::

            list_frame, list_desc = robot.get_saved_dynamic_frame_list()
            print(list_frame)
            print(list_desc)

        :return: list of dynamic frames name, list of description of dynamic frames
        :rtype: list[str], list[str]
        """
        return self.__send_n_receive(Command.GET_SAVED_DYNAMIC_FRAME_LIST)

    def get_saved_dynamic_frame(self, frame_name):
        """
        Get name, description and pose of a dynamic frame

        Example: ::

            frame = robot.get_saved_dynamic_frame("default_frame")

        :param frame_name: name of the frame
        :type frame_name: str
        :return: name, description, position and orientation of a frame
        :rtype: list[str, str, list[float]]
        """
        self.__check_type(frame_name, str)
        return self.__send_n_receive(Command.GET_SAVED_DYNAMIC_FRAME, frame_name)

    def save_dynamic_frame_from_poses(self,
                                      frame_name,
                                      description,
                                      pose_origin,
                                      pose_x,
                                      pose_y,
                                      belong_to_workspace=False):
        """
        Create a dynamic frame with 3 poses (origin, x, y)

        Example: ::

            pose_o = [0.1, 0.1, 0.1, 0, 0, 0]
            pose_x = [0.2, 0.1, 0.1, 0, 0, 0]
            pose_y = [0.1, 0.2, 0.1, 0, 0, 0]

            robot.save_dynamic_frame_from_poses("name", "une description test", pose_o, pose_x, pose_y)

        :param frame_name: name of the frame
        :type frame_name: str
        :param description: description of the frame
        :type description: str
        :param pose_origin: pose of the origin of the frame
        :type pose_origin: list[float] [x, y, z, roll, pitch, yaw]
        :param pose_x: pose of the point x of the frame
        :type pose_x: list[float] [x, y, z, roll, pitch, yaw]
        :param pose_y: pose of the point y of the frame
        :type pose_y: list[float] [x, y, z, roll, pitch, yaw]
        :param belong_to_workspace: indicate if the frame belong to a workspace
        :type belong_to_workspace: boolean
        :return: None
        """
        self.__check_type(frame_name, str)
        self.__check_type(description, str)
        self.__check_type(belong_to_workspace, bool)
        self.__check_instance(pose_origin, (list, PoseObject))
        self.__check_instance(pose_x, (list, PoseObject))
        self.__check_instance(pose_y, (list, PoseObject))

        param_list = [frame_name, description]
        for pose in (pose_origin, pose_x, pose_y):
            if isinstance(pose, PoseObject):
                param_list.append(pose.to_dict())
            else:
                pose_list = self.__args_pose_to_list(pose)
                param_list.append(pose_list)
        param_list.append(belong_to_workspace)
        self.__send_n_receive(Command.SAVE_DYNAMIC_FRAME_FROM_POSES, *param_list)

    def save_dynamic_frame_from_points(self,
                                       frame_name,
                                       description,
                                       point_origin,
                                       point_x,
                                       point_y,
                                       belong_to_workspace=False):
        """
        Create a dynamic frame with 3 points (origin, x, y)

        Example: ::

            point_o = [-0.1, -0.1, 0.1]
            point_x = [-0.2, -0.1, 0.1]
            point_y = [-0.1, -0.2, 0.1]

            robot.save_dynamic_frame_from_points("name", "une description test", point_o, point_x, point_y)

        :param frame_name: name of the frame
        :type frame_name: str
        :param description: description of the frame
        :type description: str
        :param point_origin: origin point of the frame
        :type point_origin: list[float] [x, y, z]
        :param point_x: point x of the frame
        :type point_x: list[float] [x, y, z]
        :param point_y: point y of the frame
        :type point_y: list[float] [x, y, z]
        :param belong_to_workspace: indicate if the frame belong to a workspace
        :type belong_to_workspace: boolean
        :return: None
        """
        self.__check_type(frame_name, str)
        self.__check_type(description, str)
        self.__check_type(belong_to_workspace, bool)
        self.__check_type(point_origin, list)
        self.__check_type(point_x, list)
        self.__check_type(point_y, list)

        param_list = [frame_name, description]
        for point in (point_origin, point_x, point_y):
            param_list.append(self.__map_list(point, float))
        param_list.append(belong_to_workspace)
        self.__send_n_receive(Command.SAVE_DYNAMIC_FRAME_FROM_POINTS, *param_list)

    def edit_dynamic_frame(self, frame_name, new_frame_name, new_description):
        """
        Modify a dynamic frame

        Example: ::

            robot.edit_dynamic_frame("name", "new_name", "new description")

        :param frame_name: name of the frame
        :type frame_name: str
        :param new_frame_name: new name of the frame
        :type new_frame_name: str
        :param new_description: new description of the frame
        :type new_description: str
        :return: None
        """
        self.__check_type(frame_name, str)
        self.__check_type(new_frame_name, str)
        self.__check_type(new_description, str)

        param_list = [frame_name, new_frame_name, new_description]
        self.__send_n_receive(Command.EDIT_DYNAMIC_FRAME, *param_list)

    def delete_dynamic_frame(self, frame_name, belong_to_workspace=False):
        """
        Delete a dynamic frame

        Example: ::

            robot.delete_saved_dynamic_frame("name")

        :param frame_name: name of the frame to remove
        :type frame_name: str
        :param belong_to_workspace: indicate if the frame belong to a workspace
        :type belong_to_workspace: boolean
        :return: None
        """
        self.__check_type(frame_name, str)
        self.__check_type(belong_to_workspace, bool)
        self.__send_n_receive(Command.DELETE_DYNAMIC_FRAME, frame_name, belong_to_workspace)

    @deprecated(f'{get_deprecation_msg("move_relative", "move")}')
    def move_relative(self, offset, frame="world"):
        """
        .. deprecated:: 1.2.0
           You should use :func:`move` with a frame in the pose metadata.

        Move robot end of an offset in a frame

        Example: ::
            robot.move_relative([0.05, 0.05, 0.05, 0.3, 0, 0], frame="default_frame")

        :param offset: list which contains offset of x, y, z, roll, pitch, yaw
        :type offset: list[float]
        :param frame: name of local frame
        :type frame: str
        :return: None
        """
        warnings.warn(f'{get_deprecation_msg("move_linear", "move")}', DeprecationWarning, stacklevel=2)
        self.__check_type(frame, str)
        self.__check_type(offset, list)
        if len(offset) != 6:
            self.__raise_exception("An offset must contain 6 members: [x, y, z, roll, pitch, yaw]")

        self.__send_n_receive(Command.MOVE_RELATIVE, offset, frame)

    @deprecated(f'{get_deprecation_msg("move_linear_relative", "move_relative")}')
    def move_linear_relative(self, offset, frame="world"):
        """
        .. deprecated:: 1.2.0
           You should use :func:`move` with a frame in the pose metadata and linear=True.

        Move robot end of an offset by a linear movement in a frame

        Example: ::

            robot.move_linear_relative([0.05, 0.05, 0.05, 0.3, 0, 0], frame="default_frame")

        :param offset: list which contains offset of x, y, z, roll, pitch, yaw
        :type offset: list[float]
        :param frame: name of local frame
        :type frame: str
        :return: None
        """
        warnings.warn(f'{get_deprecation_msg("move_linear_relative", "move_relative")}',
                      DeprecationWarning,
                      stacklevel=2)
        self.__check_type(frame, str)
        self.__check_type(offset, list)
        if len(offset) != 6:
            self.__raise_exception("An offset must contain 6 members: [x, y, z, roll, pitch, yaw]")

        self.__send_n_receive(Command.MOVE_LINEAR_RELATIVE, offset, frame)

    # Sound

    def get_sounds(self):
        """
        Get sound name list

        :return: list of the sounds of the robot
        :rtype: list[string]
        """
        return self.__send_n_receive(Command.GET_SOUNDS)

    def play_sound(self, sound_name, wait_end=True, start_time_sec=0, end_time_sec=0):
        """
        Play a sound from the robot

        :param sound_name: Name of the sound to play
        :type sound_name: string
        :param wait_end: wait for the end of the sound before exiting the function
        :type wait_end: bool
        :param start_time_sec: start the sound from this value in seconds
        :type start_time_sec: float
        :param end_time_sec: end the sound at this value in seconds
        :type end_time_sec: float
        :rtype: None
        """
        self.__check_list_belonging(sound_name, self.get_sounds())
        self.__send_n_receive(Command.PLAY_SOUND, sound_name, wait_end, start_time_sec, end_time_sec)

    def set_volume(self, sound_volume):
        """
        Set the volume percentage of the robot.

        :param sound_volume: volume percentage of the sound (0: no sound, 100: max sound)
        :type sound_volume: int
        :rtype: None
        """
        self.__check_range_belonging(sound_volume, 0, 200)
        self.__send_n_receive(Command.SET_VOLUME, sound_volume)

    def stop_sound(self):
        """
        Stop a sound being played.

        :rtype: None
        """
        self.__send_n_receive(Command.STOP_SOUND)

    def get_sound_duration(self, sound_name):
        """
        Returns the duration in seconds of a sound stored in the robot database
        raise SoundRosWrapperException if the sound doesn't exists

        :param sound_name: name of sound
        :type sound_name: string
        :return: sound duration in seconds
        :rtype: float
        """
        self.__check_list_belonging(sound_name, self.get_sounds())
        return self.__send_n_receive(Command.GET_SOUND_DURATION, sound_name)

    def say(self, text, language=0):
        """
        Use gtts (Google Text To Speech) to interprete a string as sound
        Languages available are:
        * English: 0
        * French: 1
        * Spanish: 2
        * Mandarin: 3
        * Portuguese: 4

        Example ::

            robot.say("Hello", 0)
            robot.say("Bonjour", 1)
            robot.say("Hola", 2)

        :param text: Text that needs to be spoken < 100 char
        :type text: string
        :param language: language of the text
        :type language: int
        :rtype: None
        """
        self.__send_n_receive(Command.SAY, text, language)

    # Led Ring

    def set_led_color(self, led_id, color):
        """
        Lights up an LED in one colour. RGB colour between 0 and 255.

        Example: ::

            robot.set_led_color(5, [15, 50, 255])

        :param led_id: Id of the led: between 0 and 29
        :type led_id: int
        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        """
        self.__send_n_receive(Command.LED_RING_SET_LED, led_id, color)

    def led_ring_solid(self, color):
        """
        Set the whole Led Ring to a fixed color.

        Example: ::

            robot.led_ring_solid([15, 50, 255])

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        """
        self.__send_n_receive(Command.LED_RING_SOLID, color, True)

    def led_ring_turn_off(self):
        """
        Turn off all LEDs

        Example: ::

            robot.led_ring_turn_off()
        """
        self.__send_n_receive(Command.LED_RING_TURN_OFF, True)

    def led_ring_flashing(self, color, period=0, iterations=0, wait=False):
        """
        Flashes a color according to a frequency. The frequency is equal to 1 / period.

        Examples: ::

            robot.led_ring_flashing([15, 50, 255])
            robot.led_ring_flashing([15, 50, 255], 1, 100, True)
            robot.led_ring_flashing([15, 50, 255], iterations=20, wait=True)

            frequency = 20  # Hz
            total_duration = 10 # seconds
            robot.flashing([15, 50, 255], 1./frequency, total_duration * frequency , True)

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive flashes. If 0, the Led Ring flashes endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish all iterations or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_FLASH, color, period, iterations, wait)

    def led_ring_alternate(self, color_list, period=0, iterations=0, wait=False):
        """
        Several colors are alternated one after the other.

        Examples: ::

            color_list = [
                [15, 50, 255],
                [255, 0, 0],
                [0, 255, 0],
            ]

            robot.led_ring_alternate(color_list)
            robot.led_ring_alternate(color_list, 1, 100, True)
            robot.led_ring_alternate(color_list, iterations=20, wait=True)

        :param color_list: Led color list of lists of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color_list: list[list[float]]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive alternations. If 0, the Led Ring alternates endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish all iterations or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_ALTERNATE, color_list, period, iterations, wait)

    def led_ring_chase(self, color, period=0, iterations=0, wait=False):
        """
        Movie theater light style chaser animation.

        Examples: ::


            robot.led_ring_chase([15, 50, 255])
            robot.led_ring_chase([15, 50, 255], 1, 100, True)
            robot.led_ring_chase([15, 50, 255], iterations=20, wait=True)

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive chase. If 0, the animation continues endlessly.
            One chase just lights one Led every 3 LEDs.
        :type iterations: int
        :param wait: The service wait for the animation to finish all iterations or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_CHASE, color, period, iterations, wait)

    def led_ring_wipe(self, color, period=0, wait=False):
        """
        Wipe a color across the Led Ring, light a Led at a time.

        Examples: ::

            robot.led_ring_wipe([15, 50, 255])
            robot.led_ring_wipe([15, 50, 255], 1, True)
            robot.led_ring_wipe([15, 50, 255], wait=True)

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param wait: The service wait for the animation to finish or not to answer.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_WIPE, color, period, wait)

    def led_ring_rainbow(self, period=0, iterations=0, wait=False):
        """
        Draw rainbow that fades across all LEDs at once.

        Examples: ::

            robot.led_ring_rainbow()
            robot.led_ring_rainbow(5, 2, True)
            robot.led_ring_rainbow(wait=True)

        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive rainbows. If 0, the animation continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_RAINBOW, period, iterations, wait)

    def led_ring_rainbow_cycle(self, period=0, iterations=0, wait=False):
        """
        Draw rainbow that uniformly distributes itself across all LEDs.

        Examples: ::

            robot.led_ring_rainbow_cycle()
            robot.led_ring_rainbow_cycle(5, 2, True)
            robot.led_ring_rainbow_cycle(wait=True)

        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive rainbow cycles. If 0, the animation continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_RAINBOW_CYCLE, period, iterations, wait)

    def led_ring_rainbow_chase(self, period=0, iterations=0, wait=False):
        """
        Rainbow chase animation, like the led_ring_chase method.

        Examples: ::

            robot.led_ring_rainbow_chase()
            robot.led_ring_rainbow_chase(5, 2, True)
            robot.led_ring_rainbow_chase(wait=True)

        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive rainbow cycles. If 0, the animation continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_RAINBOW_CHASE, period, iterations, wait)

    def led_ring_go_up(self, color, period=0, iterations=0, wait=False):
        """
        LEDs turn on like a loading circle, and are then all turned off at once.

        Examples: ::

            robot.led_ring_go_up([15, 50, 255])
            robot.led_ring_go_up([15, 50, 255], 1, 100, True)
            robot.led_ring_go_up([15, 50, 255], iterations=20, wait=True)


        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive turns around the Led Ring. If 0, the animation
            continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_GO_UP, color, period, iterations, wait)

    def led_ring_go_up_down(self, color, period=0, iterations=0, wait=False):
        """
        LEDs turn on like a loading circle, and are turned off the same way.

        Examples: ::

            robot.led_ring_go_up_down([15, 50, 255])
            robot.led_ring_go_up_down([15, 50, 255], 1, 100, True)
            robot.led_ring_go_up_down([15, 50, 255], iterations=20, wait=True)


        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive turns around the Led Ring. If 0, the animation
            continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_GO_UP_DOWN, color, period, iterations, wait)

    def led_ring_breath(self, color, period=0, iterations=0, wait=False):
        """
        Variation of the light intensity of the LED ring, similar to human breathing.

        Examples: ::

            robot.led_ring_breath([15, 50, 255])
            robot.led_ring_breath([15, 50, 255], 1, 100, True)
            robot.led_ring_breath([15, 50, 255], iterations=20, wait=True)

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default time will be used.
        :type period: float
        :param iterations: Number of consecutive turns around the Led Ring. If 0, the animation
            continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_BREATH, color, period, iterations, wait)

    def led_ring_snake(self, color, period=0, iterations=0, wait=False):
        """
        A small coloured snake (certainly a python :D ) runs around the LED ring.

        Examples: ::

            robot.led_ring_snake([15, 50, 255])
            robot.led_ring_snake([15, 50, 255], 1, 100, True)

        :param color: Led color in a list of size 3[R, G, B]. RGB channels from 0 to 255.
        :type color: list[float]
        :param period: Execution time for a pattern in seconds. If 0, the default duration will be used.
        :type period: float
        :param iterations: Number of consecutive turns around the Led Ring. If 0, the animation
            continues endlessly.
        :type iterations: int
        :param wait: The service wait for the animation to finish or not to answer. If iterations
                is 0, the service answers immediately.
        :type wait: bool
        """
        self.__send_n_receive(Command.LED_RING_SNAKE, color, period, iterations, wait)

    def led_ring_custom(self, led_colors):
        """
        Sends a colour command to all LEDs of the LED ring.
        The function expects a list of colours for the 30 LEDs  of the robot.

        Example: ::

            led_list = [[i / 30. * 255 , 0, 255 - i / 30.] for i in range(30)]
            robot.led_ring_custom(led_list)

        :param led_colors: List of size 30 of led color in a list of size 3[R, G, B].
                RGB channels from 0 to 255.
        :type led_colors: list[list[float]]
        """
        self.__send_n_receive(Command.LED_RING_CUSTOM, led_colors)
