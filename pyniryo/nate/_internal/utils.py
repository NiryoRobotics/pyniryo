from typing import TypeVar

from pydantic import BaseModel, ValidationError

from pyniryo.nate.exceptions import DataValidationError

T = TypeVar("T", bound=BaseModel)


def new_transport_model(d: dict, transport_model: type[T]) -> T:
    """
    Create a new transport model from a dictionary.
    :param d: The dictionary to convert.
    :param transport_model: The transport model to use.
    :return: The transport model.
    :raises DataValidationError: If the data is not valid.
    """
    try:
        return transport_model(**d)
    except ValidationError as e:
        error_msgs = []
        for error in e.errors():
            error_msgs.append(f'Error for field {error["loc"][0]}={repr(error["input"])}: {error["msg"]}')
        raise DataValidationError(', '.join(error_msgs)) from e