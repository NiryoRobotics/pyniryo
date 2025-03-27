from typing import Optional, Type, Any

import requests
from pydantic import BaseModel

from .exceptions import ServerException, ClientException


class HttpClient:
    """
    A simple HTTP client wrapped around the requests library to suit the API behaviours.
    """

    def __init__(self, hostname: str, port: int, prefix: str, headers: Optional[dict[str, str]] = None):
        if headers is None:
            headers = {}
        self.__hostname = hostname
        self.__port = port
        self.__prefix = prefix
        self.__headers = headers

    def set_header(self, key: str, value: str):
        self.__headers[key] = value

    def __resolve_status_code(self, response: requests.Response) -> None:
        if response.status_code >= 500:
            raise ServerException(response.status_code, response.text)
        elif response.status_code >= 400:
            raise ClientException(response.status_code, response.text)

    def __url(self, path: str) -> str:
        return f"http://{self.__hostname}:{self.__port}{self.__prefix}{path}"

    def __request(self, method: str, path: str, data: Optional[BaseModel] = None, ResponseModel: type = dict) -> Any:
        dict_data = None if data is None else data.model_dump()
        response = requests.request(method, self.__url(path), json=dict_data, headers=self.__headers)
        self.__resolve_status_code(response)

        if ResponseModel is None:
            return response.json()
        return ResponseModel(**response.json())

    def get(self, path: str, ResponseModel: type) -> Any:
        return self.__request('GET', path, data=None, ResponseModel=ResponseModel)

    def post(self, path: str, data: BaseModel, ResponseModel: type) -> Any:
        return self.__request('POST', path, data, ResponseModel)
