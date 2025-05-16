import sys

if sys.version_info < (3, 11):
    from typing_extensions import *
else:
    from typing import *