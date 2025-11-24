from pydantic import RootModel
from .models_gen import User, Token, Program, ProgramExecution

UserList = RootModel[list[User]]
TokenList = RootModel[list[Token]]

ProgramList = RootModel[list[Program]]
ProgramExecutionList = RootModel[list[ProgramExecution]]

FrameIdList = RootModel[list[str]]
