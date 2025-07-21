from typing import Callable, List
from uuid import UUID, uuid4
import time
import datetime

from pyniryo.nate.components import BaseAPIComponent
from .. import models
from .._internal import transport_models, paths_gen, topics
from .._internal.mqtt import MqttClient

JointsCallback = Callable[[models.Joints], None]


class MoveCommand:

    def __init__(self, mqtt_client: MqttClient, command_id: UUID):
        self.__mqtt_client: MqttClient = mqtt_client
        self.__command_id: UUID = command_id

        self.__mqtt_client.subscribe(self.topic, self.__move_feedback_callback, transport_models.MoveFeedback)
        self.__feedbacks: List[models.MoveFeedback] = [models.MoveFeedback(state=models.MoveState.UNKNOWN, message="")]

    def __move_feedback_callback(self, _topic: str, payload: transport_models.MoveFeedback) -> None:
        """
        Internal callback to handle move feedback messages.
        """
        self.__feedbacks.append(models.MoveFeedback.from_transport_model(payload))

        if self.state.is_final():
            self.__mqtt_client.unsubscribe(self.topic)

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
            if start + timeout > time.monotonic():
                raise TimeoutError(f'Move command {self.__command_id} timed out after {timeout} seconds.')
            time.sleep(0.1)
        if self.state.is_error():
            raise RuntimeError(f'Move command {self.__command_id} failed with error: {self.__feedbacks[-1].message}')
        print(f'Move command {self.__command_id} completed with state: {self.state}')


class Motion(BaseAPIComponent):

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

    def move(self, target: models.MoveTarget, desired_time: float | None = None) -> MoveCommand:
        """
        Move the robot to the specified joint positions.

        :param target: The target to reach
        :param desired_time: The desired time to reach the target, in seconds. If not specified, the robot will move as fast as possible.
        """
        if isinstance(target, models.Joints):
            command_id = uuid4()
            move_command = MoveCommand(self._mqtt_client, command_id)
            self._http_client.post(
                paths_gen.Robot.JOINTS,
                transport_models.MoveJoints(command_id=command_id,
                                            joints=target.to_transport_model(),
                                            desired_time=desired_time),
                transport_models.MoveResponse)
            return move_command
        else:
            valid_types = ', '.join(f'{m.__module__}.{m.__qualname__}' for m in models.MoveTarget.__args__)
            raise TypeError(f'Invalid type {target.__class__.__name__} for target. Expected on of {valid_types}')
