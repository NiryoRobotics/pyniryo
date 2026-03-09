from dataclasses import dataclass
from strenum import StrEnum

from .._internal import transport_models


class IOLabel(StrEnum):
    TDI1 = 'tdi1'
    TDI2 = 'tdi2'
    TDO1 = 'tdo1'
    TDO2 = 'tdo2'
    TAI1 = 'tai1'
    TAI2 = 'tai2'


@dataclass
class DigitalIO:
    id: IOLabel
    value: bool

    @classmethod
    def from_transport_model(cls, model: transport_models.s.DigitalIO) -> 'DigitalIO':
        return cls(id=IOLabel(model.id), value=model.value)

    def to_transport_model(self) -> transport_models.s.DigitalIO:
        return transport_models.s.DigitalIO(id=self.id, value=self.value)


@dataclass
class AnalogIO:
    id: IOLabel
    value: float

    @classmethod
    def from_transport_model(cls, model: transport_models.s.AnalogIO) -> 'AnalogIO':
        return cls(id=IOLabel(model.id), value=model.value)

    def to_transport_model(self) -> transport_models.s.AnalogIO:
        return transport_models.s.AnalogIO(id=self.id, value=self.value)


@dataclass
class IOStates:
    digital_inputs: dict[IOLabel, DigitalIO]
    digital_outputs: dict[IOLabel, DigitalIO]
    analog_inputs: dict[IOLabel, AnalogIO]
    analog_outputs: dict[IOLabel, AnalogIO]

    @classmethod
    def from_transport_model(cls, model: transport_models.s.IOStates) -> 'IOStates':
        return cls(
            digital_inputs={IOLabel(io.id): DigitalIO.from_transport_model(io)
                            for io in model.digital_inputs} if model.digital_inputs is not None else {},
            digital_outputs={IOLabel(io.id): DigitalIO.from_transport_model(io)
                             for io in model.digital_outputs} if model.digital_outputs is not None else {},
            analog_inputs={IOLabel(io.id): AnalogIO.from_transport_model(io)
                           for io in model.analog_inputs} if model.analog_inputs is not None else {},
            analog_outputs={IOLabel(io.id): AnalogIO.from_transport_model(io)
                            for io in model.analog_outputs} if model.analog_outputs is not None else {},
        )

    def to_transport_model(self) -> transport_models.s.IOStates:
        return transport_models.s.IOStates(
            digital_inputs=[io.to_transport_model() for io in self.digital_inputs.values()],
            digital_outputs=[io.to_transport_model() for io in self.digital_outputs.values()],
            analog_inputs=[io.to_transport_model() for io in self.analog_inputs.values()],
            analog_outputs=[io.to_transport_model() for io in self.analog_outputs.values()],
        )


AnyIO = DigitalIO | AnalogIO
