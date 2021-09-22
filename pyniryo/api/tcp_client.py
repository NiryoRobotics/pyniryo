# - Imports
from __future__ import print_function

# Python libraries
import time
import socket
import numpy as np
import sys

# Communication imports
from .enums_communication import *
from .communication_functions import dict_to_packet, receive_dict, receive_dict_w_payload

from .exceptions import *
from .objects import PoseObject, HardwareStatusObject, DigitalPinObject


class NiryoRobot(object):
    def __init__(self, ip_address=None):
        self.__ip_address = None
        self.__port = TCP_PORT
        self.__client_socket = None

        self.__timeout = TCP_TIMEOUT

        self.__is_running = True
        self.__is_connected = False

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
        print("\nConnected to server ({}) on port: {}\n".format(ip_address, self.__port))

    def __close_socket(self):
        if self.__client_socket is not None and self.__is_connected is True:
            try:
                self.__client_socket.shutdown(socket.SHUT_RDWR)
                self.__client_socket.close()
            except socket.error:
                pass
            self.__is_connected = False
            print("\nDisconnected from robot\n")

    def close_connection(self):
        """
        Close connection with robot

        :rtype: None
        """
        self.__is_running = False
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
                print(e, file=sys.stderr)
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
            print(e, file=sys.stderr)
            raise HostNotReachableException()
        if not received_dict:
            raise HostNotReachableException()
        answer_status = received_dict["status"]
        if answer_status not in ["OK", "KO"]:
            raise InvalidAnswerException(answer_status)
        if received_dict["status"] != "OK":
            raise NiryoRobotException("Command KO : {}".format(received_dict["message"]))
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
        if value not in enum_:
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
        raise TcpCommandException(
            "Expected the following condition: {} <= value <= {}\nGiven: {}".format(range_min, range_max, given))

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

    # --- Public functions --- #

    # - Main purpose

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

    # - Joints/Pose

    @property
    def joints(self):
        return self.get_joints()

    def get_joints(self):
        """
        Get joints value in radians
        You can also use a getter ::

            joints = robot.get_joints()
            joints = robot.joints

        :return: List of joints value
        :rtype: list[float]
        """
        return self.__send_n_receive(Command.GET_JOINTS)

    @property
    def pose(self):
        return self.get_pose()

    def get_pose(self):
        """
        Get end effector link pose as [x, y, z, roll, pitch, yaw].
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians
        You can also use a getter ::

            pose = robot.get_pose()
            pose = robot.pose

        :rtype: PoseObject
        """
        data = self.__send_n_receive(Command.GET_POSE)
        pose_array = self.__map_list(data, float)
        pose_object = PoseObject(*pose_array)
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

    @joints.setter
    def joints(self, *args):
        self.move_joints(*args)

    def move_joints(self, *args):
        """
        Move robot joints. Joints are expressed in radians.

        All lines of the next example realize the same operation: ::

            robot.joints = [0.2, 0.1, 0.3, 0.0, 0.5, 0.0]
            robot.move_joints([0.2, 0.1, 0.3, 0.0, 0.5, 0.0])
            robot.move_joints(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)

        :param args: either 6 args (1 for each joints) or a list of 6 joints
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        joints = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.MOVE_JOINTS, *joints)

    @pose.setter
    def pose(self, *args):
        self.move_pose(*args)

    def move_pose(self, *args):
        """
        Move robot end effector pose to a (x, y, z, roll, pitch, yaw) pose.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in radians

        All lines of the next example realize the same operation: ::

            robot.pose = [0.2, 0.1, 0.3, 0.0, 0.5, 0.0]
            robot.move_pose([0.2, 0.1, 0.3, 0.0, 0.5, 0.0])
            robot.move_pose(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)
            robot.move_pose(PoseObject(0.2, 0.1, 0.3, 0.0, 0.5, 0.0))

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a ``PoseObject``
        :type args: Union[tuple[float], list[float], PoseObject]

        :rtype: None
        """
        pose_list = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.MOVE_POSE, *pose_list)

    def move_linear_pose(self, *args):
        """
        Move robot end effector pose to a (x, y, z, roll, pitch, yaw) pose with a linear trajectory

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[tuple[float], list[float], PoseObject]
        :rtype: None
        """
        pose_list = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.MOVE_LINEAR_POSE, *pose_list)

    def shift_pose(self, axis, shift_value):
        """
        Shift robot end effector pose along one axis

        :param axis: Axis along which the robot is shifted
        :type axis: RobotAxis
        :param shift_value: In meter for X/Y/Z and radians for roll/pitch/yaw
        :type shift_value: float
        :rtype: None
        """
        self.__check_enum_belonging(axis, RobotAxis)
        shift_value = self.__transform_to_type(shift_value, float)
        self.__send_n_receive(Command.SHIFT_POSE, axis, shift_value)

    def shift_linear_pose(self, axis, shift_value):
        """
        Shift robot end effector pose along one axis, with a linear trajectory

        :param axis: Axis along which the robot is shifted
        :type axis: RobotAxis
        :param shift_value: In meter for X/Y/Z and radians for roll/pitch/yaw
        :type shift_value: float
        :rtype: None
        """
        self.__check_enum_belonging(axis, RobotAxis)
        shift_value = self.__transform_to_type(shift_value, float)
        self.__send_n_receive(Command.SHIFT_LINEAR_POSE, axis, shift_value)

    def jog_joints(self, *args):
        """
        Jog robot joints'.
        Jog corresponds to a shift without motion planning.
        Values are expressed in radians.

        :param args: either 6 args (1 for each joints) or a list of 6 joints offset
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        joints_offset = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.JOG_JOINTS, *joints_offset)

    def jog_pose(self, *args):
        """
        Jog robot end effector pose
        Jog corresponds to a shift without motion planning
        Arguments are [dx, dy, dz, d_roll, d_pitch, d_yaw]
        dx, dy & dz are expressed in meters / d_roll, d_pitch & d_yaw are expressed in radians

        :param args: either 6 args (1 for each coordinates) or a list of 6 offset
        :type args: Union[list[float], tuple[float]]
        :rtype: None
        """
        pose_offset = self.__args_joints_to_list(*args)
        self.__send_n_receive(Command.JOG_POSE, *pose_offset)

    def move_to_home_pose(self):
        """
        Move to a position where the forearm lays on shoulder

        :rtype: None
        """
        self.move_joints(0.0, 0.3, -1.3, 0.0, 0.0, 0.0)

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

        :param args: either 6 args (1 for each joints) or a list of 6 joints
        :type args: Union[list[float], tuple[float]]
        :rtype: PoseObject
        """
        joints = self.__args_joints_to_list(*args)
        data = self.__send_n_receive(Command.FORWARD_KINEMATICS, *joints)

        pose_array = self.__map_list(data, float)
        pose_object = PoseObject(*pose_array)
        return pose_object

    def inverse_kinematics(self, *args):
        """
        Compute inverse kinematics

        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a ``PoseObject``
        :type args: Union[tuple[float], list[float], PoseObject]

        :return: List of joints value
        :rtype: list[float]
        """
        pose_list = self.__args_pose_to_list(*args)

        return self.__send_n_receive(Command.INVERSE_KINEMATICS, *pose_list)

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
        return PoseObject(*pose_list)

    def save_pose(self, pose_name, *args):
        """
        Save pose in robot's memory
        
        :type pose_name: str
        :param args: either 6 args (1 for each coordinates) or a list of 6 coordinates or a PoseObject
        :type args: Union[list[float], tuple[float], PoseObject]
        :rtype: None 
        """
        self.__check_type(pose_name, str)
        pose_list = self.__args_pose_to_list(*args)

        self.__send_n_receive(Command.SAVE_POSE, pose_name, *pose_list)

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

    def pick_from_pose(self, *args):
        """
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
        pose = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.PICK_FROM_POSE, *pose)

    def place_from_pose(self, *args):
        """
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
        pose = self.__args_pose_to_list(*args)
        self.__send_n_receive(Command.PLACE_FROM_POSE, *pose)

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
        pick_pose_list = self.__args_pose_to_list(pick_pose)
        place_pos_list = self.__args_pose_to_list(place_pos)

        self.__send_n_receive(Command.PICK_AND_PLACE, pick_pose_list, place_pos_list, dist_smoothing)

    # - Trajectories
    def get_trajectory_saved(self, trajectory_name):
        """
        Get trajectory saved in Ned's memory

        :type trajectory_name: str
        :return: Trajectory
        :rtype: list[list[float]]
        """
        self.__check_type(trajectory_name, str)
        return self.__send_n_receive(Command.GET_TRAJECTORY_SAVED, trajectory_name)

    def execute_trajectory_saved(self, trajectory_name):
        """
        Execute trajectory from Ned's memory

        :type trajectory_name: str
        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        self.__send_n_receive(Command.EXECUTE_TRAJECTORY_SAVED, trajectory_name)

    def execute_trajectory_from_poses(self, list_poses, dist_smoothing=0.0):
        """
        Execute trajectory from list of poses

        :param list_poses: List of [x,y,z,qx,qy,qz,qw] or list of [x,y,z,roll,pitch,yaw]
        :type list_poses: list[list[float]]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        for i, pose in enumerate(list_poses):
            if len(pose) != 7 and len(pose) != 6:
                self.__raise_exception(
                    "7 parameters expected in a pose [x,y,z,qx,qy,qz,qw], or 6 in a pose [x,y,z,roll,pitch,yaw], "
                    "{} parameters given".format(len(pose)))
            list_poses[i] = self.__map_list(pose, float)

        self.__send_n_receive(Command.EXECUTE_TRAJECTORY_FROM_POSES, list_poses, dist_smoothing)

    def execute_trajectory_from_poses_and_joints(self, list_pose_joints, list_type=None, dist_smoothing=0.0):
        """
        Execute trajectory from list of poses and joints

        :param list_pose_joints: List of [x,y,z,qx,qy,qz,qw] or list of [x,y,z,roll,pitch,yaw] or a list of [j1,j2,j3,j4,j5,j6]
        :type list_pose_joints: list[list[float]]
        :param list_type: List of string 'pose' or 'joint', or ['pose'] (if poses only) or ['joint'] (if joints only). 
                        If None, it is assumed there are only poses in the list.
        :type list_type: list[string]
        :param dist_smoothing: Distance from waypoints before smoothing trajectory
        :type dist_smoothing: float
        :rtype: None
        """
        if list_type is None:
            list_type = ['pose']
        for i, pose_or_joint in enumerate(list_pose_joints):
            if len(pose_or_joint) != 7 and len(pose_or_joint) != 6:
                self.__raise_exception(
                    "7 parameters expected in a pose [x,y,z,qx,qy,qz,qw], or 6 in a pose [x,y,z,roll,pitch,yaw], "
                    "or 6 in a joint [j1,j2,j3,j4,j5,j6]"
                    "{} parameters given".format(len(pose_or_joint)))
            list_pose_joints[i] = self.__map_list(pose_or_joint, float)
        self.__send_n_receive(Command.EXECUTE_TRAJECTORY_FROM_POSES_AND_JOINTS, list_pose_joints, list_type,
                              dist_smoothing)

    def save_trajectory(self, trajectory_name, list_poses):
        """
        Save trajectory in robot memory

        :type trajectory_name: str
        :param list_poses: List of [x,y,z,qx,qy,qz,qw] or list of [x,y,z,roll,pitch,yaw]
        :type list_poses: list[list[float]]
        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        for i, pose in enumerate(list_poses):
            if len(pose) != 7 and len(pose) != 6:
                self.__raise_exception(
                    "7 parameters expected in a pose [x,y,z,qx,qy,qz,qw], or 6 in a pose [x,y,z,roll,pitch,yaw], "
                    "{} parameters given".format(len(pose)))
            list_poses[i] = self.__map_list(pose, float)

        self.__send_n_receive(Command.SAVE_TRAJECTORY, trajectory_name, list_poses)

    def delete_trajectory(self, trajectory_name):
        """
        Delete trajectory from robot's memory

        :type trajectory_name: str
        :rtype: None
        """
        self.__check_type(trajectory_name, str)
        self.__send_n_receive(Command.DELETE_TRAJECTORY, trajectory_name)

    def get_saved_trajectory_list(self):
        """
        Get list of trajectories' name saved in robot memory

        :rtype: list[str]
        """
        return self.__send_n_receive(Command.GET_SAVED_TRAJECTORY_LIST)

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
    def open_gripper(self, speed=500):
        """
        Open gripper associated to 'gripper_id' with a speed 'speed'

        :param speed: Between 100 & 1000
        :type speed: int
        :rtype: None
        """
        speed = self.__transform_to_type(speed, int)

        self.__send_n_receive(Command.OPEN_GRIPPER, speed)

    def close_gripper(self, speed=500):
        """
        Close gripper associated to 'gripper_id' with a speed 'speed'

        :param speed: Between 100 & 1000
        :type speed: int
        :rtype: None
        """
        speed = self.__transform_to_type(speed, int)

        self.__send_n_receive(Command.CLOSE_GRIPPER, speed)

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
        :type pin_id: PinID
        :rtype: None
        """
        self.__check_enum_belonging(pin_id, PinID)

        self.__send_n_receive(Command.SETUP_ELECTROMAGNET, pin_id)

    def activate_electromagnet(self, pin_id):
        """
        Activate electromagnet associated to electromagnet_id on pin_id

        :param pin_id:
        :type pin_id: PinID
        :rtype: None
        """
        self.__check_enum_belonging(pin_id, PinID)

        self.__send_n_receive(Command.ACTIVATE_ELECTROMAGNET, pin_id)

    def deactivate_electromagnet(self, pin_id):
        """
        Deactivate electromagnet associated to electromagnet_id on pin_id

        :param pin_id:
        :type pin_id: PinID
        :rtype: None
        """
        self.__check_enum_belonging(pin_id, PinID)
        self.__send_n_receive(Command.DEACTIVATE_ELECTROMAGNET, pin_id)

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
        Reboot the motor of the tool equipped. Useful when an Overload error occurs. (cf HardwareStatus)

        :rtype: None
        """
        self.__send_n_receive(Command.TOOL_REBOOT)

    # - Hardware

    def set_pin_mode(self, pin_id, pin_mode):
        """
        Set pin number pin_id to mode pin_mode

        :param pin_id:
        :type pin_id: PinID
        :param pin_mode:
        :type pin_mode: PinMode
        :rtype: None
        """
        self.__check_enum_belonging(pin_id, PinID)
        self.__check_enum_belonging(pin_mode, PinMode)

        self.__send_n_receive(Command.SET_PIN_MODE, pin_id, pin_mode)

    def digital_write(self, pin_id, digital_state):
        """
        Set pin_id state to digital_state

        :param pin_id:
        :type pin_id: PinID
        :param digital_state:
        :type digital_state: PinState
        :rtype: None
        """
        self.__check_enum_belonging(pin_id, PinID)
        self.__check_enum_belonging(digital_state, PinState)

        self.__send_n_receive(Command.DIGITAL_WRITE, pin_id, digital_state)

    def digital_read(self, pin_id):
        """
        Read pin number pin_id and return its state

        :param pin_id:
        :type pin_id: PinID
        :rtype: PinState
        """
        self.__check_enum_belonging(pin_id, PinID)

        state_id = self.__send_n_receive(Command.DIGITAL_READ, pin_id)
        return PinState[state_id]

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

        hardware_status = HardwareStatusObject(rpi_temperature, hardware_version, connection_up, error_message,
                                               calibration_needed, calibration_in_progress,
                                               motor_names, motor_types,
                                               temperatures, voltages, hardware_errors)
        return hardware_status

    @property
    def digital_io_state(self):
        return self.get_digital_io_state()

    def get_digital_io_state(self):
        """
        Get Digital IO state : Names, modes, states

        :return: List of DigitalPinObject instance
        :rtype: list[DigitalPinObject]
        """
        data = self.__send_n_receive(Command.GET_DIGITAL_IO_STATE)
        digital_pin_array = []
        for pin_info in data:
            pin_id, name, mode, state = pin_info
            digital_pin_array.append(DigitalPinObject(pin_id, name, mode, state))
        return digital_pin_array

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
            print("No conveyor connected !", file=sys.stderr)
            return ConveyorID.NONE
        else:
            print("No new conveyor detected, returning last connected conveyor", file=sys.stderr)
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
        self.__check_range_belonging(brightness_factor, 0.0, np.Inf)
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
        self.__check_range_belonging(contrast_factor, 0.0, np.Inf)
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
        self.__check_range_belonging(saturation_factor, 0.0, np.Inf)
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
                                           workspace_name, height_offset, x_rel, y_rel, yaw_rel)
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
                                           workspace_name, height_offset, shape, color)
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

    def __move_with_vision(self, command, workspace_name, height_offset, shape, color):
        self.__check_type(workspace_name, str)
        height_offset = self.__transform_to_type(height_offset, float)
        self.__check_enum_belonging(shape, ObjectShape)
        self.__check_enum_belonging(color, ObjectColor)

        data_array = self.__send_n_receive(command, workspace_name, height_offset, shape, color)

        obj_found = eval(data_array[0])
        if obj_found is True:
            shape_ret = data_array[1]
            color_ret = data_array[2]
        else:
            shape_ret = "ANY"
            color_ret = 'ANY'
        return obj_found, ObjectShape[shape_ret], ObjectColor[color_ret]

    def vision_pick(self, workspace_name, height_offset=0.0, shape=ObjectShape.ANY, color=ObjectColor.ANY):
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
        :return: object_found, object_shape, object_color
        :rtype: (bool, ObjectShape, ObjectColor)
        """
        return self.__move_with_vision(Command.VISION_PICK, workspace_name, height_offset, shape, color)

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
        :return: object_found, object_pose, object_shape, object_color
        :rtype: (bool, PoseObject, str, str)
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

        :param workspace_name: workspace name, maximum lenght 30 char.
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
            pose_list = self.__args_pose_to_list(pose)
            param_list.append(pose_list)
        self.__send_n_receive(Command.SAVE_WORKSPACE_FROM_POSES, *param_list)

    def save_workspace_from_points(self, workspace_name, point_origin, point_2, point_3, point_4):
        """
        Save workspace by giving the points of worskpace's 4 corners. Points are written as [x, y, z]
        Corners should be in the good order.

        :param workspace_name: workspace name, maximum lenght 30 char.
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
