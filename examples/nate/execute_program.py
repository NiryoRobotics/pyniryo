import logging
from io import StringIO
from pathlib import Path

from pyniryo.nate.client import Nate
from pyniryo.nate.models.programs import ProgramType

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    n = Nate()

    move_poses_path = Path(__file__).parent.joinpath("move_poses.py")
    with open(move_poses_path, "r") as program_file:
        program = n.programs.create(move_poses_path.stem, program_file, program_type=ProgramType.python())

    program_output = StringIO()
    execution = n.programs.execute(
        program.id,
        environment={
            "NATE_INSECURE": "1",
            "NATE_USERNAME": "admin",
            "NATE_PASSWORD": "@dm1n",
        },
        stdout=program_output,
    )
    execution.wait()
    print(f'Execution finished with exit code {execution.execution.exitCode}')
    print('Program output:')
    print(program_output.getvalue())


if __name__ == "__main__":
    main()
