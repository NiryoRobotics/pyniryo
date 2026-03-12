import unittest
import math
import socket
from unittest.mock import MagicMock, patch

from pyniryo.nate.integrations.sensopart.visor import (
    _deserialize_coordinate,
    _deserialize_angle,
    _deserialize_pose,
    _deserialize_poses,
    Visor,
)
from pyniryo.nate.models import geometry


class TestDeserializeCoordinate(unittest.TestCase):
    """Test the _deserialize_coordinate helper function."""

    def test_basic_conversion(self):
        """Test basic coordinate conversion."""
        result = _deserialize_coordinate("1000000")
        self.assertEqual(result, 1.0)

    def test_negative_coordinate(self):
        """Test negative coordinate conversion."""
        result = _deserialize_coordinate("-500000")
        self.assertEqual(result, -0.5)

    def test_zero_coordinate(self):
        """Test zero coordinate conversion."""
        result = _deserialize_coordinate("0")
        self.assertEqual(result, 0.0)

    def test_large_coordinate(self):
        """Test large coordinate conversion."""
        result = _deserialize_coordinate("123456789")
        self.assertAlmostEqual(result, 123.456789, places=6)


class TestDeserializeAngle(unittest.TestCase):
    """Test the _deserialize_angle helper function."""

    def test_basic_conversion(self):
        """Test basic angle conversion to radians."""
        # 180000 milliradians = 180 radians = π radians after conversion
        result = _deserialize_angle("180000")
        expected = math.radians(180.0)
        self.assertAlmostEqual(result, expected, places=6)

    def test_negative_angle(self):
        """Test negative angle conversion."""
        result = _deserialize_angle("-90000")
        expected = math.radians(-90.0)
        self.assertAlmostEqual(result, expected, places=6)

    def test_zero_angle(self):
        """Test zero angle conversion."""
        result = _deserialize_angle("0")
        self.assertEqual(result, 0.0)

    def test_full_rotation(self):
        """Test full rotation angle."""
        result = _deserialize_angle("360000")
        expected = math.radians(360.0)
        self.assertAlmostEqual(result, expected, places=6)


class TestDeserializePose(unittest.TestCase):
    """Test the _deserialize_pose helper function."""

    def test_valid_pose(self):
        """Test deserializing valid pose data."""
        data = ["100000", "200000", "300000", "45000", "90000", "180000"]
        pose = _deserialize_pose(data)

        self.assertIsInstance(pose, geometry.Pose)
        self.assertAlmostEqual(pose.position.x, 0.1, places=6)
        self.assertAlmostEqual(pose.position.y, 0.2, places=6)
        self.assertAlmostEqual(pose.position.z, 0.3, places=6)

        # Check orientation (should be Quaternion or EulerAngles)
        self.assertIsInstance(pose.orientation, (geometry.Quaternion, geometry.EulerAngles))

    def test_zero_pose(self):
        """Test deserializing zero pose."""
        data = ["0", "0", "0", "0", "0", "0"]
        pose = _deserialize_pose(data)

        self.assertEqual(pose.position.x, 0.0)
        self.assertEqual(pose.position.y, 0.0)
        self.assertEqual(pose.position.z, 0.0)

    def test_negative_values(self):
        """Test deserializing pose with negative values."""
        data = ["-100000", "-200000", "-300000", "-45000", "-90000", "-180000"]
        pose = _deserialize_pose(data)

        self.assertAlmostEqual(pose.position.x, -0.1, places=6)
        self.assertAlmostEqual(pose.position.y, -0.2, places=6)
        self.assertAlmostEqual(pose.position.z, -0.3, places=6)

    def test_invalid_data_length(self):
        """Test error with wrong number of elements."""
        with self.assertRaises(ValueError) as context:
            _deserialize_pose(["100000", "200000", "300000"])
        self.assertIn("Expected 6 elements, got 3", str(context.exception))

    def test_invalid_data_length_too_many(self):
        """Test error with too many elements."""
        with self.assertRaises(ValueError) as context:
            _deserialize_pose(["100000", "200000", "300000", "0", "0", "0", "0"])
        self.assertIn("Expected 6 elements, got 7", str(context.exception))


