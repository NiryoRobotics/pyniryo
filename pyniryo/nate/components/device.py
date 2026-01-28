from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models


class Device(BaseAPIComponent):
    """
    Device component for the API.
    """

    def id(self) -> str:
        """
        Get the device ID of the robot.
        :return: The device ID of the robot.
        """
        resp = self._http_client.get(paths_gen.Device.GET_DEVICE_ID, transport_models.DeviceID)
        return resp.device_id
