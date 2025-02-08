'''
Output assets that correspond one-to-one with a designer_config file.

Requires:
    - designer_config
    - sceneinfo
    - text
'''

from sandrock         import *
from sandrock.preproc import get_config_paths

# ------------------------------------------------------------------------------

# Using the number-to-word translations that are already used in the wiki. Can't 
# find interpretations of these numbers in the game code; how did they know what
# they represent?

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

cooking_types = {
    0: 'Steamer',
    1: 'Pot',
    2: 'FryingPan',
    3: 'Oven'
}

exhibition_types = {
    0: 'Fossil' # ?
}

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

sizes = {
    0: 'Small',
    1: 'Medium',
    2: 'Large',
    3: 'None'
}

weapon_types = {
    0: 'Sword',
    1: 'Hammer',
    2: 'Lance',
    3: 'Dagger'
}

attr_types = {
    0: 'nodrop',
    1: 'attack_l',
    2: 'attack_u',
    3: 'durability',
    4: 'element_fire',
    5: 'element_water',
    6: 'element_acid',
    7: 'element_electricity',
    8: 'element_poison',
    10: 'critical_rate',
    11: 'critical_damage',
    13: 'magazine',
    14: 'armor',
    15: 'resist_fire',
    16: 'resist_water',
    17: 'resist_acid',
    18: 'resist_electricity',
    19: 'resist_poison',
    20: 'hp',
    21: 'strength',
    22: 'endurance',
    23: 'lv',
    24: 'beaten_ratio',
    25: 'lucky',
    26: 'machine_plugins_sand',
    27: 'machine_plugins_temperature',
    28: 'machine_plugins_water',
    29: 'machine_plugins_power',
    30: 'machine_plugins_powerstorage',
    32: 'machine_plugins_gradechance',
    33: 'machine_plugins_doublecount',
    35: 'machine_plugins_reduceslot',
    38: 'element_sword',
    39: 'element_hammer',
    40: 'element_blade',
    41: 'element_lance',
    42: 'element_hand',
    43: 'resist_sword',
    44: 'resist_hammer',
    45: 'resist_blade',
    46: 'resist_lance',
    47: 'resist_hand',
    48: 'endurance_recover',
    49: 'attackEnhancement',
    50: 'remoteEnhancement',
    51: 'brokeStoicDam',
    52: 'levelThreshold',
    53: 'crushDam',
    54: 'hpMinimal',
    55: 'lifeDrainRatio',
    56: 'invincible_ratio',
    57: 'dashDis_ratio',
    58: 'dodge_level',
    59: 'cp_cd',
    60: 'cp_cost_reduce_ratio',
    63: 'voxel_dig_range',
    64: 'voxel_dig_range_mul',
    65: 'voxel_dig_count_mul',
    66: 'gather_attack',
    67: 'gather_attack_mul',
    68: 'sand_attack',
    69: 'sand_attack_mul',
    72: 'product_queue_count',
    73: 'product_count',
    74: 'product_grade_Q_up',
    75: 'product_speed_up',
    76: 'product_count_up',
    77: 'fuel',
    78: 'fuel_cost_deduct',
    79: 'water',
    80: 'water_cost_deduct',
    81: 'manure',
    82: 'manure_cost_deduct',
    83: 'manure_extra_up',
    84: 'grow_speed_up',
    87: 'fish_point',
    88: 'fish_max',
    89: 'fish_range'
}

gain_types = {
    0: 'A',
    1: 'B'
}

