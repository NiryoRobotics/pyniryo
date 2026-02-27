import math
from collections import UserList
from dataclasses import dataclass

from .._internal import transport_models


class Joints(UserList[float]):
    """
    Represents joint positions for a robot.
    
    A list of float values representing the position of each joint in radians.
    Can optionally include timestamp and velocity information.
    
    :param joints: Variable number of joint positions (in radians).
    """
    timestamp: int | None = None
    velocities: list[float] | None = None

    def __init__(self, *joints: float):
        if len(joints) > 0 and isinstance(joints[0], list):
            joints = joints[0]
        super().__init__(initlist=joints)

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Joints) -> 'Joints':
        return cls(*model.root)

    def to_transport_model(self) -> transport_models.s.Joints:
        return transport_models.s.Joints(root=self.data)

    @classmethod
    def from_a_transport_model(cls, model: transport_models.a.Joints) -> 'Joints':
        m = cls(*model.positions)
        m.timestamp = model.timestamp
        m.velocities = model.velocities
        return m

    def to_a_transport_model(self) -> transport_models.a.Joints:
        return transport_models.a.Joints(positions=self.data, timestamp=self.timestamp, velocities=self.velocities)


@dataclass
class Point:
    """
    Represents a 3D point in Cartesian space.
    
    :param x: The x-coordinate in meters.
    :param y: The y-coordinate in meters.
    :param z: The z-coordinate in meters.
    """
    x: float
    y: float
    z: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Point) -> 'Point':
        return cls(x=model.x, y=model.y, z=model.z)

    def to_transport_model(self) -> transport_models.s.Point:
        return transport_models.s.Point(x=self.x, y=self.y, z=self.z)


@dataclass
class Quaternion:
    """
    Represents orientation using quaternion representation.
    
    :param x: The x component of the quaternion.
    :param y: The y component of the quaternion.
    :param z: The z component of the quaternion.
    :param w: The w (scalar) component of the quaternion.
    """
    x: float
    y: float
    z: float
    w: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Quaternion) -> 'Quaternion':
        return cls(x=model.x, y=model.y, z=model.z, w=model.w)

    def to_transport_model(self) -> transport_models.s.Quaternion:
        return transport_models.s.Quaternion(x=self.x, y=self.y, z=self.z, w=self.w)


@dataclass
class EulerAngles:
    """
    Represents orientation using Euler angles (roll, pitch, yaw).
    
    :param roll: Rotation around the x-axis in radians.
    :param pitch: Rotation around the y-axis in radians.
    :param yaw: Rotation around the z-axis in radians.
    """
    roll: float
    pitch: float
    yaw: float

    def to_quaternion(self) -> Quaternion:
        """
        Convert Euler angles to quaternion representation.
        
        :return: The equivalent Quaternion representation.
        """
        cy = math.cos(self.yaw * 0.5)
        sy = math.sin(self.yaw * 0.5)
        cp = math.cos(self.pitch * 0.5)
        sp = math.sin(self.pitch * 0.5)
        cr = math.cos(self.roll * 0.5)
        sr = math.sin(self.roll * 0.5)
        rw = cr * cp * cy + sr * sp * sy
        rx = sr * cp * cy - cr * sp * sy
        ry = cr * sp * cy + sr * cp * sy
        rz = cr * cp * sy - sr * sp * cy

        return Quaternion(rx, ry, rz, rw)


@dataclass
class Pose:
    """
    Represents a pose in 3D space, defined by a position and an orientation.
     - The position is represented by a Point (x, y, z).
     - The orientation can be represented either as a Quaternion (x, y, z, w) or as Euler angles (roll, pitch, yaw).

     The choice between Quaternion and Euler angles is left to the user.
     Keep in mind that the Nate API expects orientations to be sent as Quaternions, so Euler angles will be
     automatically converted to Quaternions when sending commands to the API.
    """
    position: Point
    orientation: Quaternion | EulerAngles

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Pose) -> 'Pose':
        return cls(
            position=Point.from_transport_model(model.position),
            orientation=Quaternion.from_transport_model(model.orientation),
        )

    def to_transport_model(self) -> transport_models.s.Pose:
        quaternion = self.orientation
        if isinstance(self.orientation, EulerAngles):
            quaternion = self.orientation.to_quaternion()

        return transport_models.s.Pose(position=self.position.to_transport_model(),
                                       orientation=quaternion.to_transport_model())
