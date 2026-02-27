from dataclasses import dataclass
from datetime import datetime, timedelta

from .._internal import transport_models


def get_mtype(_type: type, a: bool = False) -> transport_models.s.MType:
    """
    Get the MType corresponding to a Python type for metrics.
    
    :param _type: The Python type.
    :param a: Whether to return the asynchronous MType variant.
    :return: The corresponding MType enum value.
    :raises TypeError: If the type is not supported for metrics.
    """
    tr_model = transport_models.a if a else transport_models.s
    if _type is str:
        return tr_model.MType.STRING
    elif _type is int:
        return tr_model.MType.INT
    elif _type is float:
        return tr_model.MType.FLOAT
    elif _type is bool:
        return tr_model.MType.BOOL
    elif _type is datetime:
        return tr_model.MType.DATETIME
    elif _type is timedelta:
        return tr_model.MType.DURATION
    else:
        raise TypeError(f"Unsupported metric type: {_type}")


def parse_mtype(mtype: transport_models.s.MType | transport_models.a.MType) -> type:
    """
    Parse an MType to get the corresponding Python type.
    
    :param mtype: The MType enum value.
    :return: The corresponding Python type.
    :raises TypeError: If the MType is not recognized.
    """
    tr_model = transport_models.a if isinstance(mtype, transport_models.a.MType) else transport_models.s
    if mtype is tr_model.MType.STRING:
        return str
    elif mtype is tr_model.MType.INT:
        return int
    elif mtype is tr_model.MType.FLOAT:
        return float
    elif mtype is tr_model.MType.BOOL:
        return bool
    elif mtype is tr_model.MType.DATETIME:
        return datetime
    elif mtype is tr_model.MType.DURATION:
        return timedelta
    else:
        raise TypeError(f"Unsupported metric type: {mtype}")


@dataclass
class Metric:
    """
    Represents a custom metric.
    
    :param name: The name of the metric.
    :param value: The value of the metric as a string.
    :param type: The Python type of the metric value.
    """
    name: str
    value: str
    type: type

    @classmethod
    def from_transport_model(cls, model: transport_models.a.CustomMetric) -> 'Metric':
        return cls(name=model.name, value=model.value, type=parse_mtype(model.m_type))

    def to_transport_model(self) -> transport_models.a.CustomMetric:
        return transport_models.a.CustomMetric(name=self.name, value=self.value, m_type=get_mtype(self.type, a=True))
