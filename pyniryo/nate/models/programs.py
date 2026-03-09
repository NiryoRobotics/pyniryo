import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from strenum import StrEnum

from .._internal import transport_models


class ProgramType(StrEnum):
    """
    Enumeration of supported program types and Python versions.
    """
    PYTHON39 = 'python3.9'
    PYTHON310 = 'python3.10'
    PYTHON311 = 'python3.11'
    PYTHON312 = 'python3.12'

    def __key(self) -> tuple[str, tuple[int, ...]]:
        pattern = r'^([a-z]+)([\d\.?]+)$'
        match = re.match(pattern, self)
        if not match:
            raise ValueError(f"Invalid ProgramType format: {self}")
        return match.group(1), tuple(int(v) for v in match.group(2).split('.'))

    @classmethod
    def python(cls) -> 'ProgramType':
        """
        Get the latest supported Python version.
        :return: The latest supported Python version.
        """
        return max((e for e in cls if e.__key()[0] == 'python'), key=lambda e: e.__key())

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramType) -> 'ProgramType':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.ProgramType:
        return transport_models.s.ProgramType(str(self))


@dataclass
class Program:
    """
    Represents a program stored on the robot.
    
    :param id: The unique identifier of the program.
    :param name: The name of the program.
    :param type: The type/version of the program.
    """
    id: str
    name: str
    type: ProgramType

    @classmethod
    def from_transport_model(cls, model: transport_models.s.Program) -> 'Program':
        return cls(
            id=str(model.id),
            name=model.name,
            type=ProgramType.from_transport_model(model.type),
        )

    def to_transport_model(self) -> transport_models.s.Program:
        return transport_models.s.Program(
            id=UUID(self.id),
            name=self.name,
            type=transport_models.s.ProgramType(self.type.value),
        )


@dataclass
class ProgramExecutionContext:
    """
    Represents the execution context for a program.
    
    :param environment: Environment variables to set for the program execution.
    :param arguments: Command-line arguments to pass to the program.
    """
    environment: dict[str, str]
    arguments: list[str]

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramExecutionContext) -> 'ProgramExecutionContext':
        return cls(
            environment=model.environment or {},
            arguments=model.arguments or [],
        )

    def to_transport_model(self) -> transport_models.s.ProgramExecutionContext:
        return transport_models.s.ProgramExecutionContext(environment=self.environment, arguments=self.arguments)


@dataclass
class ProgramExecution:
    """
    Represents a program execution instance.
    
    :param id: The unique identifier of the execution.
    :param program_id: The ID of the program being executed.
    :param context: The execution context (environment variables and arguments).
    :param started_at: When the execution started.
    :param finished_at: When the execution finished.
    :param exit_code: The exit code of the program execution.
    """
    id: str
    program_id: str
    context: ProgramExecutionContext
    started_at: datetime | None
    finished_at: datetime | None
    exit_code: int | None

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramExecution) -> 'ProgramExecution':
        return cls(
            id=str(model.id),
            program_id=str(model.programId),
            context=ProgramExecutionContext.from_transport_model(model.context),
            started_at=model.startedAt,
            finished_at=model.finishedAt,
            exit_code=model.exitCode,
        )

    def to_transport_model(self) -> transport_models.s.ProgramExecution:
        return transport_models.s.ProgramExecution(id=UUID(self.id),
                                                   programId=UUID(self.program_id),
                                                   context=self.context.to_transport_model(),
                                                   startedAt=self.started_at,
                                                   finishedAt=self.finished_at,
                                                   exitCode=self.exit_code)


@dataclass
class ExecutionOutput:
    """
    Represents output from a program execution.
    
    :param output: The output text from the program.
    :param eof: Whether this is the end of the output stream.
    """
    output: str
    eof: bool

    @classmethod
    def from_transport_model(cls, model: transport_models.a.ProgramExecutionOutput) -> 'ExecutionOutput':
        return cls(output=model.output, eof=model.eof)

    def to_transport_model(self) -> transport_models.a.ProgramExecutionOutput:
        return transport_models.a.ProgramExecutionOutput(output=self.output, eof=self.eof)


class ExecutionStatusStatus(StrEnum):
    """
    Enumeration of program execution statuses.
    """
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PAUSED = 'paused'
    STOPPED = 'stopped'

    def is_error(self) -> bool:
        """
        Check if this status represents an error condition.
        
        :return: True if the status indicates failure, False otherwise.
        """
        return self == ExecutionStatusStatus.FAILED

    def is_final(self) -> bool:
        """
        Check if this status represents a final state.
        
        :return: True if the status is final (completed or failed), False otherwise.
        """
        return self == ExecutionStatusStatus.COMPLETED or self.is_error()

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ExecutorStatus) -> 'ExecutionStatusStatus':
        return cls(model.value)

    def to_transport_model(self) -> transport_models.s.ExecutorStatus:
        return transport_models.s.ExecutorStatus(self.value)


@dataclass
class ExecutionStatus:
    """
    Represents the current status of a program execution.
    
    :param status: The current execution status.
    """
    status: ExecutionStatusStatus

    @classmethod
    def from_transport_model(cls, model: transport_models.s.ProgramsExecutorStatus) -> 'ExecutionStatus':
        return cls(status=ExecutionStatusStatus.from_transport_model(model.status))

    def to_transport_model(self) -> transport_models.s.ProgramsExecutorStatus:
        return transport_models.s.ProgramsExecutorStatus(status=self.status.to_transport_model())
