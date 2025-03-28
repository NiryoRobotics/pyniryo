from typing import Optional, Any

import requests
from pydantic import BaseModel

from .exceptions import ServerException, ClientException


class HttpClient:
    """
    A simple HTTP client wrapped around the requests library to suit the API behaviours.
    """

    def __init__(self, hostname: str, port: int, prefix: str = '', headers: Optional[dict[str, str]] = None):
        """
        Initialize the HTTP client.
        :param hostname: The hostname of the API.
        :param port: The port of the API.
        :param prefix: The prefix of the API.
        :param headers: The headers to use for the requests.
        """
        if headers is None:
            headers = {}
        self.__hostname = hostname
        self.__port = port
        self.__prefix = prefix
        self.__headers = headers

    def set_header(self, key: str, value: str):
        """
        Set a header for the requests.
        :param key: The key of the header.
        :param value: The value of the header.
        """
        self.__headers[key] = value

    def __resolve_status_code(self, response: requests.Response) -> None:
        """
        Resolve the status code of the response and raise an exception if needed.
        :param response: The response to resolve.
        """
        if response.status_code >= 500:
            raise ServerException(response.status_code, response.text)
        elif response.status_code >= 400:
            raise ClientException(response.status_code, response.text)

    def __url(self, path: str) -> str:
        """
        Generate the URL for the request.
        :param path: The path of the request.
        :return: The URL of the request.
        """
        return f"http://{self.__hostname}:{self.__port}{self.__prefix}{path}"

    def __request(self, method: str, path: str, data: Optional[BaseModel] = None, ResponseModel: type = dict) -> Any:
        """
        Make a request to the API.
        :param method: The method of the request.
        :param path: The path of the request.
        :param data: The data to send with the request.
        :param ResponseModel: The model to use to parse the response.
        :return: The response of the request.
        :rtype: ResponseModel
        """
        dict_data = None if data is None else data.model_dump()
        response = requests.request(method, self.__url(path), json=dict_data, headers=self.__headers)
        self.__resolve_status_code(response)

        if ResponseModel is None:
            return response.json()
        return ResponseModel(**response.json())

    def get(self, path: str, ResponseModel: type) -> Any:
        """
        Make a GET request to the API.
        :param path: The path of the request.
        :param ResponseModel: The model to use to parse the response.
        :return: The response of the request.
        :rtype: ResponseModel
        """
        return self.__request('GET', path, data=None, ResponseModel=ResponseModel)

    def post(self, path: str, data: BaseModel, ResponseModel: type) -> Any:
        """
        Make a POST request to the API.
        :param path: The path of the request.
        :param data: The data to send with the request.
        :param ResponseModel: The model to use to parse the response.
        :return: The response of the request.
        :rtype: ResponseModel
        """
        return self.__request('POST', path, data, ResponseModel)
