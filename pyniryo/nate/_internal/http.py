import warnings

import requests
from typing import Type, TypeVar, IO
from pydantic import BaseModel, ValidationError
from urllib3.exceptions import InsecureRequestWarning

from ..exceptions import get_msg_from_errors, ServerError, ClientError, InternalError

T = TypeVar("T", bound=BaseModel)


class HttpClient:
    """
    A simple HTTP client wrapped around the requests library to suit the API behaviours.
    """

    def __init__(self, hostname: str, port: int, token: str, insecure: bool = False, use_http: bool = False) -> None:
        """
        Initialize the HTTP client.
        :param hostname: The hostname of the API.
        :param port: The port of the API.
        """
        if not hostname:
            raise ValueError(f'Invalid hostname "{hostname}"')
        if not (1 <= port <= 2**16 - 1):
            raise ValueError(f'Invalid port number "{port}"')

        self.__hostname = hostname
        self.__port = port
        self.__headers = {}
        if token is not None:
            self.set_token(token)
        self.__insecure = insecure
        self.__scheme = 'http' if use_http else 'https'

        if self.__insecure:
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)

    def set_header(self, key: str, value: str) -> None:
        """
        Set a custom header.
        :param key: The key of the header.
        :param value: The value of the header.
        """
        self.__headers[key] = value

    def set_token(self, token: str) -> None:
        """
        Set the authentication token.
        :param token: The token to set.
        """
        self.set_header('Authorization', f'Bearer {token}')

    @staticmethod
    def __resolve_status_code(response: requests.Response) -> None:
        """
        Resolve the status code of the response and raise an exception if needed.
        :param response: The response to resolve.
        """
        if response.status_code >= 500:
            raise ServerError.from_response(response)
        elif response.status_code >= 400:
            raise ClientError.from_response(response)

    def __url(self, path: str) -> str:
        """
        Generate the URL for the request.
        :param path: The path of the request.
        :return: The URL of the request.
        """
        return f"{self.__scheme}://{self.__hostname}:{self.__port}{path}"

    def __request(self,
                  method: str,
                  path: str,
                  response_model: Type[T],
                  json: BaseModel | None = None,
                  files: dict[str, IO[bytes]] = None) -> T:
        """
        Make a request to the API.
        :param method: The method of the request.
        :param path: The path of the request.
        :param json: The data to send as serialized json with the request. If files is not None, this will be sent as form data.
        :param response_model: The model to use to parse the response.
        :return: The response of the request.
        :rtype: response_model
        """
        if response_model is not None and not issubclass(response_model, BaseModel):
            raise TypeError(f'Invalid type {response_model.__name__} for response model.')

        dict_json = None if json is None else json.model_dump(mode='json')
        response = requests.request(method,
                                    self.__url(path),
                                    json=dict_json if files is None else None,
                                    data=dict_json if files is not None else None,
                                    allow_redirects=True,
                                    files=files,
                                    headers=self.__headers,
                                    verify=not self.__insecure)
        self.__resolve_status_code(response)

        try:
            return response_model.model_validate(response.json())
        except ValidationError as e:
            raise InternalError(get_msg_from_errors(e.errors())) from e

    def get(self, path: str, response_model: Type[T]) -> T:
        """
        Make a GET request to the API.
        :param path: The path of the request.
        :param response_model: The model to use to parse the response.
        :return: The response of the request.
        :rtype: response_model
        """
        return self.__request('GET', path, response_model)

    def post(self, path: str, response_model: Type[T], data: BaseModel | None, files: dict[str, IO[bytes]] = None) -> T:
        """
        Make a POST request to the API.
        :param path: The path of the request.
        :param response_model: The model to use to parse the response.
        :param data: The data to send with the request.
        :param files: Optional files to send with the request.
        :return: The response of the request.
        :rtype: response_model
        """
        return self.__request('POST', path, response_model, data, files)

    def delete(self, path: str, response_model: Type[T]) -> T:
        """
        Make a DELETE request to the API.
        :param path: The path of the request.
        :param response_model: The model to use to parse the response.
        :return: The response of the request.
        :rtype: response_model
        """
        return self.__request('DELETE', path, response_model)

    def patch(self,
              path: str,
              response_model: Type[T],
              data: BaseModel | None,
              files: dict[str, IO[bytes]] = None) -> T:
        """
        Make a PATCH request to the API.
        :param path: The path of the request.
        :param response_model: The model to use to parse the response.
        :param data: The data to send with the request.
        :param files: Optional files to send with the request.
        :return: The response of the request.
        :rtype: response_model
        """
        return self.__request('PATCH', path, response_model, data, files)

    def download(self, path: str, dst: IO[bytes]) -> None:
        """
        Download a file from the API.
        :param path: The path of the file to download.
        :param dst: A file-like object to write the content to.
        :return: The content of the file, as a BytesIO object.
        """
        with requests.get(self.__url(path), headers=self.__headers, verify=not self.__insecure,
                          stream=True) as response:
            self.__resolve_status_code(response)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    dst.write(chunk)
