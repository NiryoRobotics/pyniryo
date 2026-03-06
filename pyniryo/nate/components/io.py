import logging
from typing import Callable

from pyniryo.nate.components import BaseAPIComponent

from .._internal import paths_gen, transport_models, topics_gen, mqtt
from ..models import IOStates, DigitalIO, AnalogIO, IOLabel, AnyIO, Unsubscribe

logger = logging.getLogger(__name__)

AnalogIOCallback = Callable[[AnalogIO], None]
DigitalIOCallback = Callable[[DigitalIO], None]


class IO(BaseAPIComponent):

    def get_all(self) -> IOStates:
        """
        Get the current states of all digital and analog inputs and outputs.
        :return:
        """
        t_ios = self._http_client.get(paths_gen.Ios.GET_IO_STATES, transport_models.s.IOStates)
        return IOStates.from_transport_model(t_ios)

    def set_digital_output(self, io_id: IOLabel | str, value: bool) -> None:
        """
        Set the state of a digital output.
        :param io_id: The ID of the digital output to set (e.g., IoId.TDO1, 'tdo2').
        :param value: The value to set (True for HIGH, False for LOW).
        """
        self.update_states([DigitalIO(id=IOLabel(io_id), value=value)])

    def set_analog_output(self, io_id: IOLabel | str, value: float) -> None:
        """
        Set the value of an analog output.
        :param io_id: The ID of the analog output to set (e.g., IoId.TAO1, 'tao2').
        :param value: The value to set (a float).
        """
        self.update_states([AnalogIO(id=IOLabel(io_id), value=value)])

    def update_states(self, outputs: list[AnyIO]) -> None:
        """
        Update the states of multiple digital and analog outputs at once.
        :param outputs: A list of DigitalIO and AnalogIO objects representing the outputs to update.
        """
        req = transport_models.s.IOStates(
            digital_outputs=[i.to_transport_model() for i in outputs if isinstance(i, DigitalIO)],
            analog_outputs=[i.to_transport_model() for i in outputs if isinstance(i, AnalogIO)],
        )
        self._http_client.put(paths_gen.Ios.UPDATE_IO_STATES, transport_models.EmptyPayload, req)

    def on_analog_io(self, io_id: IOLabel | str, callback: AnalogIOCallback) -> Unsubscribe:
        """
        Set a callback to be called when the state of the specified analog IOs changes.
        :param io_id: An IO ID to monitor (e.g., IoId.TAI1).
        :param callback: A function that takes an AnalogIO object as an argument and returns None.
          This function will be called whenever the state of the specified analog IOs changes.
        """

        def internal_callback(_: str, aio: transport_models.a.AnalogIOState) -> None:
            callback(AnalogIO(id=IOLabel(io_id), value=aio.value))

        topic = topics_gen.Io.ANALOG_INPUT_STATE.replace('input', mqtt.Wildcard.SINGLE_LEVEL)
        return self._mqtt_client.subscribe(self._mqtt_client.format(topic, io_id=io_id),
                                           internal_callback,
                                           transport_models.a.AnalogIOState)

    def on_digital_io(self, io_id: IOLabel | str, callback: DigitalIOCallback) -> Unsubscribe:
        """
        Set a callback to be called when the state of the specified digital IOs changes.
        :param io_id: An IO ID to monitor (e.g., IoId.TDI1).
        :param callback: A function that takes a DigitalIO object as an argument and returns None.
          This function will be called whenever the state of the specified digital IOs changes.
        """

        def internal_callback(_: str, aio: transport_models.a.DigitalIOState) -> None:
            callback(DigitalIO(id=IOLabel(io_id), value=aio.value))

        topic = topics_gen.Io.DIGITAL_INPUT_STATE.replace('input', mqtt.Wildcard.SINGLE_LEVEL)
        return self._mqtt_client.subscribe(self._mqtt_client.format(topic, io_id=io_id),
                                           internal_callback,
                                           transport_models.a.DigitalIOState)
