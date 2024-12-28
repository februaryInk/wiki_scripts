'''
Basic utility methods.
'''

from .std import *
from .dump import lua_dump, yaml_dump

# ------------------------------------------------------------------------------

# Wildcard export methods.
__all__ = [
    'read_json',
    'sorted_dict',
    'write_json',
    'write_lua',
    'write_text',
    'write_xml',
    'write_yaml',
]

# Key, Type, Value
K = TypeVar('K')
T = TypeVar('T')
V = TypeVar('V')

# ------------------------------------------------------------------------------

# Overload with multiple call: return signatures.
# If called only with a path, the output type is indeterminate.
@overload
def read_json(Path: PathLike) -> Any: ...
# If called with a type, the output should be that type.
@overload
def read_json(Path: PathLike, json_type: Type[T]) -> T: ...
def read_json(path, json_type=None):
    with open(path) as f:
        return json.load(f)

# Sort dictionary by its keys.
def sorted_dict(dict_: dict[K, V]) -> dict[K, V]:
    return dict(sorted(dict_.items()))

# -- Output Methods ------------------------------------------------------------

def write_json(path: PathLike, data: Any) -> None:
    with open(_resolve_path(path), 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_lua(path: PathLike, data: Any, indent: str = '\t') -> None:
    s = lua_dump(data, '', indent)
    _resolve_path(path).write_text('return ' + s)

def write_text(path: PathLike, text: str) -> None:
    with open(_resolve_path(path), 'w') as f:
        f.write(text)

def write_xml(path: PathLike, root: ElementTree.Element) -> None:
    ElementTree.ElementTree(root).write(_resolve_path(path), 'utf_8')

def write_yaml(path: PathLike, data: Any) -> None:
    s = yaml_dump(data, '', '    ')
    if isinstance(s, list):
        s = '\n'.join(s)
    _resolve_path(path).write_text(s)

# -- Private -------------------------------------------------------------------

def _resolve_path(path: PathLike) -> Path:
    path = Path(path)
    if not path.is_absolute():
        from .common import config
        path = config.output_dir / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
