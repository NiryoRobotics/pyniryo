#!/usr/bin/env python
# coding=utf-8
import math
import re

import numpy as np

from .enums_communication import LengthUnit


class PoseMetadata:
    """
    Represents all the metadata of a PoseObject.

    :ivar version: The version of the metadata. Each new version adds more attributes.
                   (use :func:`v1` or :func:`v2` to quickly create a default metadata instance)
    :type version: int
    :ivar frame: Name of the frame if the pose is relative to a frame other than the world.
    :type frame: str
    :ivar length_unit: The length unit of the position (x, y, z). Default: :const:`LengthUnit.METERS`
    :type length_unit: LengthUnit
    """
    __DEFAULT_LENGTH_UNIT = LengthUnit.METERS
    __DEFAULT_FRAME = ''

    def __init__(self, version, frame=__DEFAULT_FRAME, length_unit=__DEFAULT_LENGTH_UNIT):
        self.version = version
        self.frame = frame
        self.length_unit = length_unit

    def __eq__(self, other):
        return self.version == other.version and self.frame == other.frame and self.length_unit == other.length_unit

    def to_dict(self):
        """
        :return: A dictionary representing the object.
        :rtype: dict
        """
        return {'version': self.version, 'frame': self.frame, 'length_unit': self.length_unit.name}

    @classmethod
    def from_dict(cls, d):
        """
        Creates a new object from a dictionary representing the object.
        :param d: A dictionary representing the object.
        :type d: dict
        :return: A new PoseMetadata instance.
        :rtype: PoseMetadata
        """
        if d['version'] == 1:
            return cls.v1()
        elif d['version'] == 2:
            return cls.v2(d['frame'], LengthUnit[d['length_unit']])

    @classmethod
    def v1(cls, frame=__DEFAULT_FRAME):
        """
        Quickly creates a new PoseMetadata instance initialized as a V1 pose.
        :param frame: The frame of the pose to create.
        :type frame: str
        """
        return cls(1, frame=frame)

    @classmethod
    def v2(cls, frame=__DEFAULT_FRAME, length_unit=__DEFAULT_LENGTH_UNIT):
        """
        Quickly creates a new PoseMetadata instance initialized as a V2 pose.

        :param frame: The frame of the pose to create. Default:
        :type frame: str
        :param length_unit: The length unit of the position (x, y, z). Default:
        """
        return cls(2, frame=frame, length_unit=length_unit)


