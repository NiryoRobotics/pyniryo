from pydantic import RootModel, BaseModel, Field

from .models_gen import User, Token, Program, ProgramExecution

UserList = RootModel[list[User]]
TokenList = RootModel[list[Token]]

ProgramList = RootModel[list[Program]]
ProgramExecutionList = RootModel[list[ProgramExecution]]

FrameIdList = RootModel[list[str]]


class HealthCheckResponse(BaseModel):
    status: str = Field(description="The health status of the robot.", examples=['ok'])


class ReadinessCheckResponse(BaseModel):
    ready: bool = Field(description="Whether the robot is ready or not.")


class EmptyPayload(BaseModel):
    """
    An empty response model for endpoints that return no data.
    """
    pass
