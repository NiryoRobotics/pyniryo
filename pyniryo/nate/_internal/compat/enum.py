import sys

if sys.version_info < (3, 11):
    from enum import Enum
    class StrEnum(str, Enum):
        """
        A subclass of str and Enum that allows for string comparison.
        This is a workaround for Python versions < 3.11 where str and Enum
        cannot be compared directly.
        """
        pass
else:
    from enum import StrEnum

__all__ = ['StrEnum']

