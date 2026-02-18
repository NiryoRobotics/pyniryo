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
    """
    Represents a move command and tracks its execution progress.
    
    This class monitors the state of a robot movement operation, receiving feedback
    through MQTT and allowing you to wait for completion.
    
    Example:
        >>> cmd = robot.move(Joints(0, 0, 0, 0, 0, 0))
        >>> cmd.wait()  # Block until movement is complete
        >>> print(cmd.state)  # Check final state
    """

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
    """
    Robot component for controlling robot movements and accessing robot state.
    
    This component provides methods for:
    - Getting and monitoring joint positions
    - Moving the robot using joints, poses, waypoints, or trajectories
    - Managing frames and coordinate systems
    - Controlling robot execution (pause, resume, stop)
    - Jogging in manual mode
    
    Example:
        >>> from pyniryo.nate import Nate
        >>> from pyniryo.nate.models import Joints, Pose, Point, Quaternion
        >>> 
        >>> nate = Nate()
        >>> 
        >>> # Move to joint position
        >>> cmd = nate.robot.move(Joints(0, -1.57, 1.57, 0, 0, 0))
        >>> cmd.wait()
        >>> 
        >>> # Move to Cartesian pose
        >>> pose = Pose(Point(0.3, 0, 0.4), Quaternion(0, 1, 0, 0))
        >>> cmd = nate.robot.move(pose)
        >>> cmd.wait()
    """

    def get_joints(self) -> models.Joints:
        """
        Get the current joint positions of the robot.

        :return: The current joint positions as a Joints object.
        """
        joints = self._http_client.get(paths_gen.Robot.GET_ROBOT_JOINTS, transport_models.s.Joints)
        return models.Joints.from_transport_model(joints)

    def on_joints(self, callback: JointsCallback) -> None:
        """
        Set the callback to call when the robot's joint positions are received.

        :param callback: The callback function that takes a Joints parameter.
        
        Example:
            >>> def joints_callback(joints):
            ...     print(f"Current joints: {joints.data}")
            >>> 
            >>> robot.on_joints(joints_callback)
        """

        def internal_callback(_, joints: transport_models.a.Joints) -> None:
            callback(models.Joints.from_a_transport_model(joints))

        self._mqtt_client.subscribe(topics_gen.Robot.JOINTS, internal_callback, transport_models.a.Joints)

    def get_all_frames(self) -> List[str]:
        """
        Get all frames defined in the robot.

        :return: A list of frame IDs.
        
        Example:
            >>> frames = robot.get_all_frames()
            >>> print(f"Available frames: {frames}")
        """
        frames = self._http_client.get(
            paths_gen.Robot.GET_ALL_FRAMES,
            transport_models.FrameIdList,
        )
        return frames.root

    def get_frame_pose(self, frame_id: str) -> Pose:
        """
        Get the current pose of a specific frame.

        :param frame_id: The ID of the frame to retrieve.
        :return: The current pose of the frame as a Pose object.
        
        Example:
            >>> pose = robot.get_frame_pose("tool0")
            >>> print(f"Tool position: x={pose.position.x}, y={pose.position.y}, z={pose.position.z}")
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
        :param callback: The callback function that takes a Pose parameter.
        
        Example:
            >>> def pose_callback(pose):
            ...     print(f"Tool pose: {pose.position.x}, {pose.position.y}, {pose.position.z}")
            >>> 
            >>> robot.on_frame_pose("tool0", pose_callback)
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

        :param target: The target to reach. Can be Joints, Pose, Waypoint, or Waypoints.
        :param add_start: Whether to add the current robot position as the first waypoint.
        :return: A MoveCommand object to track the progress of the movement.
        
        Example:
            >>> # Move using joint positions
            >>> from pyniryo.nate.models import Joints
            >>> cmd = robot.move(Joints(0, -1.57, 1.57, 0, 0, 0))
            >>> cmd.wait()
            >>> 
            >>> # Move using Cartesian pose
            >>> from pyniryo.nate.models import Pose, Point, EulerAngles
            >>> import math
            >>> pose = Pose(Point(0.3, 0, 0.4), EulerAngles(0, math.pi, 0))
            >>> cmd = robot.move(pose)
            >>> cmd.wait()
            >>> 
            >>> # Move through multiple waypoints
            >>> from pyniryo.nate.models import Waypoint, Waypoints, Planner
            >>> waypoints = Waypoints([
            ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
            ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0), planner=Planner.LIN)
            ... ])
            >>> cmd = robot.move(waypoints)
            >>> cmd.wait()
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
        Execute a pre-computed trajectory on the robot.

        :param trajectory: The trajectory to execute.
        :return: A MoveCommand object to track the progress of the movement.
        
        Example:
            >>> # Generate and execute a trajectory
            >>> from pyniryo.nate.models import Waypoint, Waypoints, Joints
            >>> waypoints = Waypoints([
            ...     Waypoint(joints=Joints(0, 0, 0, 0, 0, 0)),
            ...     Waypoint(joints=Joints(1, -1, 1, 0, 0, 0))
            ... ])
            >>> trajectory = nate.motion_planner.generate_trajectory(waypoints)
            >>> cmd = robot.execute_trajectory(trajectory)
            >>> cmd.wait()
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
        """
        Get the robot's URDF (Unified Robot Description Format) description.
        
        :return: The root XML element of the URDF document.
        """
        buffer = BytesIO()
        self._http_client.download(paths_gen.Robot.GET_ROBOT_URDF, buffer)
        buffer.seek(0)
        tree = ET.parse(buffer)
        return tree.getroot()

    def get_configuration(self) -> models.RobotConfiguration:
        """
        Get the robot's configuration including joint limits and PID parameters.
        
        :return: The robot configuration.
        
        Example:
            >>> config = robot.get_configuration()
            >>> print(f"Robot: {config.name}, Joints: {config.n_joint}")
            >>> for joint in config.joints:
            ...     print(f"{joint.name}: limits [{joint.position_limit_min}, {joint.position_limit_max}]")
        """
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONFIG, transport_models.s.RobotConfig)
        return models.RobotConfiguration.from_transport_model(resp)

    def get_control_mode(self) -> models.ControlMode:
        """
        Get the current control mode of the robot.
        
        :return: The current control mode (TRAJECTORY, JOG, or SPEED).
        """
        resp = self._http_client.get(paths_gen.Robot.GET_ROBOT_CONTROL_MODE, transport_models.s.ControlMode)
        return models.ControlMode.from_transport_model(resp)

    def set_control_mode(self, mode: models.ControlMode) -> None:
        """
        Set the control mode of the robot.
        
        :param mode: The control mode to set (TRAJECTORY, JOG, or SPEED).
        :raises RuntimeError: If the mode could not be set.
        
        Example:
            >>> from pyniryo.nate.models import ControlMode
            >>> robot.set_control_mode(ControlMode.JOG)
        """
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
        Send a jog command to the robot with the specified joint velocities. The robot must be in jog mode for this to
        work.

        :param target: The target joint velocities for the jog command (in rad/s).
        
        Example:
            >>> from pyniryo.nate.models import Joints, ControlMode
            >>> robot.set_control_mode(ControlMode.JOG)
            >>> robot.jog_joints(Joints(0.1, 0, 0, 0, 0, 0))  # Jog first joint
            >>> # ... do something ...
            >>> robot.stop_jog()
        """
        self._mqtt_client.publish(topics_gen.Cmd.ROBOT_JOG_JOINT, transport_models.a.JogJoint(velocities=target.data))

    def jog_cartesian(self, linear_velocity: list[float], angular_velocity: list[float], frame_id: str = None) -> None:
        """
        Send a jog command to the robot with the specified Cartesian velocities. The robot must be in jog mode for this to
        work.
        
        :param linear_velocity: The linear velocity of the jog command in m/s. It should be a list of 3 floats representing the velocity in the x, y and z directions.
        :param angular_velocity: The angular velocity of the jog command in rad/s. It should be a list of 3 floats representing the angular velocity around the x, y and z axes.
        :param frame_id: The reference frame for the velocities (e.g., "tcp", "base_link", "world"). If not specified, the velocities will be applied in the robot's default frame.
        
        Example:
            >>> from pyniryo.nate.models import ControlMode
            >>> robot.set_control_mode(ControlMode.JOG)
            >>> # Move in +Z direction at 0.05 m/s
            >>> robot.jog_cartesian([0, 0, 0.05], [0, 0, 0], frame_id="base_link")
            >>> # ... do something ...
            >>> robot.stop_jog()
        """
        self._mqtt_client.publish(
            topics_gen.Cmd.ROBOT_JOG_CARTESIAN,
            transport_models.a.JogCartesian(linear=linear_velocity, angular=angular_velocity, frame_id=frame_id))

    def executor_status(self) -> models.ExecutorStatus:
        """
        Get the current status of the trajectory executor.
        
        :return: The current status of the trajectory executor.
        """
        status = self._http_client.get(paths_gen.Robot.GET_TRAJECTORY_EXECUTOR_STATUS,
                                       transport_models.s.TrajectoryExecutorStatus)
        return models.ExecutorStatus.from_transport_model(status.status)

    def _update_executor_status(self, status: transport_models.s.ExecutorStatus) -> None:
        self._http_client.patch(paths_gen.Robot.UPDATE_TRAJECTORY_EXECUTOR_STATUS,
                                transport_models.EmptyPayload,
                                transport_models.s.TrajectoryExecutorStatus(status=status))

    def pause(self) -> None:
        """
        Pause the current trajectory execution.
        
        Example:
            >>> cmd = robot.move(Joints(1, -1, 1, 0, 0, 0))
            >>> # Pause after starting
            >>> robot.pause()
            >>> # Resume later
            >>> robot.resume()
            >>> cmd.wait()
        """
        self._update_executor_status(transport_models.s.ExecutorStatus.PAUSED)

    def stop(self) -> None:
        """
        Stop the current trajectory execution.
        """
        self._update_executor_status(transport_models.s.ExecutorStatus.STOPPED)

    def resume(self) -> None:
        """
        Resume a paused trajectory execution.
        """
        self._update_executor_status(transport_models.s.ExecutorStatus.RUNNING)
