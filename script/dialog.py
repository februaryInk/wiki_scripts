'''
Print character dialog.
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.lib.asset               import Asset, Bundle
from sandrock.lib.text                import load_text
from sandrock.structures.characters   import characters
from sandrock.structures.conversation import *
from script.structures.generators     import *

# ------------------------------------------------------------------------------

festival_bundle: Bundle = Bundle(config.assets_root / 'festival')

npc_name = 'Musa'

# ------------------------------------------------------------------------------

def run() -> None:
    print_pet_dialogs()

def print_festival_dialogs() -> None:
    festival_asset = next(asset for asset in festival_bundle.behaviours if asset.name == 'FestivalAsset')
    
    for festival in festival_asset.data['festivals']:
        festival_id = festival['festival']
        print('')
        print('')
        print(f'Festival ID {festival_id}: {text(festival["nameId"])}')

        for id, character in characters.items():
            festival_dialog = character.festival_dialog(festival_id)
            for line in festival_dialog:
                print(line)
        
        breakpoint()

    # npc_ids = [id for id, npc in DesignerConfig.Npc.items() if text.npc(id) == npc_name]

    # print_introductions()
    # read_chat_dialogue(npc_ids[0])

def print_introductions() -> None:
    dialog_sets = DesignerConfig.GeneralDialog._data

    # Sort by NPC name.
    dialog_sets.sort(key=lambda ds: text.npc(ds['id']['id0']))

    for dialog_set in dialog_sets:
        npc_id = dialog_set['id']['id0']
        npc_name = text.npc(npc_id)
        first = dialog_set['first']

        if first == '-1':
            print(f'{npc_name} has no first dialog.')
            continue

        segment_ids = [int(id) for id in first.split(',')]

        lines = []
        for segment_id in segment_ids:
            read_conv_segment(segment_id)

    print('\n'.join(lines))

def print_pet_dialogs() -> None:
    print(f'=== Followed by one or two pets ===')

    for id, character in characters.items():
        pet_one_dialog = character.pets_one_dialog()
        if pet_one_dialog:
            print('')
            for line in pet_one_dialog:
                print(line)

    print(f'=== Followed by three or more pets ===')

    for id, character in characters.items():
        pet_three_dialog = character.pets_three_dialog()
        if pet_three_dialog:
            print('')
            for line in pet_three_dialog:
                print(line)
    
    print('=== Special pet reactions ===')

    for id, character in characters.items():
        pet_special_dialog = character.pet_special_dialog()
        if pet_special_dialog:
            print('')
            for line in pet_special_dialog:
                print(line)

def read_chat_dialogue(npc_id: int) -> None:
    social_levels = DesignerConfig.SocialLevel
    social_level_map = {level['level']: {'count': 0, 'icon': 'star', 'name': text(level['nameId'])} for level in social_levels}
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
            read_conv_segment(segment_id)

def read_conv_builder(id: int) -> None:
    builder = ConvBuilder(id)
    builder.read()

def read_conv_segment(id: int) -> None:
    seg = ConvSegment(id, [])
    seg.print()

def read_conv_talk(id: int) -> None:
    talk = ConvTalk(id, [])
    talk.read()

if __name__ == '__main__':
    run()
