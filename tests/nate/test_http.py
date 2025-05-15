import unittest
from unittest.mock import patch, Mock
from pydantic import BaseModel

from pyniryo.nate.exceptions import ServerError, ClientError, InternalError
from pyniryo.nate._internal.http import HttpClient


class ResponseModel(BaseModel):
    message: str


class TestHttpClient(unittest.TestCase):

    def setUp(self) -> None:
        self.client = HttpClient("localhost", 8000)

    def mock_response(self, status_code: int, json_data=None, text=""):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        mock_response.text = text
        return mock_response

    @patch("requests.request", autospec=True)
    def test_get_request_success(self, mock_request):
        mock_request.return_value = self.mock_response(200, {"message": "Success"})

        response = self.client.get("/test", ResponseModel)
        self.assertEqual(response.message, "Success")

    @patch("requests.request", autospec=True)
    def test_post_request_success(self, mock_request):
        mock_request.return_value = self.mock_response(201, {"message": "Created"})

        data = ResponseModel(message="Hello")
        response = self.client.post("/test", data, ResponseModel)
        self.assertEqual(response.message, "Created")

    @patch("requests.request", autospec=True)
    def test_delete_request_success(self, mock_request):
        mock_request.return_value = self.mock_response(204)

        response = self.client.delete("/test")
        self.assertIsNone(response)

    @patch("requests.request", autospec=True)
    def test_server_error(self, mock_request):
        mock_request.return_value = self.mock_response(500, text="Internal Server Error")

        with self.assertRaises(ServerError):
            self.client.get("/test", ResponseModel)

    @patch("requests.request", autospec=True)
    def test_client_error(self, mock_request):
        mock_request.return_value = self.mock_response(404, text="Not Found")

        with self.assertRaises(ClientError):
            self.client.get("/test", ResponseModel)

    @patch("requests.request", autospec=True)
    def test_model_validation_error(self, mock_request):
        mock_request.return_value = self.mock_response(200, {"message": 123})

        with self.assertRaises(InternalError):
            self.client.get("/test", ResponseModel)

    @patch("requests.request", autospec=True)
    def test_internal_error_on_invalid_json(self, mock_request):
        mock_request.return_value = self.mock_response(200, "Invalid JSON")

        with self.assertRaises(InternalError):
            self.client.get("/test", ResponseModel)


if __name__ == "__main__":
    unittest.main()
