from typing import Any

import requests


class PyNiryoError(Exception):
    pass


class ApiError(PyNiryoError):
    status_code: int
    response: str

    def __init__(self, status_code: int, response: str, *args) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.response = response

    @classmethod
    def from_response(cls, response: requests.Response, *args) -> "ApiError":
        return cls(response.status_code, response.text, *args)


class ClientError(ApiError):
    pass


class ServerError(ApiError):
    pass


class DataValidationError(PyNiryoError):
    pass


class InternalError(PyNiryoError):
    pass


class GenerateTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory generation.
    """


class LoadTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory loading.
    """


class ExecuteTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory execution.
    """


def get_msg_from_errors(errors: list[dict]) -> str:
    """
    Get the error message from pydantic errors list.
    :param errors: The pydantic errors list.
    :return: The error message.
    """
    error_msgs = []
    for error in errors:
        if len(error['loc']) == 0:
            error_msgs.append(error['msg'])
        else:
            error_msgs.append(f'Error for field {error["loc"][0]}={repr(error["input"])}: {error["msg"]}')
    return ', '.join(error_msgs)
