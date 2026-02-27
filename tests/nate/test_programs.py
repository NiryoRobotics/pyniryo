import unittest
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch
from uuid import uuid4

from pyniryo.nate.models import programs, robot
from pyniryo.nate._internal import transport_models, paths_gen, topics_gen
from pyniryo.nate.components.programs import Programs, ExecutionCommand
from pyniryo.nate.exceptions import PyNiryoError

from .base import BaseTestComponent

base_program = programs.Program(
    id=str(uuid4()),
    name='test_program',
    type=programs.ProgramType.PYTHON312,
)

base_execution = programs.ProgramExecution(
    id=str(uuid4()),
    program_id=base_program.id,
    context=programs.ProgramExecutionContext(environment={}, arguments=[]),
    started_at=datetime.now(),
    finished_at=datetime.now(),
    exit_code=0,
)


class TestPrograms(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.programs = Programs(http_client=self.http_client,
                                 mqtt_client=self.mqtt_client,
                                 correlation_id=self.correlation_id)

    def tearDown(self):
        del self.programs

    def test_get_all(self):
        """Test getting all programs."""
        t_models = transport_models.ProgramList([base_program.to_transport_model()])
        self.http_client.get.return_value = t_models

        all_programs = self.programs.get_all()

        self.http_client.get.assert_called_once_with(paths_gen.Programs.GET_ALL_PROGRAMS, transport_models.ProgramList)
        self.assertEqual(len(all_programs), 1)
        self.assertEqual(all_programs[0].id, base_program.id)
        self.assertEqual(all_programs[0].name, base_program.name)

    def test_create(self):
        """Test creating a program with file upload."""
        self.http_client.post.return_value = base_program.to_transport_model()

        file_content = b"print('Hello, World!')"
        file = BytesIO(file_content)

        program = self.programs.create('test_program', file, programs.ProgramType.PYTHON312)

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        self.assertEqual(call_args[0][0], paths_gen.Programs.CREATE_PROGRAM)
        self.assertEqual(call_args[0][1], transport_models.s.Program)
        self.assertIn('files', call_args[1])
        self.assertEqual(program.id, base_program.id)

    def test_get_without_download(self):
        """Test getting a program without downloading content."""
        self.http_client.get.return_value = base_program.to_transport_model()

        program = self.programs.get(base_program.id)

        self.http_client.get.assert_called_once_with(paths_gen.Programs.GET_PROGRAM.format(program_id=base_program.id),
                                                     transport_models.s.Program)
        self.http_client.download.assert_not_called()
        self.assertEqual(program.id, base_program.id)

    def test_get_with_download(self):
        """Test getting a program with downloading content."""
        self.http_client.get.return_value = base_program.to_transport_model()

        dst = BytesIO()
        program = self.programs.get(base_program.id, dst)

        self.http_client.get.assert_called_once()
        self.http_client.download.assert_called_once_with(
            paths_gen.Programs.GET_PROGRAM_FILE.format(program_id=base_program.id), dst)
        self.assertEqual(program.id, base_program.id)

    def test_delete(self):
        """Test deleting a program."""
        self.http_client.delete.return_value = None

        self.programs.delete(base_program.id)

        self.http_client.delete.assert_called_once_with(
            paths_gen.Programs.DELETE_PROGRAM.format(program_id=base_program.id), transport_models.EmptyPayload)

    def test_update_without_file(self):
        """Test updating program metadata without file upload."""
        updated_program = programs.Program(
            id=base_program.id,
            name='updated_program',
            type=programs.ProgramType.PYTHON312,
        )
        self.http_client.patch.return_value = updated_program.to_transport_model()

        program = self.programs.update(updated_program)

        self.http_client.patch.assert_called_once_with(
            paths_gen.Programs.UPDATE_PROGRAM.format(program_id=updated_program.id),
            transport_models.s.Program,
            updated_program.to_transport_model())
        self.assertEqual(program.name, 'updated_program')

    def test_update_with_file(self):
        """Test updating program with file upload."""
        self.http_client.patch.return_value = base_program.to_transport_model()

        file_content = b"print('Updated code')"
        src = BytesIO(file_content)

        _ = self.programs.update(base_program, src)

        # Should call patch twice: once for metadata, once for file
        self.assertEqual(self.http_client.patch.call_count, 2)

        # Check file upload call
        file_upload_call = self.http_client.patch.call_args_list[1]
        self.assertEqual(file_upload_call[0][0],
                         paths_gen.Programs.UPLOAD_PROGRAM_FILE.format(program_id=base_program.id))
        self.assertIn('files', file_upload_call[1])

    def test_get_executions(self):
        """Test getting all executions of a program."""
        t_models = transport_models.ProgramExecutionList([base_execution.to_transport_model()])
        self.http_client.get.return_value = t_models

        executions = self.programs.get_executions(base_program.id)

        self.http_client.get.assert_called_once_with(
            paths_gen.Programs.GET_PROGRAM_EXECUTIONS.format(program_id=base_program.id),
            transport_models.ProgramExecutionList)
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0].id, base_execution.id)

    def test_get_execution(self):
        """Test getting a specific program execution."""
        self.http_client.get.return_value = base_execution.to_transport_model()

        execution = self.programs.get_execution(base_program.id, base_execution.id)

        self.http_client.get.assert_called_once_with(
            paths_gen.Programs.GET_PROGRAM_EXECUTION.format(program_id=base_program.id, execution_id=base_execution.id),
            transport_models.s.ProgramExecution)
        self.assertEqual(execution.id, base_execution.id)

    def test_execute_without_callbacks(self):
        """Test executing a program without callbacks."""
        execution_id = str(uuid4())
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=execution_id)

        cmd = self.programs.execute(base_program.id)

        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Programs.EXECUTE_PROGRAM.format(program_id=base_program.id))
        self.assertEqual(call_args[1], transport_models.s.FeedbackResponse)

        request = call_args[2]
        self.assertEqual(str(request.execution_id), cmd.execution_id)

        self.assertIsInstance(cmd, ExecutionCommand)
        self.assertEqual(cmd.program_id, base_program.id)

    def test_execute_with_environment_and_arguments(self):
        """Test executing a program with environment variables and arguments."""
        execution_id = str(uuid4())
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=execution_id)

        env = {'KEY': 'value'}
        args = ['arg1', 'arg2']

        _ = self.programs.execute(base_program.id, environment=env, arguments=args)

        request = self.http_client.post.call_args[0][2]
        self.assertEqual(request.context.environment, env)
        self.assertEqual(request.context.arguments, args)

    def test_execute_with_callbacks(self):
        """Test executing a program with output and status callbacks."""
        execution_id = str(uuid4())
        self.http_client.post.return_value = transport_models.s.FeedbackResponse(feedback_id=execution_id)

        output_callback = MagicMock()
        status_callback = MagicMock()

        cmd = self.programs.execute(base_program.id, on_output=output_callback, on_status=status_callback)

        # Verify MQTT subscriptions were made
        self.assertEqual(self.mqtt_client.subscribe.call_count, 2)

        # Check output subscription
        output_topic = topics_gen.Programs.PROGRAM_EXECUTION_OUTPUT.format(program_id=base_program.id,
                                                                           execution_id=cmd.execution_id)
        status_topic = topics_gen.Programs.PROGRAM_EXECUTION_STATUS.format(program_id=base_program.id,
                                                                           execution_id=cmd.execution_id)

        subscribed_topics = [call[0][0] for call in self.mqtt_client.subscribe.call_args_list]
        self.assertIn(output_topic, subscribed_topics)
        self.assertIn(status_topic, subscribed_topics)

    def test_executor_status(self):
        """Test getting the executor status."""
        self.http_client.get.return_value = transport_models.s.ProgramsExecutorStatus(
            status=transport_models.s.ExecutorStatus.RUNNING)

        status = self.programs.executor_status()

        self.http_client.get.assert_called_once_with(paths_gen.Programs.GET_PROGRAMS_EXECUTOR_STATUS,
                                                     transport_models.s.ProgramsExecutorStatus)
        self.assertEqual(status, robot.ExecutorStatus.RUNNING)

    def test_pause(self):
        """Test pausing program execution."""
        self.http_client.patch.return_value = None

        self.programs.pause()

        self.http_client.patch.assert_called_once()
        call_args = self.http_client.patch.call_args[0]
        self.assertEqual(call_args[0], paths_gen.Programs.UPDATE_PROGRAMS_EXECUTOR_STATUS)
        request = call_args[2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.PAUSED)

    def test_stop(self):
        """Test stopping program execution."""
        self.http_client.patch.return_value = None

        self.programs.stop(sigkill=False)

        request = self.http_client.patch.call_args[0][2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.STOPPED)
        self.assertFalse(request.sigkill)

    def test_stop_with_sigkill(self):
        """Test stopping program execution with SIGKILL."""
        self.http_client.patch.return_value = None

        self.programs.stop(sigkill=True)

        request = self.http_client.patch.call_args[0][2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.STOPPED)
        self.assertTrue(request.sigkill)

    def test_resume(self):
        """Test resuming program execution."""
        self.http_client.patch.return_value = None

        self.programs.resume()

        request = self.http_client.patch.call_args[0][2]
        self.assertEqual(request.status, transport_models.s.ExecutorStatus.RUNNING)


