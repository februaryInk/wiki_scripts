'''
Usage:
    & "C:\Program Files\Python313\python.exe" -m script.asset_store_base_data_shop
'''
import json
import sys
from pathlib import Path
from sandrock.preproc  import get_config_paths
from sandrock          import *

attributes_by_file = {    
    'GroupProduct': [
        'id',
        'goods',
        'maxCount'
    ],
    'SellProduct': [
        'id',
        'itemId',
        'price',
        'currency',
        'globalStr',
        'unlockQuest',
        'unlockDlc',
        'regain',
        'refreshDays',
        'grade',
        'sellSeason',
        'isUnique'
    ],
    'StoreBaseData': [
        'id',
        'shopName',
        'npcId',
        'groupGoods',
        'goodsSetting',
        'recycle',
        'moneyStart',
        'moneyGain',
        'moneyTypes'
    ]
}

def main():
    config_paths = get_config_paths()

    for key, required_attributes in attributes_by_file.items():
        file = config_paths['designer_config'][key]
        items = load_asset(file)
        transcribed_items = {}

        for item in items.values():
            transcribed_item = {}

            for attribute in required_attributes:
                transcribed_item[attribute] = item[attribute]

            transcribed_items[transcribed_item['id']] = transcribed_item

        convert(transcribed_items, file, key)

def convert(items, file, key):
    name = file.split('\\')[-1].split('@')[0].strip()    

    data = {
        'version': f'V{config.version}',
        'name': name,
        'key': key,
        'configList': items
    }

    write_lua(config.output_dir / f'lua/{name}.lua', data)

def load_asset(file):
    data = json.load(Path(file).open(encoding='utf-8'))['configList']

    if 'id' in data[0]:
        data = {item['id']: item for item in data}

    return data

def to_lua(value, parent_indent=0, key=''):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, str):
        return str_to_lua(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, list):
        return array_to_lua(value, parent_indent, key)
    if isinstance(value, dict):
        return object_to_lua(value, parent_indent, key)
    if value is None:
        return 'nil'
    raise TypeError(repr(value))

def str_to_lua(s):
    assert '\\' not in s
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('"', '\\"')
    return f'"{s}"'

def array_to_lua(array, parent_indent, key):
    if not array:
        return '{}'
    indent = parent_indent + 1
    line = '{'
    for i, item in enumerate(array):
        line += to_lua(item, indent, key)
        if i < len(array) - 1:
            line += ','
    line += '}'
    return line

def object_to_lua(obj, parent_indent, _key):
    if not obj:
        return '{}'
    indent = parent_indent + 1
    line = '{'
    last_key = list(obj.keys())[-1]
    for key, value in obj.items():
        if not isinstance(key, str) or not key.isidentifier():
            key = f'[{key}]'
        line += f'{key}={str(to_lua(value, indent, key))}'
        if key != last_key:
            line += ','
    line += '}'
    return line

if __name__ == '__main__':
    main()