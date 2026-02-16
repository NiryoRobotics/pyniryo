import contextlib
import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Callable, List, Any, Generator
from uuid import uuid4
import time

from .. import models
from .._internal import transport_models, paths_gen, topics_gen
from .._internal.mqtt import MqttClient
from ..models import Pose, Waypoint

from . import BaseAPIComponent

logger = logging.getLogger(__name__)

JointsCallback = Callable[[models.Joints], None]
PoseCallback = Callable[[models.Pose], None]


class MoveCommand:

    def __init__(self, mqtt_client: MqttClient, command_id: str):
        self.__mqtt_client: MqttClient = mqtt_client
        self.__command_id: str = command_id

        self.__mqtt_client.subscribe(self.topic, self.__move_feedback_callback, transport_models.a.MoveFeedback)
        self.__feedbacks: List[models.MoveFeedback] = [models.MoveFeedback(state=models.MoveState.UNKNOWN, message="")]

    def __move_feedback_callback(self, _topic: str, payload: transport_models.a.MoveFeedback) -> None:
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
        joints = self._http_client.get(paths_gen.Robot.GET_ROBOT_JOINTS, transport_models.s.Joints)
        return models.Joints.from_transport_model(joints)

    def on_joints(self, callback: JointsCallback) -> None:
        """
        Set the callback to call when the robot's joints are received.

        :param callback: The callback to call. The callback must take the topic and the joints as parameters.
        """

        def internal_callback(_, joints: transport_models.a.Joints) -> None:
            callback(models.Joints.from_a_transport_model(joints))

        self._mqtt_client.subscribe(topics_gen.Robot.JOINTS, internal_callback, transport_models.a.Joints)

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
            transport_models.s.Pose,
        )
        return models.Pose.from_transport_model(pose)

    def on_frame_pose(self, frame_id: str, callback: PoseCallback) -> None:
        """
        Set a callback to be called when the pose of a specific frame is received.

        :param frame_id: The ID of the frame to subscribe to.
        :param callback: The callback to call. The callback must take the topic and the pose as parameters.
        """

        def internal_callback(_, pose: transport_models.a.Pose) -> None:
            callback(models.Pose.from_transport_model(pose))

        self._mqtt_client.subscribe(
            topics_gen.Robot.FRAME_POSE.format(frame_id=frame_id),
            internal_callback,
            transport_models.a.Pose,
        )

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

    def move(self, target: models.MoveTarget, add_start: bool = False) -> MoveCommand:
        """
        Move the robot according to the provided target. Note that if a joints and pose are provided in the same
        waypoint, the robot will prioritize the joints target and ignore the pose target.

        :param target: The target to reach
        :param add_start: Whether to add the current robot position as the first waypoint.
        :return: A MoveCommand object to track the progress of the movement.
        """
        command_id = uuid4()
        move_command = MoveCommand(self._mqtt_client, str(command_id))

        target = self._normalize_move_target(target)
        self._http_client.post(
            paths_gen.Robot.MOVE_ALONG_WAYPOINTS,
            transport_models.s.FeedbackResponse,
            transport_models.s.MoveWaypoints(command_id=command_id,
                                             add_start=add_start,
                                             waypoints=[w.to_transport_model() for w in target]),
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
            transport_models.s.FeedbackResponse,
            transport_models.s.TrajectoryExecution(command_id=command_id, trajectory=trajectory.to_transport_model()),
        )
        return move_command

    def get_urdf(self) -> ET.Element:
        buffer = BytesIO()
        self._http_client.download(paths_gen.Robot.GET_ROBOT_URDF, buffer)
        buffer.seek(0)
        tree = ET.parse(buffer)
        return tree.getroot()

    def get_configuration(self) -> models.RobotConfiguration:
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONFIG, transport_models.s.RobotConfig)
        return models.RobotConfiguration.from_transport_model(resp)

    def get_control_mode(self) -> models.ControlMode:
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONTROL_MODE, transport_models.s.ControlMode)
        return models.ControlMode.from_transport_model(resp)

    def set_control_mode(self, mode: models.ControlMode) -> None:
        resp = self._http_client.put(paths_gen.Robot.SET_ROBOT_CONTROL_MODE,
                                     transport_models.s.ControlMode,
                                     mode.to_transport_model())
        if resp.mode.value != mode.value:
            raise RuntimeError(f'Failed to set control mode to {mode}. Current mode is {resp.mode}')

    @contextlib.contextmanager
    def jog_mode(self) -> Generator[None, Any, None]:
        """
        Context manager to temporarily set the robot in jog mode. The robot will be set back to its previous control
        mode when exiting the context.

        Usage:
        ```
        with robot.jog_mode():
            # Do something in jog mode
            ...
        # Back to previous control mode
        ```
        """
        previous_mode = self.get_control_mode()
        self.set_control_mode(models.ControlMode.JOG)
        try:
            yield
        finally:
            self.set_control_mode(previous_mode)

    def stop_jog(self) -> None:
        """
        Stop the current jog command. The robot must be in jog mode for this to work.
        """
        self._mqtt_client.publish(topics_gen.Cmd.ROBOT_JOG_STOP, transport_models.EmptyPayload())

    def jog_joints(self, target: models.Joints) -> None:
        """
        Send a jog command to the robot with the specified joint speed. The robot must be in jog mode for this to
        work.

        :param target: The target joints speed for the jog command.
        """
        self._mqtt_client.publish(topics_gen.Cmd.ROBOT_JOG_JOINT, transport_models.a.JogJoint(velocities=target.data))

    def jog_cartesian(self, linear_velocity: list[float], angular_velocity: list[float], frame_id: str = None) -> None:
        """
        Send a jog command to the robot with the specified Cartesian speed. The robot must be in jog mode for this to
        work.
        :param linear_velocity: The linear velocity of the jog command in m/s. It should be a list of 3 floats representing the velocity in the x, y and z directions.
        :param angular_velocity: The angular velocity of the jog command in rad/s. It should be a list of 3 floats representing the angular velocity around the x, y and z axes.
        :param frame_id: The reference frame for the velocities (e.g., "tcp", "base_link", "world"). If not specified, the velocities will be applied in the robot's default frame.
        """
        self._mqtt_client.publish(
            topics_gen.Cmd.ROBOT_JOG_CARTESIAN,
            transport_models.a.JogCartesian(linear=linear_velocity, angular=angular_velocity, frame_id=frame_id))

    def executor_status(self) -> models.ExecutorStatus:
        """ Get the current status of the program executor. :return: The current status of the program executor. """
        status = self._http_client.get(paths_gen.Robot.GET_TRAJECTORY_EXECUTOR_STATUS,
                                       transport_models.s.TrajectoryExecutorStatus)
        return models.ExecutorStatus.from_transport_model(status.status)

    def _update_executor_status(self, status: transport_models.s.ExecutorStatus) -> None:
        self._http_client.patch(paths_gen.Robot.UPDATE_TRAJECTORY_EXECUTOR_STATUS,
                                transport_models.EmptyPayload,
                                transport_models.s.TrajectoryExecutorStatus(status=status))

    def pause(self) -> None:
        self._update_executor_status(transport_models.s.ExecutorStatus.PAUSED)

    def stop(self) -> None:
        self._update_executor_status(transport_models.s.ExecutorStatus.STOPPED)

    def resume(self) -> None:
        self._update_executor_status(transport_models.s.ExecutorStatus.RUNNING)
