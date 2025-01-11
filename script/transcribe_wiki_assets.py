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

cooking_types = [
    'Steamer',
    'Pot',
    'FryingPan',
    'Oven'
]

gen_grades = {
    0: 'Grade_0',
    1: 'Grade_1',
    2: 'Grade_2',
    3: 'Grade_3',
    4: 'Max'
}

mail_template_attachment_types = {
    0: 'Money',
    1: 'Item',
    3: 'MissionAutoReceive',
    5: 'Favor'
}

random_types = {
    0: 'Num',
    1: 'Uniform',
    2: 'Normal',
    3: 'UniformFloat'
}

pages = {
    'AssetAbandonedDungeonRuleDataAbandonedDungeon': [
        ('scene', lambda item: sceneinfo.scene_system_name(item['scene'])),
        'keyLevel',
        'treasureItem',
        'treasureData'
    ],
    'AssetCookingConfigCooking': [
        'id',
        ('isActive', lambda item: str(item['isActive'] == 1)),
        'outItemId',
        'costMinutes',
        'gainExp',
        ('formulaIds', lambda item: {1: item['formulaId']})
    ],
    'AssetCookingFormulaConfigCookingFormula': [
        'id',
        ('isActive', lambda item: str(item['isActive'] == 1)),
        ('disableTrying', lambda item: str(item['disableTrying'] == 1)),
        ('cookingType', lambda item: cooking_types[item['cookingType']]),
        ('materials', lambda item: {i + 1: mat for i, mat in enumerate(item['materials'])})
    ],
    'AssetDlcConfigDlc': [
        ('id', lambda item: item['dlc']),
        'nameId',
        'alwaysDisplay'
    ],
    'AssetGeneratorGroupConfigGeneratorGroup': [
        'id',
        ('elements', lambda item: transform_generator_group(item['elements'])),
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
    ],
    'AssetIllustrationConfigIllustration': [
        'id',
        'nameId',
        'catalogId',
        # 'order'
    ],
    'AssetIllustrationCatalogConfigIllustrationCatalog': [
        'id',
        'parentId',
        'nameId',
        'iconName',
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
    ],
    'AssetItemGeneratorConfigGenerator_Item': [ # AssetItemGeneratorConfigs
        'id',
        'itemId',
        ('randomType', lambda item: random_types[item['randomType']]),
        'parameters',
        ('parameters', lambda item: {i + 1: par for i, par in enumerate(item['parameters'])}),
        ('genGrade', lambda item: gen_grades[item['genGrade']]),
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
    ],
    'AssetItemPrototypeItem': [
        'id',
        'maleIconPath',   # Default icon path.
        'femaleIconPath', # Female variant icon path.
        'nameId',
        # ('name', lambda item: text(item['nameId'])),
        'infoId',
        'gradeWeight',
        'orderIndex',
        ('tags', lambda item: [tag_translations[tag] for tag in item['tags']]),
        'buyPrice',
        'sellPrice',
        'itemTag',
        'cantSold'
    ],
    'AssetMailTemplateDataMailTemplate': [
        'id',
        'title',
        'content',
        'sender',
        ('attachData', lambda item: [modify_attachment(att) for att in item['attachData']]),
        'cover'
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
    ],
    'AssetSceneConfigSceneConfig': [
        ('id', lambda item: item['scene']),
        'nameId',
        ('name', lambda item: text(item['nameId'])),
        ('scene', lambda item: sceneinfo.scene_system_name(item['scene']))
    ]
}

def modify_attachment(attachment: dict) -> dict:
    attachment['type'] = mail_template_attachment_types[attachment['type']]
    return attachment

def transform_generator_group(data):
    return {
        i + 1: {
            "idWeights": {
                j + 1: weight_entry
                for j, weight_entry in enumerate(entry["idWeights"])
            }
        }
        for i, entry in enumerate(data)
    }

def run() -> None:
    config_paths = get_config_paths()

    for key, path in config_paths['designer_config'].items():
        for page_name, required_attributes in pages.items():
            if page_name not in path:
                continue

            config_data = read_json(path)['configList']
            items       = []

            # The order of Encyclopedia items is a mystery to me, I don't know
            # how to match the in-game Encyclopedia.
            # if key == 'Illustration':
            #     config_data = [{**config, 'order': i + 1} for i, config in enumerate(config_data)]

            for element in config_data:
                item = {}

                for attribute in required_attributes:
                    if isinstance(attribute, str):
                        # If it's a simple attribute, copy it directly.
                        item[attribute] = element[attribute]
                    elif isinstance(attribute, tuple):
                        # If it's a transformation, apply it.
                        attr, transform = attribute
                        item[attr] = transform(element)

                items.append(item)

            if 'id' in items[0]:
                items = {item['id']: item for item in items}
                items = dict(sorted(items.items()))
            else:
                items = {i + 1: item for i, item in enumerate(items)}

            data = {
                'version': config.version,
                'key': key,
                'configList': items
            }
            write_lua(config.output_dir / f'lua/{page_name}.lua', data)

if __name__ == '__main__':
    run()
