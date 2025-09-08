'''
Output assets that correspond one-to-one with a designer_config file.

Requires:
    - designer_config
    - sceneinfo
    - text
'''

from sandrock         import *
from sandrock.preproc import get_config_paths

npc_pet_ids = {
    1: 'Nemo',
    2: 'CoCo',
    3: 'Macchiato',
    4: 'Meerkat',
    5: 'Fennec Fox',
    6: 'Banjo',
    7: 'Gecko',
    8: 'X',
    100: 'Wild Yakmel',
    101: 'Wild Alpha Yakmel',
    102: 'Rocket Rooster',
    103: 'Cock-a-doodle-Doom',
    104: 'Boxing Jack',
    105: 'Tripion',
    106: 'Punished Tripion',
    107: 'Pensky',
    108: 'Thorny Jumper',
    109: 'Rockyenaroll',
    110: 'Alpha Rockyenaroll',
    111: 'Sandpony',
    112: 'Bumble Ant',
    113: 'Hot Honey BBQ Bumble Ant',
    114: 'Spoiled Honey Bumble Ant',
    115: 'Desert Hopper',
    116: 'Desert Viper',
    117: 'Supa Hot Hermicrab',
    118: 'Starby-on-a-Horse',
    119: 'Superstarby',
    120: 'Starby',
    # ID + 1000 = Shiny variant.
}

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
    1: 'Cooking Pot',
    2: 'Wok',
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

