from pydantic import BaseModel


class UserEvent(BaseModel):
    pass


UserLoggedIn = UserEvent
UserLoggedOut = UserEvent
