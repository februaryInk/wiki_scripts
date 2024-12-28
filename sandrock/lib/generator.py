'''
So, what is a generator? A dropper of items?
'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig

# ------------------------------------------------------------------------------

# Get the item ids for the generators in a select group.
def expand_generator(group_id: int) -> list[int]:
    item_ids = set()
    group    = DesignerConfig.GeneratorGroup[group_id]

    for gen_id in _group_generator_ids(group):
        generator = DesignerConfig.Generator_Item[gen_id]
        if generator['randomType'] == 0 and generator['parameters'][0] <= 0:
            continue
        item_ids.add(generator['itemId'])
    return sorted(item_ids)

def find_item_generators(item: dict | int) -> list[int]:
    if isinstance(item, dict):
        item = item['id']

    gen_ids = []
    for gen in DesignerConfig.Generator_Item:
        if gen['itemId'] == item:
            gen_ids.append(gen['id'])

    group_ids = []
    for group in DesignerConfig.GeneratorGroup:
        for gen_id in _group_generator_ids(group):
            if gen_id in gen_ids:
                group_ids.append(group['id'])

    return sorted(set(group_ids))

# -- Private -------------------------------------------------------------------

def _group_generator_ids(group: dict) -> list[int]:
    ids = []
    for element in group['elements']:
        for id_weight in element['idWeights']:
            if id_weight['weight'] <= 0:
                continue
            ids.append(id_weight['id'])
    return ids
