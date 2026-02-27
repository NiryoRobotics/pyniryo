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
        """
        resp = self._http_client.get(paths_gen.Device.READINESS_CHECK, transport_models.ReadinessCheckResponse)
        return resp.ready

    def reboot(self) -> None:
        """
        Reboot the robot device.
        
        Note: The connection will be lost during the reboot process.
        """
        self._http_client.post(paths_gen.Device.REBOOT,
                               transport_models.EmptyPayload,
                               transport_models.EmptyPayload())

    def shutdown(self) -> None:
        """
        Shutdown the robot device.
        
        Note: The device will need to be manually powered on after shutdown.
        """
        self._http_client.post(paths_gen.Device.SHUTDOWN,
                               transport_models.EmptyPayload,
                               transport_models.EmptyPayload())