class PoseObject:
    """
    Pose object which stores x, y, z, roll, pitch & yaw parameters

    :param x: The x coordinate of the pose.
    :type x: float
    :param y: The y coordinate of the pose.
    :type y: float
    :param z: The z coordinate of the pose.
    :type z: float
    :param roll: The roll angle of the pose.
    :type roll: float
    :param pitch: The pitch angle of the pose.
    :type pitch: float
    :param yaw: The yaw angle of the pose.
    :type yaw: float
    :param metadata: The metadata of the pose.
    :type metadata: PoseMetadata
    """

    def __init__(self, x, y, z, roll, pitch, yaw, metadata=PoseMetadata.v2()):
        # X (meter)
        self.x = float(x)
        # Y (meter)
        self.y = float(y)
        # Z (meter)
        self.z = float(z)
        # Roll (radian)
        self.roll = float(roll)
        # Pitch (radian)
        self.pitch = float(pitch)
        # Yaw (radian)
        self.yaw = float(yaw)
        self.metadata = metadata

    def __str__(self):
        position = "x = {:.4f}, y = {:.4f}, z = {:.4f}".format(self.x, self.y, self.z)
        orientation = "roll = {:.3f}, pitch = {:.3f}, yaw = {:.3f}".format(self.roll, self.pitch, self.yaw)
        return position + "\n" + orientation

    def __repr__(self):
        return self.__str__()

    def copy_with_offsets(self, x_offset=0., y_offset=0., z_offset=0., roll_offset=0., pitch_offset=0., yaw_offset=0.):
        """
        Create a new pose from copying actual pose with offsets

        :param x_offset: Offset of the x coordinate of the new pose.
        :type x_offset: float
        :param y_offset: Offset of the y coordinate of the new pose.
        :type y_offset: float
        :param z_offset: Offset of the z coordinate of the new pose.
        :type z_offset: float
        :param roll_offset: Offset of the roll angle of the new pose.
        :type roll_offset: float
        :param pitch_offset: Offset of the pitch angle of the new pose.
        :type pitch_offset: float
        :param yaw_offset: Offset of the yaw angle of the new pose.
        :type yaw_offset: float

        :return: A new PoseObject with the applied offsets.
        :rtype: PoseObject
        """
        return PoseObject(self.x + x_offset,
                          self.y + y_offset,
                          self.z + z_offset,
                          self.roll + roll_offset,
                          self.pitch + pitch_offset,
                          self.yaw + yaw_offset,
                          self.metadata)

    def __iter__(self):
        for attr in self.to_list():
            yield attr

    def __getitem__(self, value):
        return self.to_list()[value]

    def __setitem__(self, key, value):
        attr = ['x', 'y', 'z', 'roll', 'pitch', 'yaw'][key]
        setattr(self, attr, value)

    def __len__(self):
        return 6

    def __eq__(self, other):
        return self.to_list() == other.to_list() and self.metadata == other.metadata

    def to_list(self):
        """
        :return: A list [x, y, z, roll, pitch, yaw]
        :rtype: list[float]
        """
        list_pos = [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]
        return list(map(float, list_pos))

    def to_dict(self):
        """
        :return: A dictionary representing the object.
        :rtype: dict
        """
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'roll': self.roll,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'metadata': self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls, d):
        """
        Creates a new PoseObject from a dictionary representing the object.

        :param d: A dictionary representing the object.
        :type d: dict
        """
        args = [d['x'], d['y'], d['z'], d['roll'], d['pitch'], d['yaw']]
        if 'metadata' in d:
            args.append(PoseMetadata.from_dict(d['metadata']))
        return cls(*args)

    def quaternion(self, normalization_tolerance=0.00001):
        """
        Convert the pose rotation (euler angles) to a quaternion.

        :param normalization_tolerance: Tolerance for quaternion normalization.
        :type normalization_tolerance: float
        :return: A quaternion.
        :rtype: list
        """
        # simplified version of the tf.transformations.quaternion_from_euler function
        ai = self.roll / 2.0
        aj = self.pitch / 2.0
        ak = self.yaw / 2.0
        ci = math.cos(ai)
        si = math.sin(ai)
        cj = math.cos(aj)
        sj = math.sin(aj)
        ck = math.cos(ak)
        sk = math.sin(ak)
        cc = ci * ck
        cs = ci * sk
        sc = si * ck
        ss = si * sk

        quaternion = np.array([
            cj * sc - sj * cs,
            cj * ss + sj * cc,
            cj * cs - sj * sc,
            cj * cc + sj * ss,
        ])

        # Normalize the quaternion
        mag2 = np.square(quaternion).sum()
        if mag2 <= normalization_tolerance:
            return quaternion
        mag = math.sqrt(mag2)
        normalized_quaternion = quaternion / mag
        return normalized_quaternion.tolist()


class JointsPositionMetadata:
    """
    Metadata for a JointsPosition object.
    """

    def __init__(self, version):
        self.version = version

    def to_dict(self):
        return {'version': self.version}

    @classmethod
    def from_dict(cls, d):
        return cls(d['version'])

    @classmethod
    def v1(cls):
        return cls(version=1)


class JointsPosition:
    """
    Represents a robot position given by the position of each of its joints

    :param joints: all the joints positions
    :type joints: float
    """

    def __init__(self, *joints, **kwargs):
        self.__joints = list(joints)
        self.metadata = kwargs.get('metadata', JointsPositionMetadata.v1())

    def __iter__(self):
        return iter(self.__joints)

    def __getitem__(self, item):
        return self.__joints[item]

    def __setitem__(self, key, value):
        self.__joints[key] = value

    def __len__(self):
        return len(self.__joints)

    def __eq__(self, other):
        return self.__joints == other.__joints

    def to_list(self):
        """
        :return: A list containing all the joints positions.
        :rtype: list[float]
        """
        return list(self.__joints)

    def to_dict(self):
        """
        :return: A dictionary representing the object.
        :rtype: dict
        """
        d = {f'joint_{n}': joint for n, joint in enumerate(self.__joints)}
        d['metadata'] = self.metadata.to_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        """
        Creates a new JointsPosition object from a dictionary representing the object.

        :param d: A dictionary representing the object.
        :type d: dict
        """
        joints = []
        other_args = {}
        for name, value in d.items():
            if re.match(r'^joint_\d+$', name):
                joints.append(value)
        if 'metadata' in d:
            other_args['metadata'] = JointsPositionMetadata.from_dict(d['metadata'])
        return cls(*joints, **other_args)

    def __repr__(self):
        args = [str(joint) for joint in self.__joints]
        args += [f'{name}={repr(value)}' for name, value in self.__dict__.items() if value != self.__joints]
        repr_str = f'{self.__class__.__name__}({", ".join(args)})'
        return repr_str


