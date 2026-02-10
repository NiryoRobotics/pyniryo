import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Callable, List
from uuid import uuid4
import time

from .. import models
from .._internal import transport_models, paths_gen, topics_gen
from .._internal.mqtt import MqttClient
from ..models import Pose, Waypoint

from . import BaseAPIComponent

logger = logging.getLogger(__name__)

JointsCallback = Callable[[models.Joints], None]


class MoveCommand:

    def __init__(self, mqtt_client: MqttClient, command_id: str):
        self.__mqtt_client: MqttClient = mqtt_client
        self.__command_id: str = command_id

        self.__mqtt_client.subscribe(self.topic, self.__move_feedback_callback, transport_models.MoveFeedback)
        self.__feedbacks: List[models.MoveFeedback] = [models.MoveFeedback(state=models.MoveState.UNKNOWN, message="")]

    def __move_feedback_callback(self, _topic: str, payload: transport_models.MoveFeedback) -> None:
        """
        Internal callback to handle move feedback messages.
        """
        self.__feedbacks.append(models.MoveFeedback.from_transport_model(payload))

        if self.state.is_final():
            self.__mqtt_client.unsubscribe(self.__move_feedback_callback)

    @property
    def state(self) -> models.MoveState:
        """
        Get the current state of the move command.

        :return: The current state of the move command.
        """
        return self.__feedbacks[-1].state

    @property
    def command_id(self) -> str:
        """
        Get the command ID of the move command.

        :return: The command ID.
        """
        return str(self.__command_id)

    @property
    def topic(self) -> str:
        """
        Get the topic of the move command.

        :return: The topic of the move command.
        """
        return topics_gen.Robot.ROBOT_MOVE_FEEDBACK.format(cmd_id=self.__command_id)

    def wait(self, timeout: float = -1) -> None:
        """
        Wait for the move command to complete.
        :param timeout: The maximum time to wait in seconds. If negative, wait indefinitely.
        """
        start = time.monotonic()
        while not self.state.is_final():
            if timeout > 0 and start + timeout < time.monotonic():
                raise TimeoutError(f'Move command {self.__command_id} timed out after {timeout} seconds.')
            time.sleep(0.1)
        if self.state.is_error():
            raise self.state.get_exception()(
                f'Move command {self.__command_id} failed with error: {self.__feedbacks[-1].message}')


class Robot(BaseAPIComponent):

    def get_joints(self) -> models.Joints:
        """
        Get the current joint positions of the robot.

        :return: The current joint positions as a Joints object.
        """
        joints = self._http_client.get(paths_gen.Robot.GET_ROBOT_JOINTS, transport_models.Joints)
        return models.Joints.from_transport_model(joints)

    def on_joints_received(self, callback: JointsCallback) -> None:
        """
        Set the callback to call when the robot's joints are received.

        :param callback: The callback to call. The callback must take the topic and the joints as parameters.
        """

        def internal_callback(_, joints: transport_models.Joints) -> None:
            callback(models.Joints.from_transport_model(joints))

        self._mqtt_client.subscribe(topics_gen.Robot.JOINTS, internal_callback, transport_models.Joints)

    def get_all_frames(self) -> List[str]:
        """
        Get all frames defined in the robot.

        :return: A list of Frame objects.
        """
        frames = self._http_client.get(
            paths_gen.Robot.GET_ALL_FRAMES,
            transport_models.FrameIdList,
        )
        return frames.root

    def get_frame_pose(self, frame_id: str) -> Pose:
        """
        Get a specific frame by its ID.

        :param frame_id: The ID of the frame to retrieve.
        :return: The current pose of the frame as a Pose object.
        """
        pose = self._http_client.get(
            paths_gen.Robot.GET_FRAME_POSE.format(frame_id=frame_id),
            transport_models.Pose,
        )
        return models.Pose.from_transport_model(pose)

    @staticmethod
    def _normalize_move_target(target: models.MoveTarget) -> models.Waypoints:
        if isinstance(target, models.Joints):
            return models.Waypoints([Waypoint(joints=target)])
        if isinstance(target, models.Pose):
            return models.Waypoints([Waypoint(pose=target)])
        if isinstance(target, models.Waypoint):
            return models.Waypoints([target])
        if isinstance(target, models.Waypoints):
            return target
        else:
            valid_types = ', '.join(f'{m.__module__}.{m.__qualname__}' for m in models.MoveTarget.__args__)
            raise TypeError(f'Invalid type {target.__class__.__name__} for target. Expected one of {valid_types}')

    def move(self, target: models.MoveTarget) -> MoveCommand:
        """
        Move the robot according to the provided target. Note that if a joints and pose are provided in the same
        waypoint, the robot will prioritize the joints target and ignore the pose target.

        :param target: The target to reach
        :return: A MoveCommand object to track the progress of the movement.
        """
        command_id = uuid4()
        move_command = MoveCommand(self._mqtt_client, str(command_id))

        target = self._normalize_move_target(target)
        self._http_client.post(
            paths_gen.Robot.MOVE_ALONG_WAYPOINTS,
            transport_models.FeedbackResponse,
            transport_models.MoveWaypoints(command_id=command_id, waypoints=[w.to_transport_model() for w in target]),
        )
        return move_command

    def execute_trajectory(self, trajectory: models.Trajectory) -> MoveCommand:
        """
        Execute a trajectory on the robot.

        :param trajectory: The trajectory to execute.
        :return: A MoveCommand object to track the progress of the movement.
        """
        command_id = uuid4()
        move_command = MoveCommand(self._mqtt_client, str(command_id))

        self._http_client.post(
            paths_gen.Robot.EXECUTE_TRAJECTORY,
            transport_models.FeedbackResponse,
            transport_models.TrajectoryExecution(command_id=command_id, trajectory=trajectory.to_transport_model()),
        )
        return move_command

    def get_urdf(self) -> ET.Element:
        buffer = BytesIO()
        self._http_client.download(paths_gen.Robot.GET_ROBOT_URDF, buffer)
        buffer.seek(0)
        tree = ET.parse(buffer)
        return tree.getroot()

    def get_configuration(self) -> models.RobotConfiguration:
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONFIG, transport_models.RobotConfig)
        return models.RobotConfiguration.from_transport_model(resp)

    def get_control_mode(self) -> models.ControlMode:
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONTROL_MODE, transport_models.ControlMode)
        return models.ControlMode.from_transport_model(resp)

    def set_control_mode(self, mode: models.ControlMode) -> None:
        self._http_client.put(paths_gen.Robot.SET_ROBOT_CONTROL_MODE,
                              transport_models.FeedbackResponse,
                              mode.to_transport_model())
