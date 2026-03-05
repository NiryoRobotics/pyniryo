from typing import Any

import requests
from pydantic_core import ErrorDetails


class PyNiryoError(Exception):
    """
    Base exception class for all PyNiryo errors.
    """
    pass


class ApiError(PyNiryoError):
    """
    Exception raised when an API request fails.
    
    :param status_code: The HTTP status code of the response.
    :param response: The response body text.
    :param message: An optional custom error message.
    """
    status_code: int
    response: str

    def __init__(self, status_code: int, response: str, message: str | None = None) -> None:
        self.status_code = status_code
        self.response = response
        if message is None:
            message = f"API error with status code {status_code}: {response}"
        super().__init__(message)

    @classmethod
    def from_response(cls, response: requests.Response, *args: Any) -> "ApiError":
        """
        Create an ApiError from a requests Response object.
        
        :param response: The HTTP response object.
        :return: An ApiError instance.
        """
        return cls(response.status_code, response.text, *args)


class ClientError(ApiError):
    """
    Exception raised when a client error (4xx status code) occurs.
    """
    pass


class ServerError(ApiError):
    """
    Exception raised when a server error (5xx status code) occurs.
    """
    pass


class DataValidationError(PyNiryoError):
    """
    Exception raised when data validation fails.
    """
    pass


class InternalError(PyNiryoError):
    """
    Exception raised when an internal error occurs.
    """
    pass


class GenerateTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory generation.
    
    This exception is raised when the motion planner fails to generate a valid
    trajectory from the provided waypoints, typically due to kinematic constraints,
    unreachable positions, or invalid planner configurations.
    """
    pass


class LoadTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory loading.
    
    This exception is raised when the robot controller fails to load a generated
    trajectory, usually due to invalid trajectory data or controller state issues.
    """
    pass


class ExecuteTrajectoryError(PyNiryoError):
    """
    Exception raised when an error occurs during trajectory execution.
    
    This exception is raised when the robot fails to execute a loaded trajectory,
    which may occur due to hardware faults, safety limits being exceeded, or
    external interruptions during movement.
    """
    pass


def get_msg_from_errors(errors: list[ErrorDetails]) -> str:
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
