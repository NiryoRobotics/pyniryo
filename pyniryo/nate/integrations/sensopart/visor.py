from pyniryo.nate import models
import socket
import math

cam_ip = "192.168.1.245"
_DEFAULT_CAMERA_PORT = 2006


def _deserialize_coordinate(coordinate: str) -> float:
    return int(coordinate) / 1000000


def _deserialize_angle(angle: str) -> float:
    return math.radians(int(angle) / 1000)


def _deserialize_pose(data: list[str]) -> models.Pose:
    if len(data) != 6:
        raise ValueError(f"Expected 6 elements, got {len(data)}")
    x, y, z = [_deserialize_coordinate(c) for c in data[:3]]
    roll, pitch, yaw = [_deserialize_angle(a) for a in data[3:]]
    return models.Pose.from_sequence(x, y, z, roll, pitch, yaw)


def _deserialize_poses(payload: str) -> list[models.Pose]:
    parsed = payload[1:-1].split(',')  # strips opening and closing parenthesis
    found = parsed[1] == 'P'
    if not found:
        return []

    n_objects = int(parsed[2])
    objects: list[models.Pose] = []
    parsed = parsed[3:]
    for i in range(0, n_objects):
        objects.append(_deserialize_pose(parsed[6 * i:6 * (i + 1)]))
    return objects


class Visor:

    def __init__(self, camera_hostname: str, camera_port: int = _DEFAULT_CAMERA_PORT):
        self._camera_hostname = camera_hostname
        self._camera_port = camera_port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._camera_hostname, self._camera_port))

    def _handshake(self) -> int:
        self._socket.send(b"TRX00")
        msg, _, _, _ = self._socket.recvmsg(15)
        msg_size = int(msg[-3:])
        return msg_size

    def get_object(self) -> models.Pose | list[models.Pose]:
        next_msg_size = self._handshake()
        msg, _, _, _ = self._socket.recvmsg(next_msg_size)
        return _deserialize_poses(msg.decode())
