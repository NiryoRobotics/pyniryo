from typing import Optional
from datetime import datetime

from .base_api_component import BaseAPIComponent
from ..models import Token, Login


class Auth(BaseAPIComponent):

    def login(self, email: str, password: str, expires_at: Optional[datetime] = None) -> Token:
        return self._http_client.post('/login', Login(email=email, password=password, expires_at=expires_at), Token)
