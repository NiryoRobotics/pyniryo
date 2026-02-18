from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models
from ..exceptions import PyNiryoError


class Device(BaseAPIComponent):
    """
    Device component for accessing robot device information and control.
    
    This component provides methods for:
    - Getting device ID
    - Checking device health and readiness
    - Rebooting or shutting down the device
    
    Example:
        >>> from pyniryo.nate import Nate
        >>> 
        >>> nate = Nate()
        >>> 
        >>> # Check device status
        >>> device_id = nate.device.id()
        >>> print(f"Device ID: {device_id}")
        >>> 
        >>> if nate.device.is_healthy():
        ...     print("Device is healthy")
        >>> 
        >>> if nate.device.is_ready():
        ...     print("Device is ready for operations")
    """

    def id(self) -> str:
        """
        Get the device ID of the robot.
        :return: The device ID of the robot.
        """
        resp = self._http_client.get(paths_gen.Device.GET_DEVICE_ID, transport_models.s.DeviceID)
        return resp.device_id

    def is_healthy(self) -> bool:
        """
        Check if the robot device is healthy.
        
        :return: True if the robot is healthy, False otherwise.
        
        Example:
            >>> if device.is_healthy():
            ...     print("Robot is operational")
            ... else:
            ...     print("Robot has health issues")
        """
        try:
            self._http_client.get(paths_gen.Device.HEALTH_CHECK, transport_models.HealthCheckResponse)
        except PyNiryoError:
            return False
        return True

    def is_ready(self) -> bool:
        """
        Check if the robot is ready to accept commands.
        
        :return: True if the robot is ready, False otherwise.
        
        Example:
            >>> if device.is_ready():
            ...     # Start robot operations
            ...     cmd = robot.move(Joints(0, 0, 0, 0, 0, 0))
        """
        resp = self._http_client.get(paths_gen.Device.READINESS_CHECK, transport_models.ReadinessCheckResponse)
        return resp.ready

    def reboot(self) -> None:
        """
        Reboot the robot device.
        
        Note: The connection will be lost during the reboot process.
        
        Example:
            >>> device.reboot()
            >>> # Wait for the device to restart before reconnecting
        """
        self._http_client.post(paths_gen.Device.REBOOT,
                               transport_models.EmptyPayload,
                               transport_models.EmptyPayload())

    def shutdown(self) -> None:
        """
        Shutdown the robot device.
        
        Note: The device will need to be manually powered on after shutdown.
        
        Example:
            >>> # Safely shutdown the device
            >>> device.shutdown()
        """
        self._http_client.post(paths_gen.Device.SHUTDOWN,
                               transport_models.EmptyPayload,
                               transport_models.EmptyPayload())
