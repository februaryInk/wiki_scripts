'''

Requires:
    - designer_config
    - home
    - text
'''

from sandrock.common              import *
from sandrock.lib.asset           import Asset, Bundle
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.text            import text

base_name = 'FurnitureData'

region_types = {
    0: 'Outdoor Floor', # Home Editor, not carried and placed by player.
    1: 'Outdoor Floor',
    2: 'Indoor Floor',
    3: 'Indoor Wall',
    5: 'Factory Wall',
    6: 'Factory Floor',
    7: 'Greenhouse Floor'
}

item_tags = {
    1: 'Storable',
    207: 'Melee Weapon',
    208: 'Ranged Weapon',
    209: 'Head',
    210: 'Torso',
    211: 'Legs',
    212: 'Feet',
    216: 'Readable Book',
    231: 'Decoration',
    237: 'Banquet Cake',
    356: 'Fish',
    357: 'King Fish',
    362: 'Jewelry or Gem',
    368: 'Terrarium Creature',
    214: 'Prepared Food',
}

item_config: Asset    = DesignerConfig.ItemPrototype
# TODO: Use this plus the tags to display what can be put in storage slots on the wiki.
storage_config: Asset = DesignerConfig.StorageConfig # Storage slots.
unit_config: Asset    = DesignerConfig.UnitConfig # Furniture configurations.
home_bundle: Bundle   = Bundle(config.assets_root / 'home') # Furniture sizes.

def run() -> None:
    furniture = {}
    furniture_size_assets = [asset for asset in home_bundle.behaviours if asset.name.startswith('HomeToolSetting')]

    furniture_sizes = {}
    for asset in furniture_size_assets:
        size_list = []
        for size in asset.data['list']:
            coords = size['localcoordinateList']
            coords.append({'row': 0, 'column': 0})

            x = len(set([coord['row'] for coord in coords]))
            y = len(set([coord['column'] for coord in coords]))
            z = len(set(coords))
            size_list.append([y, x, z])
    
        for item in asset.data['pairs']:
            furniture_sizes[item['itemId']] = size_list[item['rangeIndex']]

    for item in unit_config:
        if item['ID'] in furniture_sizes:
            size = furniture_sizes[item['ID']]
        else:
            print(f'Warning: No size data for {text.item(item["ID"])}')
            size = [1, 1, 1]

        furniture[item['ID']] = {
            'placement': get_placement_from_regions(item['regionTypes']),
            'unitType': item['unitType'],
            'size': size
        }

    
    data = {
        'version': config.version,
        'key': 'Furniture',
        'configList': furniture
    }
    write_lua(config.output_dir / f'lua/{base_name}.lua', data)

def get_placement_from_regions(regions: list[int]) -> str:
    if len(regions) == 1:
        return region_types[regions[0]]
    
    region_sets = {
        frozenset([2, 6]): 'Indoor Floor',
        frozenset([0, 1, 6]): 'Outdoor Floor',
        frozenset([0, 7]): 'Outdoor Floor',
        frozenset([0, 1, 2, 6]): 'Floor',
        frozenset([3, 5]): 'Wall'
    }
    
    for key, label in region_sets.items():
        if set(regions).issubset(key):
            return label

if __name__ == '__main__':
    run()
