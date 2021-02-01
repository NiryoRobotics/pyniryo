#!/usr/bin/env python
# coding=utf-8


class PoseObject:
    """
    Pose object which stores x, y, z, roll, pitch & yaw parameters
    """
    def __init__(self, x, y, z, roll, pitch, yaw):
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

    def __str__(self):
        position = "x = {:.4f}, y = {:.4f}, z = {:.4f}".format(self.x, self.y, self.z)
        orientation = "roll = {:.3f}, pitch = {:.3f}, yaw = {:.3f}".format(self.roll, self.pitch, self.yaw)
        return position + "\n" + orientation

    def __repr__(self):
        return self.__str__()

    def copy_with_offsets(self, x_offset=0., y_offset=0., z_offset=0., roll_offset=0., pitch_offset=0., yaw_offset=0.):
        """
        Create a new pose from copying from copying actual pose with offsets

        :rtype: PoseObject
        """
        return PoseObject(self.x + x_offset,
                          self.y + y_offset,
                          self.z + z_offset,
                          self.roll + roll_offset,
                          self.pitch + pitch_offset,
                          self.yaw + yaw_offset)

    def to_list(self):
        """
        Return a list [x, y, z, roll, pitch, yaw] corresponding to the pose's parameters

        :rtype: list[float]
        """
        list_pos = [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]
        return list(map(float, list_pos))


class HardwareStatusObject:
    """
    Object used to store every hardware information
    """

    def __init__(self, rpi_temperature, hardware_version, connection_up,
                 error_message, calibration_needed, calibration_in_progress,
                 motor_names, motor_types,
                 motors_temperature, motors_voltage, hardware_errors):
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
