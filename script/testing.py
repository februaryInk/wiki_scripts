'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths
from sandrock.structures.conversation import *
from sandrock.structures.story    import *
from sandrock.preproc             import get_interest_points
from script.structures.generators import *

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

def run() -> None:
    # print_mission(1600391)
    # print_conv_segment(18366)
    # print_conv_segment(4544)
    # # print_mission(1600392)
    # print_scenes()
    # # print_items_with_item_tag(86)
    # print_mission_names()
    # # # m = story.get_mission(1100106)
    # print(json.dumps(story.get_mission_names(), indent=2))
    # # # print_scenes()
    # # print_generator_items(11086)
    # # print_generator_items(20990037)
    # # print('----')
    # # print_generator_items(20900021)
    # # print_generator_items(13002)
    # # print_generator_items(20900034)
    # # print_generator_items(12030)
    # print_generator_items(15105)
    # print_conv_segment(1708)
    # m = story.get_mission(1800398)
    # m.print()   
    # m = story.get_mission(1500403)
    # m.print()
    # # print_npc_names()
    # print_items_with_item_tag(1122)

    story = Story()
    m = story.get_mission(1800528)
    # m = story.get_mission(1100071)
    m.print()
    

def print_generator(id: int) -> None:
    generator = GeneratorGroup(id)
    generator.print()

def print_refine_type() -> None:
    refines = DesignerConfig.Refine

    for id, refine in refines.items():
        if refine['refineType'] == -1:
            print(f'{refine["refineType"]}: {text.item(id)}')
    
    for id, refine in refines.items():
        if refine['refineType'] == 0:
            print(f'{refine["refineType"]}: {text.item(id)}')
    
    equipment = DesignerConfig.Equipment
    for id, equip in equipment.items():
        print(f'{id}: {text.item(id)}')


def print_dialogue(npc_name: str) -> None:
    social_levels = DesignerConfig.SocialLevel
    social_level_map = {level['level']: text(level['nameId']) for level in social_levels}
    print(json.dumps(social_level_map, indent=2))
    # Find the first match in DesignerConfig.Npc
    npc_id = next((npc_id for npc_id, npc in DesignerConfig.Npc.items() if text(npc['nameID']) == npc_name), None)
    print(f'NPC ID: {npc_id}')
    talks = [talk for talk in DesignerConfig.GeneralDialog if talk['id']['id0'] <= npc_id <= talk['id']['id1']]

    assert len(talks) == 1, f'Found {len(talks)} talks for {npc_name}'
    talk = talks[0]

    print('==General Dialog==')
    normalTalkData = talk['normal']['talkData']

    for talkData in normalTalkData:
        relation = social_level_map[talkData['relation']]
        print(f'==={relation}===')

        for segment_id_str in talkData['dialogUnit'].split(';'):
            segment_id = int(segment_id_str.split('*')[0])
            print_conv_segment(segment_id)

def print_monster_spawns() -> None:
    monsters = DesignerConfig.Monster
    count = 0

    for interest in get_interest_points():
        behav = read_json(interest['behaviour'])
        if interest['type'] == 'MonsterMarkSpawnerExecutor':
            count += 1
            for info in behav['spawnerMonsterInfos']:
                monster = monsters[info['protoId']]
                min_level = info['level']['x']
                max_level = info['level']['y']
                print(f'{text(monster["nameId"])}, {min_level}-{max_level}')
    print(f'We have {count} MonsterMarkSpawnerExecutor interests')



def read_blueprints() -> None:
    blueprints = DesignerConfig.Creation
    for blueprint in blueprints:
        if blueprint['fromMachineLevel'] > 3:
            print(f'{blueprint["id"]}: {text.item(blueprint["itemId"])}')

def read_gift_content(id: int) -> None:
    gift = DesignerConfig.FestivalGift[id]
    npc = text(gift['npcId'])
    note = text(gift['dscId'])
    drops = gift['drops'].split(',')
    print(f'{npc}: {note}')
    for drop in drops:
        id_str, count_str = drop.split('_')
        print(f'{text.item(int(id_str))} x{count_str}')

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

def print_npc_names() -> None:
    for npc in sorted(DesignerConfig.Npc, key=lambda npc: npc['id']):
        print(f'{npc["id"]}: {text(npc["nameID"])}')

def print_scenes() -> None:
    for scene in sorted(DesignerConfig.Scene, key=lambda item: item['scene']):
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
