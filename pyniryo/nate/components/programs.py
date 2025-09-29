import logging
import os
import sys
import time
from io import TextIOWrapper
from typing import IO, BinaryIO
from uuid import uuid4, UUID

from .base_api_component import BaseAPIComponent
from .._internal import paths_gen, transport_models, topics
from .. import models
from .._internal.mqtt import MqttClient
from ..exceptions import PyNiryoError
from ..models import ProgramType, ExecutionStatusStatus

logger = logging.getLogger(__name__)


class ExecutionCommand:

    def __init__(self, mqtt_client: MqttClient, program_id: str, execution_id: str, stdout: str | TextIOWrapper):
        self.__mqtt_client: MqttClient = mqtt_client
        self.__program_id: str = program_id
        self.__execution_id: str = execution_id

        self.__stdout = stdout
        self.__should_close_stdout = False

        if isinstance(stdout, str):
            self.__stdout = open(stdout, 'w', buffering=1)  # line buffered
            self.__should_close_stdout = True

        self.__mqtt_client.subscribe(self.output_topic, self.__output_callback, transport_models.ProgramExecutionOutput)

        self.__status: list[models.ExecutionStatus] = [models.ExecutionStatus(status=ExecutionStatusStatus.RUNNING)]
        self.__mqtt_client.subscribe(self.status_topic, self.__status_callback, transport_models.ProgramExecutionStatus)

    def __output_callback(self, _topic: str, payload: transport_models.ProgramExecutionOutput):
        """
        Internal callback to handle output messages.
        """
        if payload.eof:
            self.__mqtt_client.unsubscribe(self.__output_callback)
            if self.__should_close_stdout:
                self.__stdout.close()
            return

        self.__stdout.write(payload.output + '\n')
        self.__stdout.flush()

    def __status_callback(self, _topic: str, payload: transport_models.ProgramExecutionStatus) -> None:
        """
        Internal callback to handle execution state messages.
        """
        self.__status.append(models.ExecutionStatus.from_transport_model(payload))
        if self.status.is_final():
            self.__mqtt_client.unsubscribe(self.__status_callback)

    @property
    def status(self) -> models.ExecutionStatusStatus:
        """
        Get the current state of the move command.

        :return: The current state of the move command.
        """
        return self.__status[-1].status

    @property
    def program_id(self) -> str:
        """
        Get the program ID of the execution.

        :return: The program ID.
        """
        return self.__program_id

    @property
    def execution_id(self) -> str:
        """
        Get the execution ID of the execution.

        :return: The execution ID.
        """
        return self.__execution_id

    @property
    def output_topic(self) -> str:
        """
        Get the output topic of the execution.

        :return: The output topic of the execution.
        """
        return topics.ProgramsExecution.OUTPUT.format(program_id=self.__program_id, execution_id=self.__execution_id)

    @property
    def status_topic(self) -> str:
        """
        Get the status topic of the execution.

        :return: The status topic of the execution.
        """
        return topics.ProgramsExecution.STATUS.format(program_id=self.__program_id, execution_id=self.__execution_id)

    def wait(self, timeout: float = -1) -> None:
        """
        Wait for the move command to complete.
        :param timeout: The maximum time to wait in seconds. If negative, wait indefinitely.
        """
        start = time.monotonic()
        while not self.status.is_final():
            if start + timeout > time.monotonic():
                raise TimeoutError(f'Execution {self.__execution_id} timed out after {timeout} seconds.')
            time.sleep(0.1)
        # TODO: more detailed errors
        if self.status.is_error():
            raise PyNiryoError(f'Execution {self.__execution_id} failed')


class Programs(BaseAPIComponent):
    """
    Programs component for the API.
    """

    def get_all(self) -> list[models.Program]:
        """
        Get all the registered programs.

        :return: The list of all the programs.
        """
        programs = self._http_client.get(
            paths_gen.Programs.PROGRAMS,
            transport_models.ProgramList,
        )
        return [models.Program.from_transport_model(program) for program in programs.root]

    def create(self, name: str, program: IO[bytes], program_type: ProgramType) -> models.Program:
        """
        Upload a new program.

        :param name: The name of the program.
        :param program: A file-like object containing the program content.
        :param program_type: The type of the program.
        :return: The created program.
        """
        program = self._http_client.post(
            paths_gen.Programs.PROGRAMS,
            transport_models.Program(name=name, type=program_type.to_transport_model()),
            transport_models.Program,
            files={'file': program},
        )
        return models.Program.from_transport_model(program)

    def get(self, program_id: str, dst: IO[bytes] = None) -> models.Program:
        """
        Get a program by its ID.

        :param program_id: The ID of the program.
        :param dst: Optional file-like object to download the program content into. If None, the content is not downloaded.
        :return: The corresponding program.
        """
        tr_program = self._http_client.get(
            paths_gen.Programs.PROGRAM.format(program_id=program_id),
            transport_models.Program,
        )
        program = models.Program.from_transport_model(tr_program)
        if dst is not None:
            self._http_client.download(paths_gen.Programs.PROGRAM_FILE.format(program_id=program_id), dst)
        return program

    def delete(self, program_id: str) -> None:
        """
        Delete a program by its ID.

        :param program_id: The ID of the program.
        :return: None
        """
        return self._http_client.delete(paths_gen.Programs.PROGRAM.format(program_id=program_id))

    def update(self, program: models.Program, src: IO[bytes] = None) -> models.Program:
        """
        Update a program.

        :param program: The program to update.
        :param src: Optional file-like object containing the new program content. If None, the content is not updated.
        :return: The updated program.
        """
        program = self._http_client.patch(paths_gen.Programs.PROGRAM.format(program_id=program.id),
                                          program.to_transport_model(),
                                          transport_models.Program)
        if src is not None:
            self._http_client.patch(paths_gen.Programs.PROGRAM_FILE.format(program_id=program.id),
                                    None,
                                    None,
                                    files={'file': src})
        return models.Program.from_transport_model(program)

    def get_executions(self, program_id: str) -> list[models.ProgramExecution]:
        """
        Get all the executions of a program.

        :param program_id: The ID of the program.
        :return: The list of all the executions of the program.
        """
        executions = self._http_client.get(
            paths_gen.Programs.PROGRAM_EXECUTIONS.format(program_id=program_id),
            transport_models.ProgramExecutionList,
        )
        return [models.ProgramExecution.from_transport_model(execution) for execution in executions.root]

    def execute(self,
                program_id: str,
                environment: dict[str, str] = None,
                arguments: list[str] = None,
                stdout: str | TextIOWrapper = os.devnull) -> ExecutionCommand:
        """
        Execute a program.

        :param program_id: The ID of the program.
        :param environment: Optional dictionary of environment variables to pass to the program.
        :param arguments: Optional list of command line arguments to pass to the program.
        :param stdout: Destination for the program output. It can be a file-like object or a file path.
                       If a file path, the output is written to the file.  If a file-like object, the output is written
                       to the object. Default is os.devnull: the output is discarded
        :return: The created program execution.
        """
        execution_id = uuid4()
        execution_command = ExecutionCommand(self._mqtt_client, program_id, str(execution_id), stdout)

        self._http_client.post(
            paths_gen.Programs.PROGRAM_EXECUTIONS.format(program_id=program_id),
            transport_models.ExecuteProgram(execution_id=execution_id,
                                            context=transport_models.ProgramExecutionContext(programId=UUID(program_id),
                                                                                             environment=environment,
                                                                                             arguments=arguments)),
            transport_models.FeedbackResponse,
        )
        return execution_command
