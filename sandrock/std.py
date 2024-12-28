'''
Define core enviroment for our runtime, with only Python library imports. None 
of our own modules.
'''

import json
import sys

from collections     import defaultdict
from collections.abc import Iterator, Iterable
from functools       import cache
from pathlib         import Path
from typing          import (
    Any,
    Callable,
    NotRequired,
    TYPE_CHECKING,
    Type,
    TypeAlias,
    TypeVar,
    TypedDict,
    overload,
)
from xml.etree      import ElementTree

# ------------------------------------------------------------------------------

PathLike: TypeAlias = Path | str
