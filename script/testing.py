'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths
from sandrock.structures.conversation import *
from sandrock.structures.story import *

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

def run() -> None:
    # print_mission(1600391)
    # print_conv_talk(6885)
    # print_mission(1600392)
    # builder = ConvBuilder(1)
    # builder.print()
    # print_scenes()
    print_generator_items(20900021)
    print('\n')
    print_generator_items(20940000)
    print(text.npc(8002))
    print(text.npc(8011))

def read_gift_content(id: int) -> None:
    gift = DesignerConfig.FestivalGift[id]
    npc = text(gift['npcId'])
    note = text(gift['dscId'])
    drops = gift['drops'].split(',')
    print(f'{npc}: {note}')
    for drop in drops:
        id_str, count_str = drop.split('_')
        print(f'{text.item(int(id_str))} x{count_str}')

def print_generator_items(id: int) -> None:
    generator_group = DesignerConfig.GeneratorGroup[id]
    generator_items = DesignerConfig.Generator_Item
    elements = generator_group['elements']

    for id_weights in [element['idWeights'] for element in elements]:
        total_weight = sum([id_weight['weight'] for id_weight in id_weights])
        for id_weight in id_weights:
            generator_item = generator_items[id_weight['id']]
            print(f'{text.item(generator_item['itemId'])} ({int(100 * id_weight["weight"] / total_weight)}%)')

def print_party_table():
    party_services = DesignerConfig.PartyService

    tiers = [tier for tier in party_services if tier['iconPath'] == 'I_Party_img_Food_00']

    tier_data = []

    for tier in tiers:
        name = text(tier['nameId'])
        price = tier['price']
        num_dishes, dish_ids_str = tier['datas']
        dish_ids = [int(dish_id) for dish_id in dish_ids_str.split(',')]

        tier_data.append({
            'name': name,
            'cost': price,
            'numDishes': num_dishes,
            'dishes': sorted([text.item(dish_id) for dish_id in dish_ids])

        })
    
    tier_data.sort(key=lambda tier: tier['cost'])

    lines = [
        '{| class="prettytable sortable floatheader" style="min-width:100%; text-align:center;"',
        '|+{{i2|Banquet Table|size=40px}}',
        '|-',
        '!Food Package',
        '!Price',
        '!Number of Dishes',
        '!Possible Dishes'
    ]

    for i, data in enumerate(tier_data):
        lines += [
            '|-',
            f'|{data["name"]}',
            f'|{data["cost"]}',
            f'|{data["numDishes"]}',
            '|{{cols|3|'
        ]

        dishes = data['dishes']

        if i > 0:
            previous_dishes = tier_data[i - 1]['dishes']
            absent_dishes = [dish for dish in previous_dishes if dish not in dishes]
            print(absent_dishes)
        #    assert len(absent_dishes) == 0, f'{absent_dishes} not found in {dishes}'
        #    dishes = [dish for dish in dishes if dish not in previous_dishes]

        for dish in dishes:
            lines.append(f';{{{{i2|{dish}}}}}')
        
        lines.append('}}')
    
    lines.append('|}')
    print('\n'.join(lines))

# "Why is --- a dirty word?"
def find_dirty_words(string: str) -> None:
    dirty_words_list = DesignerConfig.DirtyWords
    lower_string = string.lower()
    matches = [word['text'] for word in dirty_words_list if word['text'].lower() in lower_string]
    print(matches)

def print_conv_segment(id: int) -> None:
    seg = ConvSegment(id, [])
    seg.print()

def print_conv_talk(id: int) -> None:
    seg = ConvTalk(id, [])
    seg.print()

def print_items_with_item_tag(tag_id: int) -> None:
    for item in sorted(DesignerConfig.ItemPrototype, key=lambda item: item['id']):
        if tag_id in item['itemTag']:
            print(f'{item["id"]}: {text.item(item["id"])}')

def print_mission(id: int) -> None:
    story = Story()
    mission = story.get_mission(id)
    mission.print()

def print_mission_names() -> None:
    story = Story()
    misson_names = story.get_mission_names()
    print(json.dumps(misson_names, indent=2))

def print_scenes() -> None:
    for scene in sorted(DesignerConfig.Scene, key=lambda item: item['scene']):
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
