from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import overload, Literal

from .._internal import transport_models


@overload
def get_mtype(_type: type, a: Literal[False]) -> transport_models.s.MType:
    ...


@overload
def get_mtype(_type: type, a: Literal[True]) -> transport_models.a.MType:
    ...


@overload
def get_mtype(_type: type, a: bool = False) -> transport_models.s.MType | transport_models.a.MType:
    ...


def get_mtype(_type: type, a: bool = False) -> transport_models.s.MType | transport_models.a.MType:
    """
    Get the MType corresponding to a Python type for metrics.
    
    :param _type: The Python type.
    :param a: Whether to return the asynchronous MType variant.
    :return: The corresponding MType enum value.
    :raises TypeError: If the type is not supported for metrics.
    """
    tr_enum = transport_models.a.MType if a else transport_models.s.MType
    if _type is str:
        return tr_enum.STRING
    elif _type is int:
        return tr_enum.INT
    elif _type is float:
        return tr_enum.FLOAT
    elif _type is bool:
        return tr_enum.BOOL
    elif _type is datetime:
        return tr_enum.DATETIME
    elif _type is timedelta:
        return tr_enum.DURATION
    else:
        raise TypeError(f"Unsupported metric type: {_type}")


def parse_mtype(mtype: transport_models.s.MType | transport_models.a.MType) -> type:
    """
    Parse an MType to get the corresponding Python type.

    :param mtype: The MType enum value.
    :return: The corresponding Python type.
    :raises TypeError: If the MType is not recognized.
    """
    tr_enum = transport_models.a.MType if isinstance(mtype, transport_models.a.MType) else transport_models.s.MType
    if mtype is tr_enum.STRING:
        return str
    elif mtype is tr_enum.INT:
        return int
    elif mtype is tr_enum.FLOAT:
        return float
    elif mtype is tr_enum.BOOL:
        return bool
    elif mtype is tr_enum.DATETIME:
        return datetime
    elif mtype is tr_enum.DURATION:
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
    def from_transport_model(cls,
                             tr_metric: transport_models.s.CustomMetric | transport_models.a.CustomMetric) -> 'Metric':
        return cls(name=tr_metric.name, value=tr_metric.value, type=parse_mtype(tr_metric.m_type))

    def to_transport_model(self, a: bool = False) -> transport_models.s.CustomMetric | transport_models.a.CustomMetric:
        metric_class = transport_models.a.CustomMetric if a else transport_models.s.CustomMetric
        return metric_class(name=self.name, value=self.value, m_type=get_mtype(self.type, a=a))
