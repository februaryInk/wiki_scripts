'''
Encode and chunk all of the game's English text.

Requires:
    - text
'''


# pip install lupa
from lupa import LuaRuntime

from sandrock import *
from sandrock.lib.text import load_text
from sandrock.preproc import get_config_paths

texts = load_text(config.wiki_language)

base_name = 'AssetItemEnglish'
chunk_ranges = [
    (1, 200000),
    (200000, 32000000),
    (32000000, 70000000),
    (70000000, 80000000),
    (80000000, 80020000),
    (80020000, 82000000),
    (82000000, 90000000),
    (90000000, float('inf'))
]

# Counterpart to decode2 in the Encoding Lua module.
lua_code = '''
function encode2(str)
    local encoded_str = ''
    for i = 1, #str do
        local byte = string.byte(str, i)

        if 0x21 <= byte and byte <= 0x7e then  -- printable char
            byte = 0x9f - byte
        end
        encoded_str = encoded_str .. string.char(byte)
    end
    return encoded_str
end
'''

def get_items_in_range(items, start, end) -> dict:
    return {key: value for key, value in items.items() if start <= key < end}

def run() -> None:
    # Initialize the Lua runtime, then load the Lua function, which was copied
    # over from Module:Encoding.
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(lua_code)
    encoder = lua.globals()

    items = {}

    for id, text in texts.items():
        encoded_text = encoder.encode2(text)
        items[id] = encoded_text
    items = dict(sorted(items.items()))

    assembler_data = {
        'version': config.version,
        'key': 'Text',
        'chunks': []
    }

    for start, end in chunk_ranges:
        chunk_name  = f'{base_name}_{start}'
        chunk_items = get_items_in_range(items, start, end)
        min_val     = min(chunk_items.keys())
        max_val     = max(chunk_items.keys())
        assembler_data['chunks'].append(
            {
                'name': chunk_name,
                'low': min_val,
                'high': max_val
            }
        )
        data = {
            'version': config.version,
            'key': 'Text',
            'configList': chunk_items
        }
        write_lua(config.output_dir / f'lua/{chunk_name}.lua', data)
    
    write_lua(config.output_dir / f'lua/{base_name}.lua', assembler_data)

if __name__ == '__main__':
    run()
