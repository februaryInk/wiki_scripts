'''
Methods for converting our script results to other formats.
'''

from sandrock.std import *

# -- Lua -----------------------------------------------------------------------

def_minimize = True and 0
def_compact_after = 3

def lua_dump(value, parent_indent: str, indent: str) -> str:
    if isinstance(value, dict):
        return lua_dump_object(value, parent_indent, indent)
    if isinstance(value, list):
        return lua_dump_array(value, parent_indent, indent)
    if isinstance(value, str):
        return lua_dump_string(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return dump_float(value)
    if value is None:
        return 'nil'
    raise TypeError('Cannot serialize value:', repr(value))

def lua_dump_array(arr: list, parent_indent: str, indent: str, minimize: bool = def_minimize, compact_after: int = def_compact_after) -> str:
    if not arr: return '{}'
    
    child_indent = parent_indent + indent
    compact      = len(parent_indent) >= compact_after
    lines        = ['{']
    separation   = '' if minimize and compact else ' '

    for value in arr:
        s = lua_dump(value, child_indent, indent)
        lines.append(s)
    lines.append('}')

    if compact:
        return lines[0] + f',{separation}'.join(lines[1:-1]) + lines[-1]
    else:
        indents = [''] + [child_indent] * (len(lines) - 2) + [parent_indent]
        commas  = [''] + [','] * max(0, (len(lines) - 3)) + ['', '']
        lines = [indent + line + comma for indent, line, comma in zip(indents, lines, commas)]
        return '\n'.join(lines)

def lua_dump_object(obj: dict, parent_indent: str, indent: str, minimize: bool = def_minimize, compact_after: int = def_compact_after) -> str:
    if not obj: return '{}'

    child_indent = parent_indent + indent
    compact      = len(parent_indent) >= compact_after
    lines        = ['{']
    separation   = '' if minimize and len(parent_indent) >= compact_after - 1 else ' '
    
    for key, value in obj.items():
        if not isinstance(key, str):
            key = f'[{key}]'
        elif not key.isidentifier():
            key = f'[{lua_dump_string(key)}]'
        s = lua_dump(value, child_indent, indent)
        lines.append(f'{key}{separation}={separation}{s}')
    lines.append('}')
    
    if compact:
        return lines[0] + f',{separation}'.join(lines[1:-1]) + lines[-1]
    else:
        indents = [''] + [child_indent] * (len(lines) - 2) + [parent_indent]
        commas  = [''] + [','] * max(0, (len(lines) - 3)) + ['', '']
        lines = [indent + line + comma for indent, line, comma in zip(indents, lines, commas)]
        return '\n'.join(lines)

def lua_dump_string(s: str) -> str:
    # assert '\\' not in s
    s = s.replace('\\', '\\\\')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('"', '\\"')
    return f'"{s}"'

# -- YAML ----------------------------------------------------------------------

def yaml_dump(value: Any, parent_indent: str, indent: str) -> str | list[str]:
    if isinstance(value, dict):
        return yaml_dump_object(value, parent_indent, indent)
    if isinstance(value, list):
        return yaml_dump_array(value, parent_indent, indent)
    if isinstance(value, str):
        return yaml_dump_string(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return dump_float(value)
    if value is None:
        return 'null'
    raise TypeError('Cannot serialize value:', repr(value))

def yaml_dump_object(obj: dict, parent_indent: str, indent: str) -> str | list[str]:
    if not obj:
        return '{}'
    child_indent = parent_indent + indent
    last         = list(obj.keys())[-1]
    lines        = []
    for key, value in obj.items():
        prefix = f'{parent_indent}{key}:'
        s = yaml_dump(value, child_indent, indent)
        if isinstance(s, list):
            lines.append(prefix)
            lines += s
        else:
            lines.append(f'{prefix} {s}')
    return lines

def yaml_dump_array(arr: list, parent_indent: str, indent: str) -> str | list[str]:
    if not arr:
        return '[]'
    if not parent_indent:
        child_indent = '  '
        prefix = '- '
    else:
        child_indent = parent_indent
        prefix = parent_indent[:-2] + '- '
    lines = []
    for value in arr:
        s = yaml_dump(value, child_indent, indent)
        if isinstance(s, list):
            lines.append(prefix + s[0].lstrip())
            lines += s[1:]
        else:
            lines.append(prefix + s)
    return lines

def yaml_dump_string(s: str) -> str:
    if not s:
        return "''"
    need_quote = False

    special_chars = '\n\'":{}'
    if s.strip() != s:
        need_quote = True
    if any(special_char in s for special_char in special_chars):
        need_quote = True
    if ' -' in s:
        need_quote = True
    if s[0] == '[' or s[0] == ']':
        need_quote = True

    if need_quote:
        return '"' + s.replace('"', '\\"').replace('\n', '\\n') + '"'
    else:
        return s

# -- Shared --------------------------------------------------------------------

def dump_float(x: float) -> str:
    scaled = x * 1000
    rounded = round(scaled)
    if abs(scaled - rounded) < 0.001:
        x = rounded * 0.001
        s = f'{x:.5f}'.rstrip('0')
        if s.endswith('.'):
            s += '0'
        return s
    else:
        return str(x)
