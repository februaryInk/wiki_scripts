from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths

import re

# ------------------------------------------------------------------------------

def run() -> None:
    file_path = config.assets_root / 'designer_config\\MonoBehaviour\\AssetNpcProtoDataNpc.txt'

    # Input: structured text
    input_text = file_path.read_text()
    input_text = input_text.splitlines()
    print(input_text)

    output = parse_asset_dump(input_text)
    print(json.dumps(output, indent=2))

def parse_asset_dump(lines):
    array_index = 0
    result             = {}
    stack              = [result]
    indent_level_stack = [0]

    for line in lines[1:]:
        stripped       = line.lstrip()
        is_empty       = not stripped

        if is_empty: continue
        
        previous_indent_level = indent_level_stack[-1]
        indent_level = len(line) - len(stripped)
        
        while indent_level_stack and indent_level < indent_level_stack[-1]:
            stack.pop()
            indent_level_stack.pop()
          
        if indent_level_stack and indent_level > indent_level_stack[-1]:
            indent_level_stack.append(indent_level)
        
        current = stack[-1]
        is_array_size  = isinstance(current, list) and stripped.startswith('int size =')

        # Pop an extra item off the stack if:
        #   - We read an array size of 0
        #   - The last item on the stack is an empty dictionary, and this line 
        #     has the same indent.
        if is_array_size:
            if stripped == 'int size = 0':
                stack.pop()
            continue
        
        if current == {} and indent_level == previous_indent_level:
            stack.pop()

        # Is key-value pair? Assign it to the current dictionary or array.
        if ' = ' in stripped:
            type_key, value = map(str.strip, stripped.rsplit('=', 1))
            type, key       = type_key.rsplit(' ', 1)
            if type in ['int', 'SInt64', 'UInt8', 'unsigned int']:
                value = int(value)
            elif type == 'bool':
                value = value.lower() == 'true'
            
            if isinstance(current, list):
                current[array_index] = value
            else:
                current[key] = value
        # Is array index? Prepare the current array by making sure the index 
        # exists.
        elif re.match(r"^\[\d+\]$", stripped):
            array_index = int(stripped.strip("[]"))
            if isinstance(current, list):
                while len(current) <= array_index:
                    current.append(None)
        else:
            type, key = stripped.rsplit(' ', 1)
            if type == 'Array':
                value = []
            # Everything else is a dictionary-like.
            else:
                value = {}
            
            if isinstance(current, list):
                current[array_index] = value
                stack.append(current[array_index])
            else:
                current[key] = value
                stack.append(current[key])
    
    return result

if __name__ == '__main__':
    run()
