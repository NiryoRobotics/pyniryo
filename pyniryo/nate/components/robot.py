import logging
from typing import Callable, List
from uuid import uuid4
import time

from pyniryo.nate.components import BaseAPIComponent
from .. import models
from .._internal import transport_models, paths_gen, topics
from .._internal.mqtt import MqttClient

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
        return topics.Robot.MOVE_FEEDBACK.format(cmd_id=self.__command_id)

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
        joints = self._http_client.get(paths_gen.Robot.JOINTS, transport_models.Joints)
        return models.Joints.from_transport_model(joints)

    def on_joints_received(self, callback: JointsCallback) -> None:
        """
        Set the callback to call when the robot's joints are received.

        :param callback: The callback to call. The callback must take the topic and the joints as parameters.
        """

        def internal_callback(_, joints: transport_models.Joints) -> None:
            callback(models.Joints.from_transport_model(joints))

        self._mqtt_client.subscribe(topics.Robot.JOINTS, internal_callback, transport_models.Joints)

    def move(self,
             target: models.MoveTarget,
             frame_id: str = None,
             reference_frame: str = None,
             planner: models.Planner = None) -> MoveCommand:
        """
        Move the robot to the specified joint positions.

        :param target: The target to reach
        :param frame_id: Move linear only. The frame ID to use for the target.
        :param reference_frame: The reference frame to use for the movement. If not specified, the robot's base frame will be used.
        :param planner: The motion planner to use for generating the movement trajectory.
        :return: A MoveCommand object to track the progress of the movement.
        """
        command_id = uuid4()
        move_command = MoveCommand(self._mqtt_client, str(command_id))

        if isinstance(target, models.Joints):
            uri = paths_gen.Robot.JOINTS
            planner = planner or models.Planner.PTP
            data = transport_models.MoveJoints(command_id=command_id,
                                               joints=target.to_transport_model(),
                                               planner=planner.to_transport_model())
        elif isinstance(target, models.Pose):
            if frame_id is None or frame_id == '':
                raise ValueError("frame_id must be specified when moving to a Pose target")
            uri = paths_gen.Robot.FRAME_POSE.format(frame_id=frame_id)
            data = transport_models.MoveFrame(command_id=command_id,
                                              pose=target.to_transport_model(),
                                              reference_frame=reference_frame,
                                              planner=planner)
        elif isinstance(target, list) and all(isinstance(w, models.Waypoint) for w in target):
            uri = paths_gen.Robot.WAYPOINTS
            data = transport_models.MoveWaypoints(command_id=command_id,
                                                  waypoints=[w.to_transport_model() for w in target])
        else:
            valid_types = ', '.join(f'{m.__module__}.{m.__qualname__}' for m in models.MoveTarget.__args__)
            raise TypeError(f'Invalid type {target.__class__.__name__} for target. Expected one of {valid_types}')

        self._http_client.post(uri, data, transport_models.FeedbackResponse)
        return move_command

    def get_all_frame_ids(self) -> List[str]:
        """
        Get all frames defined in the robot.

        :return: A list of Frame objects.
        """
        frames = self._http_client.get(paths_gen.Robot.FRAMES, transport_models.FrameIdList)
        return frames.root
