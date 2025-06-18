'''
Because wiki pages need to have unique names, we cannot always use exactly the 
item name given in the game because the game has items with duplicate names. 
This script assigns unique names to item ids so the wiki can identify the item 
properly.
'''

from sandrock          import *
from sandrock.lib.text import load_wiki_names

# ------------------------------------------------------------------------------

def run() -> None:
    ids_to_names = load_wiki_names()
    names_to_ids = {name: id_ for id_, name in ids_to_names.items()}
    
    key = 'ItemName'
    data = {
        'version': config.version,
        'key': key,
        'configList': ids_to_names
    }

    write_lua(config.output_dir / f'lua/Asset{key}.lua', data)

    key = 'ItemId'
    data = {
        'version': config.version,
        'key': key,
        'configList': names_to_ids
    }
    write_lua(config.output_dir / f'lua/Asset{key}.lua', data)

if __name__ == '__main__':
    run()