import logging
import os
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable, Type, TypeVar

from .components import Auth, Users, Robot, Device, Programs, MotionPlanner, Metrics, BaseAPIComponent
from ._internal import paths_gen, transport_models
from ._internal.http import HttpClient
from ._internal.mqtt import MqttClient
from ._internal.const import DEFAULT_HTTP_PORT, DEFAULT_MQTT_PORT, MQTT_PREFIX

logger = logging.getLogger(__name__)

_T = TypeVar("_T", bound=str | int | float | bool)
_C = TypeVar("_C", bound=BaseAPIComponent)


def _fetch_from_env(key: str, _type: Type[_T], default: _T) -> _T:
    value = os.getenv(key)

    if value is None:
        return default

    try:
        if _type is bool:
            return _type(value.lower() in ['true', '1', 'yes'])
        elif _type in [int, float, str]:
            return _type(value)
        else:
            raise TypeError(f'Unsupported type {_type}')

    except Exception as e:
        raise ValueError(f'Error converting environment variable {key} to type {_type}: {e}') from e


class Nate:
    """
    Main client class to interact with the Nate API. It provides access to all the components of the API,
    such as authentication, users, robot control, device information, and program management.
    """

    auth: Auth
    users: Users
    robot: Robot
    device: Device
    programs: Programs
    motion_planner: MotionPlanner
    metrics: Metrics

    def __init__(self, hostname: str | None = None, login: tuple[str, str] = None):
        """
        Initialize a client to communicate with the Nate API.
        
        :param hostname: The hostname of the Nate API. It can be an IP address or a domain name.
            If None, retrieve it from the environment variable NATE_HOSTNAME. If the environment variable is not set, use localhost.
        :type hostname: str
        :param login: A tuple containing the username and password to use for authentication. Omitted if using an auth token.
            If None, retrieve them from the environment variables NATE_USERNAME and NATE_PASSWORD.
        """
        hostname = hostname or os.getenv('NATE_HOSTNAME') or 'localhost'
        login = login or (os.getenv('NATE_USERNAME'), os.getenv('NATE_PASSWORD'))

        # Advanced options, not exposed in the constructor.
        http_port = _fetch_from_env('NATE_HTTP_PORT', int, DEFAULT_HTTP_PORT)
        mqtt_port = _fetch_from_env('NATE_MQTT_PORT', int, DEFAULT_MQTT_PORT)
        insecure = _fetch_from_env('NATE_INSECURE', bool, False)
        use_http = _fetch_from_env('NATE_USE_HTTP', bool, False)
        execution_token = _fetch_from_env('NATE_EXECUTION_TOKEN', str, '')
        token_validity_str = _fetch_from_env('NATE_TOKEN_VALIDITY', str, "1d")

        if token_validity_str.endswith('d'):
            token_validity = timedelta(days=float(token_validity_str[:-1]))
        elif token_validity_str.endswith('h'):
            token_validity = timedelta(hours=float(token_validity_str[:-1]))
        elif token_validity_str.endswith('s'):
            token_validity = timedelta(seconds=float(token_validity_str[:-1]))
        else:
            raise ValueError(f'Unsupported token validity type {token_validity_str}.')

        self._correlation_id = _fetch_from_env('NATE_CORRELATION_ID', str, uuid.uuid4().hex)

        ##########################################################################################
        ## Bootstrap: fetch all needed data to properly initiate the client and its components. ##
        ##########################################################################################

        self._http_client = HttpClient(hostname, http_port, insecure=insecure, use_http=use_http)
        if execution_token is not None:
            self._http_client.set_header('Execution-Token', execution_token)

        # Token
        if len(login) != 2 or None in login:
            raise ValueError("authentication with username and password requires both username and password")
        username, password = login

        def token_provider(validity: timedelta) -> transport_models.s.Token:
            return self._http_client.post(
                paths_gen.Authentication.LOGIN,
                transport_models.s.Token,
                transport_models.s.Login(login=username,
                                         password=password,
                                         expires_at=datetime.now(timezone.utc) + validity))

        token = token_provider(token_validity)

        self._http_client.set_token(token.token)

        # Device ID
        resp = self._http_client.get(paths_gen.Device.GET_DEVICE_ID, transport_models.s.DeviceID)
        device_id = resp.device_id

        self._mqtt_client: MqttClient = MqttClient(hostname, mqtt_port, prefix=MQTT_PREFIX(device_id))
        self._mqtt_client.set_token(token.token)

        self._token_renewer = TokenRenewer(
            token_provider,
            [self._http_client.set_token, self._mqtt_client.set_token],
            token_validity,
        )
        self._token_renewer.start()

        self.auth = Auth(self._http_client, self._mqtt_client, self._correlation_id)
        self.users = Users(self._http_client, self._mqtt_client, self._correlation_id)
        self.robot = Robot(self._http_client, self._mqtt_client, self._correlation_id)
        self.device = Device(self._http_client, self._mqtt_client, self._correlation_id)
        self.programs = Programs(self._http_client, self._mqtt_client, self._correlation_id)
        self.motion_planner = MotionPlanner(self._http_client, self._mqtt_client, self._correlation_id)
        self.metrics = Metrics(self._http_client, self._mqtt_client, self._correlation_id)

    def close(self):
        """
        Clean up resources used by the client, and ensure that any background tasks are properly terminated.
        After calling this method, the client should not be used anymore.
        """

        self.auth.close()
        self.users.close()
        self.robot.close()
        self.device.close()
        self.programs.close()
        self.metrics.close()

        self._token_renewer.stop()
        self._mqtt_client.disconnect()
        self._http_client.disconnect()


class TokenRenewer:

    def __init__(self,
                 provider: Callable[[timedelta], transport_models.s.Token],
                 setters: list[Callable[[str], None]],
                 renewal_interval: timedelta):
        self._provider = provider
        self._setters = setters
        self._renewal_interval = renewal_interval
        self._timer = None

    def start(self):
        self._setup_timer()

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _setup_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
        interval = self._renewal_interval.total_seconds() * 0.9
        self._timer = threading.Timer(interval, self._run)
        self._timer.daemon = True
        logger.info(f'Next token renewal scheduled in {timedelta(seconds=interval)}.')
        self._timer.start()

    def _run(self):
        token = self._provider(self._renewal_interval)
        for setter in self._setters:
            try:
                setter(token.token)
            except Exception as e:
                print(f'Error renewing token for setter {setter}: {e}')
        self._setup_timer()
