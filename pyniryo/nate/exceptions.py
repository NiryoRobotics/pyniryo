class PyNiryoError(Exception):
    pass


class ClientError(PyNiryoError):
    pass


class ServerError(PyNiryoError):
    pass


class DataValidationError(PyNiryoError):
    pass
