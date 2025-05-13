class PyNiryoError(Exception):
    pass


class ClientError(PyNiryoError):
    pass


class ServerError(PyNiryoError):
    pass


class DataValidationError(PyNiryoError):
    pass


class InternalError(PyNiryoError):
    pass


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
