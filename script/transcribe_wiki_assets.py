from sandrock import *
from sandrock.lib.text import load_text
from sandrock.preproc import get_config_paths

# Using the tag translations that are already used in the wiki. Can't find 
# "official" interpretations of tag numbers in the game code.
tag_translations = {
    # Assembly Station products, including Machines.
    0: 'Creation',
    # Equipables: Clothing, Accessories, Weapons, Sandfish Traps. Can also be NPC clothing.
    1: 'Equipment',
    # Consumables: Food, Medicine, Concealer, Yakmel Milk...
    2: 'Food',
    # Furniture, whole Relics.
    3: 'Furniture',
    # Base Resources: Currency, raw Resources, machined Materials, Ingredients, Relic pieces,
    # Seeds, Bait, Mission items, Toys...
    4: 'Material',
    # Items with interfaces/that open UI elements?: Books, Recipe Books, Machines (placeable 
    # versions, distinct from tag 0 Machines), Animals (which have interfaces for naming them). 
    # Currencies, for some reason?
    5: 'HiddenHandBook',
    # Unused/Removed.
    # 6: 'Refine',
    # Unused/Removed.
    # 7: 'MachinePlugin',
    # Hand Equipables: Tools, Weapons, Meatballs.
    8: 'Weapon',
    # Seasonings, loosely. All also have tag 4.
    9: 'Seasoning',
    # Non-Seasonings Ingredients, Fish. All also have tag 4.
    10: 'Ingredient',
    # Unused/Removed.
    # 11: 'ExperimentCore',
    # Unused/Removed.
    # 12: 'Max'
}

pages = {
    'AssetIllustrationConfigIllustration': [
        'id',
        'nameId',
        'catalogId'
    ],
    'AssetIllustrationCatalogConfigIllustrationCatalog': [
        'id',
        'parentId',
        'nameId',
        'iconName',
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
    ],
    'AssetItemPrototypeItem': [
        'id',
        'maleIconPath',   # Default icon path.
        'femaleIconPath', # Female variant icon path.
        'nameId',
        'infoId',
        'gradeWeight',
        'orderIndex',
        ('tags', lambda item: [tag_translations[tag] for tag in item['tags']]),
        'buyPrice',
        'sellPrice',
        'itemTag',
        'cantSold'
    ],
    'AssetNpcProtoDataNpc': [
        'id',
        'templetID',
        'nameID',
        'identityID',
        'birthday',
        'homeScene',
        'interactChoice',
        'height',
        'weight',
        'backgrounds'
    ]
}

def run() -> None:
    config_paths = get_config_paths()

    for key, path in config_paths['designer_config'].items():
        for page_name, required_attributes in pages.items():
            if page_name not in path:
                continue

            config_data = read_json(path)['configList']
            items       = []

            for element in config_data:
                item = {}

                for attribute in required_attributes:
                    if isinstance(attribute, str):
                        # If it's a simple attribute, copy it directly.
                        item[attribute] = element[attribute]
                    elif isinstance(attribute, tuple):
                        # If it's a transformation, apply it.
                        key, transform = attribute
                        item[key] = transform(element)

                items.append(item)

            # The order of Encyclopedia items does matter, but Lua tables do not 
            # keep order, so it is important to use a list instead.
            if 'id' in items[0] and key != 'Illustration':
                items = {item['id']: item for item in items}

            data = {
                'version': config.version,
                'key': key,
                'configList': items
            }
            write_lua(config.output_dir / f'lua/{page_name}.lua', data)

if __name__ == '__main__':
    run()
