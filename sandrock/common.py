'''
Define common environment for our runtime.
'''

from .std import *
from .utils import *

# Get the project config from the one-level-up parent directory.
sys.path.append(str(Path(__file__).parents[1]))
import config
sys.path.pop()

# ------------------------------------------------------------------------------

class Vector3(TypedDict):
    x: float
    y: float
    z: float