machine_types = {
    1: 'SyntheticTable',
    4: 'Furnace',
    5: 'Cutting',
    13: 'DryingStand',
    14: 'Tailor',
    15: 'Stirrer',
    16: 'Weapons',
    18: 'Jewelry',
    22: 'Grinder',
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

gender_types = {
    0: 'Male',
    1: 'Female'
}

pages = {
    'AssetAbandonedDungeonRuleDataAbandonedDungeon': [
        ('scene', lambda item: sceneinfo.scene_system_name(item['scene'])),
        'keyLevel',
        'treasureItem',
        'treasureData'
    ],
    'AssetActorProtoActor': [
        'id',
        ('gender', lambda item: gender_types[item['gender']]),
        'hp',
        'cp',
        'cpRecover',
        'sp',
        'ex',
        'att_l',
        'att_u',
        'def',
        'levelCritical',
        'levelCritiDam',
        'luckyPoint'
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
    'AssetCreationConfigCreation': [
        'id',
        'itemId',
        'nameId',
        'descriptionId',
        'makeTime',
        'fromMachineLevel',
        ('partIds', lambda item: {i + 1: part for i, part in enumerate(item['partIds'])}),
        ('page', lambda item: {i + 1: page for i, page in enumerate(item['page'])}),
        'handbookPriority',
        'rewardExp',
        'rewardProficiencyExp',
        'creationType'
    ],
    'AssetCreationPartConfigCreationPart': [
        'id',
        'material'
    ],
    'AssetDlcConfigDlc': [
        ('id', lambda item: item['dlc']),
        ('dlc', lambda item: text(item['nameId'])),
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
    'AssetFavorRelationInfluenceDataFavor_Influence': [
        'npcId',
        ('relationParams', lambda item: [{'socialLevel': param['socialLevel'], 'textId': param['textId']} for param in item['relationParams']]),
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
    'AssetInquiryDataBaseInquiry': [
        'id',
        'type',
        'para',
        ('npcId', lambda item: {i + 1: npc for i, npc in enumerate(item['npcId'])}),
        'weight',
        'missionRequire',
        'favorRequire',
        'cost',
        'addFavorRequire'
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
        # ('name', lambda item: text(item['nameId'])),
        'infoId',
        'gradeWeight',
        'orderIndex',
        ('tags', lambda item: [tag_translations[tag] for tag in item['tags']]),
        'buyPrice',
        'sellPrice',
        'itemTag',
        'cantSold',
        'cantRefine'
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
    'AssetMonsterProtoConfigMonster': [
        'id',
        'nameId',
        ('name', lambda item: text(item['nameId'])),
        'dropDatas',
        'monsterType'
    ],
    'AssetNpcProtoDataNpc': [
        'id',
        'templetID',
        'nameID',
        ('name', lambda item: text(item['nameID'])),
        'identityID',
        'birthday',
        'homeScene',
        'interactChoice',
        'height',
        'weight',
        'backgrounds'
    ],
    'AssetNpcRandomProtoDataRandomNPCData': [
        'id',
        'instanceIds',
        'initLevel',
        'nameRange',
        ('names', lambda item: [text(name_id) for name_id in range(item['nameRange']['x'], item['nameRange']['y'] + 1)]),
    ],
    'AssetPetConfigPetConfig': [
        'id',
        ('npcId', lambda item: find_pet_npc_id(item['id'])[0]),
        ('npcType', lambda item: find_pet_npc_id(item['id'])[1]),
        ('nameId', lambda item: find_pet_npc_name_id(item['id'])),
        'houseIds',
        'skillIds',
        'qualityWeights',
        'enableFoodType'
    ],
    'AssetPetLevelItemConfigPetLevelItemConfig': [
        'itemId',
        'expValue',
        'foodType'
    ],
    'AssetPetSkillConfigPetSkillConfig': [
        'skillId',
        'nameId',
        'descId',
        'level',
    ],
    'AssetReadingConfigReadingBook': [
        'id',
        'bookId',
        'translateId'
    ],
    'AssetRecycleConfigRecycle': [
        'id',
        'backCountPercent',
        'backGeneratorIds',
        ('itemResultDes', lambda item: {i + 1: des for i, des in enumerate(item['itemResultDes'])}),
        'costMinutes',
        'machineLevel',
        'orderId',
        'exp',
        'proficiencyExp'
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
    ],
    'AssetSyntheticConfigSynthetics': [
        'id',
        'itemId',
        'itemCount',
        'rawMaterials',
        ('fromMachineType', lambda item: machine_types[item['fromMachineType']]),
        'fromMachineLevel',
        ('makeTime', lambda item: int(item['makeTime'])),
        'orderId',
        'exp',
        'proficiencyExp'
    ],
    'AssetUseItemDataItemUse': [
        'id',
        ('name', lambda item: text(DesignerConfig.ItemPrototype[item['id']]['nameId'])),
        ('buffs', lambda item: [parse_buff(buff_id) for buff_id in item['buffIds']]),
        ('operators', lambda item: [parse_buff_string(op) for op in item['operators'].split(';') if op]),
    ]
}

buff_attributes = {
    'Att_l': 'Min Damage',
    'Att_u': 'Max Damage',
    'Cp': 'Endurance',
    'Def': 'Defense',
    'Hp': 'Health Points',
    'LevelCritical': 'Critical Rate',
    'LevelCritiDam': 'Critical Damage',
    'LuckyPoint': 'Luck',
    'ResistPoison': 'Poison Resistance',
    'Sp': 'Stamina',
}

buff_operators = {
    'BasePlus': '+',
    'FinalPlus': '+',
    'Plus': '+',
    'PlusByMaxPercent': '+%',
    'PlusRatio': '+%',
}

config_paths = get_config_paths()

def find_pet_npc_id(pet_id: int) -> int:
    npc_name = npc_pet_ids.get(pet_id, None)
    if npc_name is None:
        return (None, None)
    
    for id, npc in DesignerConfig.Npc.items():
        if text.npc(id) == npc_name:
            return (id, 'Npc')
    
    for id, npc in DesignerConfig.RandomNPCData.items():        
        if text.npc(npc['instanceIds']['x']) == npc_name:
            return (id, 'RandomNpc')    
    
    pet_asset = read_json(config_paths['pet']['PetAsset'])
    pet_asset_npcs = pet_asset['npcs']
    pet_asset_monsters = pet_asset['monsters']

    for n in pet_asset_npcs:        
        if (n['petId'] == pet_id):
            return (n['npcId'], 'Npc')
    
    for m in pet_asset_monsters:                    
        if(m['petId'] == pet_id):            
            return (m['randomNpcProtoId'], 'RandomNpc')
            
    raise ValueError(f'NPC for pet ID {pet_id} not found.')

def find_pet_npc_name_id(pet_id: int) -> str:
    npc_id = find_pet_npc_id(pet_id)

    if npc_id[0] is None:
        return None
    
    if npc_id[1] == 'Npc':
        return DesignerConfig.Npc[npc_id[0]]['nameID']
    elif npc_id[1] == 'RandomNpc':
        return DesignerConfig.RandomNPCData[npc_id[0]]['nameRange']['x']

def parse_buff(buff_id: int) -> dict:
    buff = DesignerConfig.ActorBuff[buff_id]
    lifetime = int(buff['lifeTime'])
    interval = int(buff['interval'])
    # Buffs in the traditional sense, where they modify a stat for a duration.
    modifiers = buff['modifiers'].split(';') if buff['modifiers'] else []
    # Effects that are applied once on use, like recovering health or stamina.
    operators = buff['operators'].split(';') if buff['operators'] else []
    icon_path = buff['iconPath']

    return {
        'lifetime': lifetime,
        'interval': interval,
        'icon_path': icon_path,
        'modifiers': [parse_buff_string(mod) for mod in modifiers],
        'operators': [parse_buff_string(op) for op in operators]
    }

# Critical Rate: +30%
# Lasts for 30 seconds
# Stamina: +50
# Every 5 seconds
# Critical Damage: +21%
# Heath Points: +100
# Endurance: +3 Every 2 seconds
def parse_buff_string(buff_str: str) -> dict:
    attr, oper, value = buff_str.split(',')

    readable_attr = buff_attributes[attr]
    readable_oper = buff_operators[oper]
    value = float(value)

    if readable_oper == '+%' or readable_attr in ['Critical Rate', 'Critical Damage']:
        value = round(value * 100, 2)
        if value.is_integer(): value = int(value)
        value = f'{value}%'
        readable_oper = '+'
    else:
        if value.is_integer(): value = int(value)
    
    return {
        'attribute': readable_attr,
        'operator': readable_oper,
        'value': value
    }


def modify_attachment(attachment: dict) -> dict:
    attachment['type'] = mail_template_attachment_types[attachment['type']]
    return attachment

def run() -> None:
    pet_asset = read_json(config_paths['pet']['PetAsset'])
    pet_asset_npcs = pet_asset['npcs']
    pet_asset_monsters = pet_asset['monsters']

    for n in pet_asset_npcs:
        npc_pet_ids[n['petId']] = text.npc(n['npcId'])
    
    for m in pet_asset_monsters:            
        npc_pet_ids[m['petId']] = text(DesignerConfig.Monster[m['protoId']]['nameId'])

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
