import logging
from io import StringIO
from pathlib import Path

from pyniryo.nate import Nate
from pyniryo.nate.models.programs import ProgramType, ExecutionStatusStatus

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    logger = logging.getLogger(__file__)
    n = Nate()

    move_poses_path = Path(__file__).parent.joinpath("move_poses.py")
    with open(move_poses_path, "rb") as program_file:
        program = n.programs.create(move_poses_path.stem, program_file, program_type=ProgramType.python())

    program_output = StringIO()

    def on_output(output: str, eof: bool):
        if eof:
            return
        program_output.write(output)

    def on_status(status: ExecutionStatusStatus):
        logger.info(f"Execution status: {status.value}")

    execution = n.programs.execute(
        program.id,
        environment={"MY_ENVIRONMENT_VARIABLE": "SOME_VALUE"},
        on_output=on_output,
    )
    execution.wait()
    print(f'Execution finished with exit code {execution.execution.exit_code} (status {execution.status})')
    print('Program output:')
    print(program_output.getvalue())


if __name__ == "__main__":
    main()