class TestExecutionCommand(BaseTestComponent):

    def test_status_property(self):
        """Test getting the execution status."""
        execution_id = str(uuid4())

        cmd = ExecutionCommand(self.mqtt_client, base_program.id, execution_id, None, None, lambda: base_execution)

        # Initial status should be RUNNING
        self.assertEqual(cmd.status, programs.ExecutionStatusStatus.RUNNING)

    def test_output_callback_invocation(self):
        """Test that output callback is invoked when output is received."""
        execution_id = str(uuid4())
        output_callback = MagicMock()

        _ = ExecutionCommand(self.mqtt_client,
                             base_program.id,
                             execution_id,
                             output_callback,
                             None,
                             lambda: base_execution)

        # Get the internal callback that was registered
        output_topic = topics_gen.Programs.PROGRAM_EXECUTION_OUTPUT.format(program_id=base_program.id,
                                                                           execution_id=execution_id)

        # Find the output callback in subscribe calls
        internal_callback = None
        for call_args in self.mqtt_client.subscribe.call_args_list:
            if call_args[0][0] == output_topic:
                internal_callback = call_args[0][1]
                break

        self.assertIsNotNone(internal_callback)

        # Simulate receiving output
        internal_callback(output_topic, transport_models.a.ProgramExecutionOutput(output='test output', eof=False))

        output_callback.assert_called_once_with('test output', False)

    def test_status_callback_invocation(self):
        """Test that status callback is invoked when status changes."""
        execution_id = str(uuid4())
        status_callback = MagicMock()

        self.http_client.get.return_value = base_execution.to_transport_model()

        cmd = ExecutionCommand(self.mqtt_client,
                               base_program.id,
                               execution_id,
                               None,
                               status_callback,
                               lambda: base_execution)

        # Get the internal status callback
        status_topic = topics_gen.Programs.PROGRAM_EXECUTION_STATUS.format(program_id=base_program.id,
                                                                           execution_id=execution_id)

        internal_callback = None
        for call_args in self.mqtt_client.subscribe.call_args_list:
            if call_args[0][0] == status_topic:
                internal_callback = call_args[0][1]
                break

        self.assertIsNotNone(internal_callback)

        # Simulate status change
        internal_callback(status_topic,
                          transport_models.s.ProgramsExecutorStatus(status=transport_models.s.ExecutorStatus.COMPLETED))

        status_callback.assert_called_once_with(programs.ExecutionStatusStatus.COMPLETED)

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_success(self, mock_monotonic, mock_sleep):
        """Test waiting for execution to complete successfully."""
        execution_id = str(uuid4())
        mock_monotonic.return_value = 0.0

        self.http_client.get.return_value = base_execution.to_transport_model()

        cmd = ExecutionCommand(self.mqtt_client, base_program.id, execution_id, None, None, lambda: base_execution)

        # Simulate status change to completed
        status_topic = topics_gen.Programs.PROGRAM_EXECUTION_STATUS.format(program_id=base_program.id,
                                                                           execution_id=execution_id)

        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        internal_callback(status_topic,
                          transport_models.s.ProgramsExecutorStatus(status=transport_models.s.ExecutorStatus.COMPLETED))

        # Wait should return without error
        cmd.wait()

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_timeout(self, mock_monotonic, mock_sleep):
        """Test waiting for execution with timeout."""
        execution_id = str(uuid4())
        mock_monotonic.side_effect = [0.0, 1.0, 2.0, 3.0]

        cmd = ExecutionCommand(self.mqtt_client, base_program.id, execution_id, None, None, lambda: base_execution)

        # Don't change status, so it stays RUNNING
        with self.assertRaises(TimeoutError):
            cmd.wait(timeout=1.0)

    @patch('time.sleep')
    @patch('time.monotonic')
    def test_wait_failure(self, mock_monotonic, mock_sleep):
        """Test waiting for execution that fails."""
        execution_id = str(uuid4())
        mock_monotonic.return_value = 0.0

        self.http_client.get.return_value = base_execution.to_transport_model()

        cmd = ExecutionCommand(self.mqtt_client, base_program.id, execution_id, None, None, lambda: base_execution)

        # Simulate status change to failed
        status_topic = topics_gen.Programs.PROGRAM_EXECUTION_STATUS.format(program_id=base_program.id,
                                                                           execution_id=execution_id)

        internal_callback = self.mqtt_client.subscribe.call_args[0][1]
        internal_callback(status_topic,
                          transport_models.s.ProgramsExecutorStatus(status=transport_models.s.ExecutorStatus.FAILED))

        # Wait should raise an error
        with self.assertRaises(PyNiryoError):
            cmd.wait()


if __name__ == "__main__":
    unittest.main()
