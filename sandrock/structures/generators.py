'''
Parses "generators" (GeneratorGroup), a data structure that determines 
probabilities for a set of outcomes. This is used to randomize items, 
equipment affixes, and equipment attributes.

GeneratorGroup -> GeneratorGroupElement -> IdWeight: Affix, Attr, Item
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths

from pathvalidate import sanitize_filename
import re

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

# ------------------------------------------------------------------------------

class _GeneratorGroupElement:
    def __init__(self, data: dict) -> None:
        self._id_weights: list = data['idWeights']

        self.outcomes: list[Affix | Attr | Item] = [
            _IdWeight.from_data(id_weight, self) for id_weight in self._id_weights
        ]
    
    @cached_property
    def has_single_outcome(self) -> bool:
        return len(self.outcomes) == 1

    @cached_property
    def lines(self) -> list[str]:
        lines = []

        for outcome in self.outcomes:
            lines += outcome.lines

        return lines
    
    @cached_property
    def total_weight(self) -> int:
        return sum([outcome.weight for outcome in self.outcomes])

# ------------------------------------------------------------------------------

class _IdWeight:
    @classmethod
    def from_data(cls, data: dict, element: _GeneratorGroupElement) -> Affix | Attr | Item:
        id = data['id']

        if id in DesignerConfig.Generator_Affix:
            return Affix(element, data)
        elif id in DesignerConfig.GeneratorAttr:
            return Attr(element, data)
        elif id in DesignerConfig.Generator_Item:
            return Item(element, data)
        else:
            raise ValueError(f"Unknown ID: {id}")

    def __init__(self, element: _GeneratorGroupElement, data: dict) -> None:
        self.element: _GeneratorGroupElement = element
        self.data = data

        self.id = data['id']
        self.luck_factor = data['luckFactor']
        self.weight = data['weight']
    
    @cached_property
    def percent_chance_str(self) -> str:
        return f'{self.probability:.0%}'
    
    @cached_property
    def probability(self) -> float:
        return self.weight / self.element.total_weight if self.element.total_weight > 0 else 0.0

# ------------------------------------------------------------------------------

class Affix(_IdWeight):

    # Blue rarity, green affix
    # When Mining minerals, 5% chance to drop extra Rare ore.
    #
    # Purple rarity, double purple affix
    # Mining minerals When Stamina is consumed, there is a 5% chance to return 6 points.
    # Use tools When Stamina is consumed, there is a 5% chance to return 6 points.
    #
    # Mining minerals efficiency +9%
    #
    # Blue affix
    # Mining minerals When Stamina is consumed, there is a 5% chance to return 4 points.
    #
    # Purple affix
    # When Quarry, 9% chance to drop extra Resources.
    #
    # Blue, purple
    # When Quarry, 7% chance to drop extra Resources.
    # Use tools When Stamina is consumed, there is a 5% chance to return 6 points.

    types = {
        1: 'Common',
        2: 'Outstanding',
        3: 'Perfect',
        4: 'Rare',
    }

    grades = {
        1: 'Outstanding',
        2: 'Perfect',
        3: 'Rare'
    }

    affix_types = {
        2: 'Weapon',
    }

    def __init__(self, element: _GeneratorGroupElement, data: dict) -> None:
        super().__init__(element, data)

        self.id: int              = data['id']
        self.asset_data: dict     = DesignerConfig.Generator_Affix[self.id]

        self.affix_type: int      = self.asset_data['affixType']
        self.default_lock: int    = self.asset_data['defaultLock']
        self.des_id: int          = self.asset_data['desId']
        self.des_param: dict      = self.asset_data['desParam']
        self.gen_dist_params: list = self.asset_data['genDistParams']
        self.group: int           = self.asset_data['group']
        self.param: int           = self.asset_data['param']
        self.priority: int        = self.asset_data['priority']
        self.require_grade: int   = self.asset_data['requireGrade']
        self.require_level: list  = self.asset_data['requireLevel']
        self.string_param: dict   = self.asset_data['stringParam']

    @cached_property
    def description(self) -> str:
        # Ex: "After defeating an enemy, gain a {0:P0} chance of increasing {2} by {1:F0}."
        description_format = text(self.des_id)

        # print(self.id)
        # print(description_format)
        # print(self.description_params)

        # Locate interpolation matches {} in the description format
        matches = re.findall(r'\{(\d+)(:)*([^}]*)?\}', description_format)

        # Replace matches with corresponding parsed parameters
        formatted_description = description_format
        for match in matches:
            index, _, param_format = match
            index = int(index)
            param = self.description_params[index] if index < len(self.description_params) else 0 # 'Unknown'

            if param_format:
                full_match = f'{{{index}:{param_format}}}'
                if param_format.startswith('P'):
                    formatted_param = f'{(param * 100):.0f}%'
                else:
                    formatted_param = param
            else:
                full_match = f'{{{index}}}'
                formatted_param = param
            
            formatted_description = formatted_description.replace(
                full_match, str(formatted_param), 1
            )

        return f'{self.id}: {formatted_description}'
    
    @cached_property
    def description_params(self) -> str:
        parsed_params = []

        for param in self.des_param['data']:
            data_type, value = param.split('_', 1)

            match data_type:
                case 'f':  # float
                    parsed_params.append(float(value))
                case 'i':  # int
                    parsed_params.append(int(value))
                case 's':  # ?
                    parsed_params.append(value)
                case 't':  # text id
                    parsed_params.append(text(int(value)))
                case _:  # handle unknown data types
                    raise ValueError(f"Unknown data type: {data_type} for param {param}")
        
        return parsed_params
    
    @cached_property
    def max_level(self) -> int:
        if len(self.require_level) > 1:
            return max(self.require_level)
        
        return 'None'
    
    @cached_property
    def min_level(self) -> int:
        return min(self.require_level)
    
    @cached_property
    def required_grade(self) -> str:
        return self.require_grade
    
    @cached_property
    def type(self) -> str:
        return self.types[self.affix_type]
    
    def print(self) -> None:
        print(f'{self.type} affix {self.id}: {self.description}')
        print(f'  Require Grade: {self.require_grade}')
        print(f'  Require Level: {self.require_level}')

# ------------------------------------------------------------------------------

class Attr(_IdWeight):
    def __init__(self, element: _GeneratorGroupElement, data: dict) -> None:
        super().__init__(element, data)

        self.id: int              = data['id']
        self.asset_data: dict     = DesignerConfig.GeneratorAttr[self.id]

        self.attr_type: int       = self.asset_data['attrType']
        self.random_type: int     = self.asset_data['randomType']
        self.parameters: list     = self.asset_data['parameters']
        self.gain_type: int       = self.asset_data['gainType']
    
    @cached_property
    def parsed_attr_type(self) -> str:
        return attr_types.get(self.attr_type, 'unknown')
    
    def print(self) -> None:
        print(f'Attr {self.id} ({self.parsed_attr_type}): {self.parameters}')
    
# ------------------------------------------------------------------------------

class Item(_IdWeight):

    random_types = {
        0: 'Number',
        2: 'Normal',
        3: 'Uniform / Uniform Float',
    }

    def __init__(self, element: _GeneratorGroupElement, data: dict) -> None:
        super().__init__(element, data)

        self.id: int              = data['id']
        self.asset_data: dict     = DesignerConfig.Generator_Item[self.id]

        self.item_id: int         = self.asset_data['itemId']
        self.random_type: int     = self.asset_data['randomType']
        self.parameters: list     = self.asset_data['parameters']
        self.gen_grade: int       = self.asset_data['genGrade']
    
    @cached_property
    def lines(self) -> list[str]:
        descriptive_parts = []

        if self.min_count != 1 or self.max_count != 1:
            if self.min_count == self.max_count:
                descriptive_parts.append(str(self.min_count))
            else:
                descriptive_parts.append(f'{self.min_count} - {self.max_count}')

        if self.probability != 1:
            descriptive_parts.append(self.percent_chance_str)
        
        if len(descriptive_parts) > 0:
            descriptive = f'|{", ".join(descriptive_parts)}'
        else:
            descriptive = ''
        
        return [f'{{{{i2|{self.name}{descriptive}}}}}']

    @cached_property
    def max_count(self) -> int:
        _, max = self.min_max_count
        return max
    
    @cached_property
    def min_count(self) -> int:
        min, _ = self.min_max_count
        return min
    
    @cached_property
    def min_max_count(self) -> tuple[int, int]:
        assert self.random_type in self.random_types, f"Unknown random type: {self.random_type}"

        if self.random_type == 0:
            min = self.parameters[0]
            max = self.parameters[0]
        elif self.random_type == 2:
            min = self.parameters[0] - self.parameters[1]
            max = self.parameters[0] + self.parameters[1]
        elif self.random_type == 3:
            min = self.parameters[0]
            max = self.parameters[1]
        else:
            raise ValueError(f"Unhandled random type: {self.random_type}")
        
        min_rounded = int(min) if min == int(min) else int(min) // 1
        max_rounded = int(max) if max == int(max) else int(max) + 1
        return (min_rounded, max_rounded)

    @cached_property
    def name(self) -> str:
        return text.item(self.item_id)

    def print(self) -> None:
        print(f'Item {self.id} ({self.item_id}): {self.parameters}')

# ------------------------------------------------------------------------------

class GeneratorGroup:
    @classmethod
    def print_generators_for_item_id(cls, item_id: int) -> None:
        lines = [f'== Item {text.item(item_id)} ==']
        generator_item_ids = [id for id, gen_item in DesignerConfig.Generator_Item.items() if gen_item['itemId'] == item_id]
        generator_group_ids = []

        for id, gen_group in DesignerConfig.GeneratorGroup.items():
            for element in gen_group['elements']:
                for id_weight in element['idWeights']:
                    if id_weight['id'] in generator_item_ids:
                        generator_group_ids.append(id)
                        break
        
        generator_group_ids = list(set(generator_group_ids))
        for id in generator_group_ids:
            generator = GeneratorGroup(id)
            lines.append(f'== Generator {id} ==')
            lines += generator.lines
            lines.append('')
        
        print('\n'.join(lines))
    
    def __init__(self, id: int) -> None:
        self.id: int              = id
        self.asset_data: dict     = DesignerConfig.GeneratorGroup[id]

        self.element_datas: list  = self.asset_data['elements']
        self.elements: list       = [_GeneratorGroupElement(data) for data in self.element_datas]

    @cached_property
    def lines(self) -> None:
        lines = []

        for element in self.elements:
            lines += element.lines
        
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.lines))