class HardwareStatusObject:
    """
    Object used to store every hardware information
    """

    def __init__(self,
                 rpi_temperature,
                 hardware_version,
                 connection_up,
                 error_message,
                 calibration_needed,
                 calibration_in_progress,
                 motor_names,
                 motor_types,
                 motors_temperature,
                 motors_voltage,
                 hardware_errors):
        # Number representing the rpi temperature
        self.rpi_temperature = rpi_temperature
        # Number representing the hardware version
        self.hardware_version = hardware_version
        # Boolean indicating if the connection with the robot is up
        self.connection_up = connection_up
        # Error message status on error
        self.error_message = error_message
        # Boolean indicating if a calibration is needed
        self.calibration_needed = calibration_needed
        # Boolean indicating if calibration is in progress
        self.calibration_in_progress = calibration_in_progress

        # Following list describe each motor
        # Row 0 for first motor, row 1 for second motor, row 2 for third motor, row 3 for fourth motor
        # List of motor names
        self.motor_names = motor_names
        # List of motor types
        self.motor_types = motor_types
        # List of motors_temperature
        self.motors_temperature = motors_temperature
        # List of motors_voltage
        self.motors_voltage = motors_voltage
        # List of hardware errors
        self.hardware_errors = hardware_errors

    def __str__(self):
        list_string_ret = list()
        list_string_ret.append("Temp (°C) : {}".format(self.rpi_temperature))
        list_string_ret.append("Hardware version : {}".format(self.hardware_version))
        list_string_ret.append("Connection Up : {}".format(self.connection_up))
        list_string_ret.append("Error Message : {}".format(self.error_message))
        list_string_ret.append("Calibration Needed : {}".format(self.calibration_needed))
        list_string_ret.append("Calibration in progress : {}".format(self.calibration_in_progress))
        list_string_ret.append("MOTORS INFOS : Motor1, Motor2, Motor3, Motor4, Motor5, Motor6,")
        list_string_ret.append("Names : {}".format(self.motor_names))
        list_string_ret.append("Types : {}".format(self.motor_types))
        list_string_ret.append("Temperatures : {}".format(self.motors_temperature))
        list_string_ret.append("Voltages : {}".format(self.motors_voltage))
        list_string_ret.append("Hardware errors : {}".format(self.hardware_errors))
        return "\n".join(list_string_ret)

    def __repr__(self):
        return self.__str__()


class DigitalPinObject:
    """
    Object used to store information on digital pins
    """

    def __init__(self, pin_id, name, mode, state):
        # Pin ID
        self.pin_id = pin_id
        # Name
        self.name = name
        # Input or output
        self.mode = mode
        # High or Low
        self.state = state

    def __str__(self):
        string_ret = "Pin : {}".format(self.pin_id)
        string_ret += ", Name : {}".format(self.name)
        string_ret += ", Mode : {}".format(self.mode)
        string_ret += ", State : {}".format(self.state)
        return string_ret

    def __repr__(self):
        return self.__str__()


class AnalogPinObject:
    """
    Object used to store information on digital pins
    """

    def __init__(self, pin_id, name, mode, value):
        # Pin ID
        self.pin_id = pin_id
        # Name
        self.name = name
        # Input or output
        self.mode = mode
        # Tension
        self.value = value

    def __str__(self):
        string_ret = "Pin : {}".format(self.pin_id)
        string_ret += ", Name : {}".format(self.name)
        string_ret += ", Mode : {}".format(self.mode)
        string_ret += ", State : {}".format(self.value)
        return string_ret

    def __repr__(self):
        return self.__str__()
