'''
Because wiki pages need to have unique names, we cannot always use exactly the 
item name given in the game because the game has items with duplicate names. 
This script assigns unique names to item ids so the wiki can identify the item 
properly.
'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import get_config_paths

# ------------------------------------------------------------------------------

# Manual overrides to force an id for a given name, for situations where item 
# ids are not being resolved otherwise by this script. Use as minimally as 
# possible; sometimes necessary for items seemingly duplicated.
priori = {
    'Cistanche': 16200019,
    'Egg': 19300011,
    'Fish Fossil Piece 1': 19210002,
    'Sand Hat': 12200011, # 21 different Sand Hats. NPC variants?
    'Sand Leek': 16200027,
    'Spoon': 15300022,
    'Tomato': 16200004,
    'Tomato and Egg Soup': 15000012
}

# One-off name variants. Assigning an id a variant name here will remove the 
# item from the pool of items that qualify for the base name.
non_standard_variant_names = {
    14000001: 'Water Tank (assembly)',
    14000044: 'Drill Arm (assembly)',
    15000124: 'Spicy Bean Paste (dish)',
    15000170: 'Spicy Bean Paste (ingredient)',
    15600005: 'Passya Game Kid (toy)',
    19200004: 'Processor (material)',
    19800034: 'Plasticizer (material)',
    19810052: 'Train Model (crafted)',
    85000124: 'Spicy Bean Paste (book for dish)',
    85000170: 'Spicy Bean Paste (book for ingredient)'
}

# ------------------------------------------------------------------------------

def main():
    items = DesignerConfig.ItemPrototype

    name_to_items = defaultdict(list)
    for item in items.values():
        base_name = texts[item['nameId']]['text']

        if "￥not use￥" in base_name:
            continue

        name = preemptively_choose_variant_name(item, base_name, texts)
        name_to_items[name].append(item)

    for name, id_ in priori.items():
        if id_ is None:
            if name in name_to_items:
                name_to_items.pop(name)
        else:
            name_to_items[name] = [items[id_]]

    result = {}
    for name, name_items in name_to_items.items():
        if not name:
            continue
        # Only one candidate for this item name. Easy.
        if len(name_items) == 1:
            item = name_items[0]
            result[name] = item['id']
        # Multiple candidates for this item name. 
        else:
            # Find out if some of these items are variants for which we can 
            # programatically determine an alternative name, i.e., "Swan Necklace"
            # into "Swan Necklace (Fang)".
            items_by_variant_name = defaultdict(list)
            for item in name_items:
                variant_name = choose_variant_name(item, name)
                items_by_variant_name[variant_name].append(item)
            
            for variant_name, variant_items in items_by_variant_name.items():
                if len(variant_items) == 1:
                    variant_item = variant_items[0]
                    result[variant_name] = variant_item['id']
                # We still have more than one item in this variant group.
                else:
                    print(f'Warning: More than one item for {variant_name}, attempting to resolve...')
                    # See if we can figure out the "right" one to use.
                    variant_item = choose_item(variant_items, texts)
                    if variant_item is None:
                        min_id = min([i["id"] for i in variant_items if "id" in i])
                        print(f'Could not resolve: {variant_name}; using lowest item ID {min_id}. \n')
                        result[variant_name] = min_id
                    else:
                        result[variant_name] = variant_item['id']

    dump_result(result)
    print(f'Output results for {len(result.keys())} out of {len(items)} items.')

# Names that the item should be assigned even if there isn't a conflict with another
# item.
def preemptively_choose_variant_name(item, base_name, texts):
    mip = item['maleIconPath'].lower()
    tags  = item['tags']

    if item['id'] in non_standard_variant_names:
        return non_standard_variant_names[item['id']]
    
    if item['id'] > 70000000 and item['id'] < 80000000 and 5 in tags:
        return f'{texts[item['nameId']]['text']} (Style)'
    
    if item['id'] > 81000000 and 5 in tags:
        return f'{texts[item['nameId']]['text']} (Book)'

    # Almost all pet accessories share names with at least one other pet accessory/item.
    if mip.startswith('i_petaccessory'):
        for key in pets_with_accessories.keys():
            if key in mip:
                return f'{base_name} ({pets_with_accessories[key]})'
    
    return base_name

def choose_variant_name(item, base_name):
    # Chromium Steel Bearings, possibly mismarked with tag 5?
    if id == 19112011:
        return base_name
    
    mip = item['maleIconPath'].lower()
    if mip is None: return base_name

    # Recipe books have the same names as the items they teach the builder to
    # produce. Most will have been caught by the preemptive name variant method,
    # but there are still a few left.
    if mip.startswith("item_book") or mip.startswith('book_') or mip == "item_instructionbook":
        if not base_name.lower().endswith('(book)'):
            return f'{base_name} (Book)'
    
    # DLC outfits for different NPCs often have the same names as each other, and as
    # the corresponding player outfits. Append the NPC name to resolve.
    if 'dlc' in mip:
        for character_name in dlc_outfit_characters:
            if character_name.lower() in mip:
                return f'{base_name} ({character_name})'
    
    return base_name

def choose_item(items, texts):
    conditions = [
        lambda item: item['maleIconPath'].lower() != 'null',
        lambda item: texts[item['infoId']]['text'],
        lambda item: item['id'] < 20000000
    ]
    for condition in conditions:
        items = [item for item in items if condition(item)]
        if len(items) == 0:
            print(f'Warning: No items meet conditions.')
            return None
        if len(items) == 1:
            return items[0]
    
    # Items with color variants often use the same maleIconPath with a number 
    # appended. We'll use the base (lowest number) item to refer to all
    # color variants.
    lowest_version      = None
    lowest_version_item = None
    common_base_mip     = None

    # Favors lowest ID item, in the event that the mips are all the same.
    items = sorted(items, key=lambda x: (x['id']))
    for item in items:
        mip           = item['maleIconPath'].lower()
        version_match = re.search(r'_(([0-9]+_?)+)$', mip)

        if version_match:
            version_str = version_match.group(1)
            item_version = float('.'.join(version_str.split('_')))
            base_mip = re.sub(r'(_[0-9]+)+$', '', mip)
        else:
            item_version = 0
            base_mip = mip

        if common_base_mip is None:
            common_base_mip = base_mip
        elif base_mip != common_base_mip:
            print(f'Warning: {base_mip} not equal to {common_base_mip}; not color variants.')
            lowest_version_item = None
            break

        if lowest_version is None or item_version < lowest_version:
            lowest_version = item_version
            lowest_version_item = item
    
    return lowest_version_item