pages = {
    'AssetAbandonedDungeonRuleDataAbandonedDungeon': [
        ('scene', lambda item: sceneinfo.scene_system_name(item['scene'])),
        'keyLevel',
        'treasureItem',
        'treasureData'
    ],
    'AssetAttrGeneratorConfigGenerator_Attr': [
        'id',
        ('attrType', lambda item: attr_types[item['attrType']]),
        ('randomType', lambda item: random_types[item['randomType']]),
        ('parameters', lambda item: {i + 1: par for i, par in enumerate(item['parameters'])}),
        ('gainType', lambda item: gain_types[item['gainType']]),
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
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
    'AssetEquipmentProtoEquipment': [
        'id',
        'equipPart',
        'accPart',
        'equipMutexes',
        'attachIDs'
    ],
    'AssetExhibitionItemBaseDataExhibitionItem': [
        'id',
        ('type', lambda item: exhibition_types[item['type']]),
        ('size', lambda item: sizes[item['size']]),
        'assetName',
        'prizeReputation',
        ('Id', lambda item: item['id']), # TODO: Remove redundancy.
    ],
    'AssetGeneratorGroupConfigGeneratorGroup': [
        'id',
        'elements'
    ],
    'AssetGrowthDataGrowthModelConfig': [
        'id',
		'startLevel',
		'endLevel',
		'startNum',
		'endNum',
		'enp'
    ],
    'AssetGrowthItemItemGrowth': [
        'growthType',
        'attrType',
        'grade'
    ],
    'AssetGunDataItemGun': [
        'id',
        'ammoId',
        'magazine',
        'isSingleFire',
        'fireInterval',
        'cursorIndex',
        'anim',
        'aimMoveSpeed',
        'emptyAmmoSound',
        'accuracyMin',
        'accuracyMax',
        'accuracyReducePerFire',
        'accuracyChangeTime',
        'fireAimMove'
    ],
    'AssetIllustrationConfigIllustration': [
        'id',
        'nameId',
        'catalogId',
        # 'order' I give up. No idea how to produce the in-game encyclopedia order.
    ],
    'AssetIllustrationCatalogConfigIllustrationCatalog': [
        'id',
        'parentId',
        'nameId',
        'iconName',
        ('Pathea.DesignerConfig.IIdConfig.Id', lambda item: item['id'])
    ],
    'AssetItemAttrGrowthDataAttrGrowth': [
        'id',
        'growthType',
        'itemLevel',
        'baseSceneSlotGroupId',
        'addSceneSlotGroupId',
        'addSceneSlotLimits'
    ],
    'AssetItemGeneratorConfigGenerator_Item': [
        'id',
        'itemId',
        'randomType',
        'parameters',
        'genGrade'
    ],
    'AssetItemPrototypeItem': [
        'id',
        'maleIconPath',   # Default icon path.
        'femaleIconPath', # Female variant icon path.
        'nameId',
        ('name', lambda item: text(item['nameId'])),
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
    'AssetMeleeWeaponProtoMeleeWeapon': [
        'id',
        ('weaponType', lambda item: weapon_types[item['weaponType']]),
        'maxCombo',
        'comboIDs_2',
        'comboIDs_3',
        'comboIDs_4',
        'comboIDs_5',
        'dashAttachCpCost',
        'dashAttackIDs'
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
    'AssetReadingConfigReadingBook': [
        'id',
        'bookId',
        'translateId'
    ],
    'AssetRefineConfigRefine': [
        'id',
        'matsGradeUp',
        'matsLevelUp',
        'maxRefineLevel'
    ],
    'AssetRequireProtoRequire': [
        'id',
        'requireLevel'
    ],
    'AssetRestoreConfig': [
        'id',
        'order',
        'displayPrefabName',
        ('sizeType', lambda item: sizes[item['sizeType']]),
        ('partsItemIds', lambda item: {i + 1: part for i, part in enumerate(item['partsItemIds'])}),
        'costTime',
        'extraItemCost'
    ],
    'AssetSceneConfigSceneConfig': [
        ('id', lambda item: item['scene']),
        'nameId',
        ('name', lambda item: text(item['nameId'])),
        ('scene', lambda item: sceneinfo.scene_system_name(item['scene']))
    ],
    'AssetScreeningConfigScreening': [
        'id',
        'inputCount',
        ('generatorIds', lambda item: {i + 1: gen for i, gen in enumerate(item['generatorIds'])}),
        ('itemResultDes', lambda item: {i + 1: des for i, des in enumerate(item['itemResultDes'])}),
        'costMinutes',
        'exp'
    ]
}

def modify_attachment(attachment: dict) -> dict:
    attachment['type'] = mail_template_attachment_types[attachment['type']]
    return attachment

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
                'name': page_name,
                'key': key,
                'configList': items
            }
            write_lua(config.output_dir / f'lua/{page_name}.lua', data)

if __name__ == '__main__':
    run()