class TestDeserializePoses(unittest.TestCase):
    """Test the _deserialize_poses helper function."""

    def test_not_found(self):
        """Test parsing payload when no object is found."""
        payload = "(123,N,0)"
        result = _deserialize_poses(payload)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_single_object_found(self):
        """Test parsing payload with single object."""
        payload = "(123,P,1,100000,200000,300000,45000,90000,180000)"
        result = _deserialize_poses(payload)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], geometry.Pose)
        self.assertAlmostEqual(result[0].position.x, 0.1, places=6)
        self.assertAlmostEqual(result[0].position.y, 0.2, places=6)
        self.assertAlmostEqual(result[0].position.z, 0.3, places=6)

    def test_multiple_objects_found(self):
        """Test parsing payload with multiple objects."""
        payload = "(123,P,2,100000,200000,300000,0,0,0,400000,500000,600000,0,0,0)"
        result = _deserialize_poses(payload)

        self.assertEqual(len(result), 2)

        # First object
        self.assertAlmostEqual(result[0].position.x, 0.1, places=6)
        self.assertAlmostEqual(result[0].position.y, 0.2, places=6)
        self.assertAlmostEqual(result[0].position.z, 0.3, places=6)

        # Second object
        self.assertAlmostEqual(result[1].position.x, 0.4, places=6)
        self.assertAlmostEqual(result[1].position.y, 0.5, places=6)
        self.assertAlmostEqual(result[1].position.z, 0.6, places=6)

    def test_zero_objects(self):
        """Test parsing payload with zero count but 'P' flag."""
        payload = "(123,P,0)"
        result = _deserialize_poses(payload)

        self.assertEqual(len(result), 0)


class TestVisor(unittest.TestCase):
    """Test the Visor class."""

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_constructor(self, mock_socket_class):
        """Test Visor constructor creates and connects socket."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        visor = Visor("192.168.1.245", 2006)

        # Verify socket was created with correct parameters
        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

        # Verify socket connect was called
        mock_socket.connect.assert_called_once_with(("192.168.1.245", 2006))

        self.assertEqual(visor._camera_hostname, "192.168.1.245")
        self.assertEqual(visor._camera_port, 2006)

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_constructor_default_port(self, mock_socket_class):
        """Test Visor constructor with default port."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        visor = Visor("192.168.1.245")

        # Verify default port is used
        mock_socket.connect.assert_called_once_with(("192.168.1.245", 2006))
        self.assertEqual(visor._camera_port, 2006)

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_handshake(self, mock_socket_class):
        """Test _handshake method."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        # Mock recvmsg to return a message with size
        mock_socket.recvmsg.return_value = (b"ACK123", None, None, None)

        visor = Visor("192.168.1.245")
        msg_size = visor._handshake()

        # Verify TRX00 was sent
        mock_socket.send.assert_called_once_with(b"TRX00")

        # Verify recvmsg was called
        mock_socket.recvmsg.assert_called_once_with(15)

        # Verify size extraction (last 3 characters)
        self.assertEqual(msg_size, 123)

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_get_object_not_found(self, mock_socket_class):
        """Test get_object when no object is found."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        # Mock handshake response
        mock_socket.recvmsg.side_effect = [
            (b"ACK018", None, None, None),  # Handshake
            (b"(456,N,0)", None, None, None),  # Actual data
        ]

        visor = Visor("192.168.1.245")
        result = visor.get_object()

        # Verify handshake happened
        self.assertEqual(mock_socket.send.call_count, 1)
        self.assertEqual(mock_socket.recvmsg.call_count, 2)

        # Verify result is empty list
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_get_object_single_pose(self, mock_socket_class):
        """Test get_object when single object is found."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        payload = "(123,P,1,100000,200000,300000,45000,90000,180000)"
        mock_socket.recvmsg.side_effect = [
            (b"ACK069", None, None, None),  # Handshake (payload length is 50)
            (payload.encode(), None, None, None),  # Actual data
        ]

        visor = Visor("192.168.1.245")
        result = visor.get_object()

        # Verify result is list with one pose
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], geometry.Pose)
        self.assertAlmostEqual(result[0].position.x, 0.1, places=6)

    @patch('pyniryo.nate.integrations.sensopart.visor.socket.socket')
    def test_get_object_multiple_poses(self, mock_socket_class):
        """Test get_object when multiple objects are found."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        payload = "(123,P,2,100000,200000,300000,0,0,0,400000,500000,600000,0,0,0)"
        mock_socket.recvmsg.side_effect = [
            (b"ACK099", None, None, None),  # Handshake
            (payload.encode(), None, None, None),  # Actual data
        ]

        visor = Visor("192.168.1.245")
        result = visor.get_object()

        # Verify result is list with two poses
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Check first pose
        self.assertAlmostEqual(result[0].position.x, 0.1, places=6)
        self.assertAlmostEqual(result[0].position.y, 0.2, places=6)

        # Check second pose
        self.assertAlmostEqual(result[1].position.x, 0.4, places=6)
        self.assertAlmostEqual(result[1].position.y, 0.5, places=6)


if __name__ == "__main__":
    unittest.main()
