from pydantic import BaseModel, RootModel
from .models_gen import User, Token, Program, ProgramExecution


class UserEvent(BaseModel):
    pass


UserLoggedIn = UserEvent
UserLoggedOut = UserEvent

UserList = RootModel[list[User]]
TokenList = RootModel[list[Token]]


class MoveFeedback(BaseModel):
    state: str
    message: str


ProgramList = RootModel[list[Program]]
ProgramExecutionList = RootModel[list[ProgramExecution]]


class ProgramExecutionStatus(BaseModel):
    status: str


class ProgramExecutionOutput(BaseModel):
    output: str
    eof: bool


FrameIdList = RootModel[list[str]]
