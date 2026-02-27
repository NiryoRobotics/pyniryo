from dataclasses import dataclass
from strenum import StrEnum

from .._internal import transport_models


class IoId(StrEnum):
    TDI1 = 'tdi1'
    TDI2 = 'tdi2'
    TDO1 = 'tdo1'
    TDO2 = 'tdo2'
    TAI1 = 'tai1'
    TAI2 = 'tai2'


@dataclass
class DigitalIO:
    id: IoId
    value: bool

    @classmethod
    def from_transport_model(cls, model: transport_models.s.DigitalIO | transport_models.a.DigitalIO) -> 'DigitalIO':
        return cls(id=IoId(model.id), value=model.value == transport_models.s.Value.HIGH)

    def to_transport_model(self) -> transport_models.s.DigitalIO:
        return transport_models.s.DigitalIO(
            id=self.id, value=transport_models.s.Value.HIGH if self.value else transport_models.s.Value.LOW)


@dataclass
class AnalogIO:
    id: IoId
    value: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.AnalogIO | transport_models.a.AnalogIO) -> 'AnalogIO':
        return cls(id=IoId(model.id), value=model.value == transport_models.s.Value.HIGH)

    def to_transport_model(self) -> transport_models.s.AnalogIO:
        return transport_models.s.AnalogIO(id=self.id, value=self.value)


@dataclass
class IOStates:
    digital_inputs: dict[IoId, DigitalIO]
    digital_outputs: dict[IoId, DigitalIO]
    analog_inputs: dict[IoId, AnalogIO]
    analog_outputs: dict[IoId, AnalogIO]

    @classmethod
    def from_transport_model(cls, model: transport_models.s.IOStates) -> 'IOStates':
        return cls(
            digital_inputs={IoId(io.id): DigitalIO.from_transport_model(io)
                            for io in model.digital_inputs},
            digital_outputs={IoId(io.id): DigitalIO.from_transport_model(io)
                             for io in model.digital_outputs},
            analog_inputs={IoId(io.id): AnalogIO.from_transport_model(io)
                           for io in model.analog_inputs},
            analog_outputs={IoId(io.id): AnalogIO.from_transport_model(io)
                            for io in model.analog_outputs},
        )

    def to_transport_model(self) -> transport_models.s.IOStates:
        return transport_models.s.IOStates(
            digital_inputs=[io.to_transport_model() for io in self.digital_inputs.values()],
            digital_outputs=[io.to_transport_model() for io in self.digital_outputs.values()],
            analog_inputs=[io.to_transport_model() for io in self.analog_inputs.values()],
            analog_outputs=[io.to_transport_model() for io in self.analog_outputs.values()],
        )


AnyIO = DigitalIO | AnalogIO
