from strenum import StrEnum


class Auth(StrEnum):
    USER_LOGGED_IN = 'users/{user_id}/logged-in'


class Robot(StrEnum):
    JOINTS = 'robot/joints'
    MOVE_FEEDBACK = 'robot/{cmd_id}/move-feedback'


class ProgramsExecution(StrEnum):
    OUTPUT = 'programs/{program_id}/executions/{execution_id}/output'
    STATUS = 'programs/{program_id}/executions/{execution_id}/status'
