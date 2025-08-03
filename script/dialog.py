'''
Print a character's dialog.
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.lib.text                import load_text
from sandrock.structures.conversation import *
from script.structures.generators     import *

# ------------------------------------------------------------------------------

npc_name = 'Andy'

# ------------------------------------------------------------------------------

def run() -> None:
    npc_ids = [id for id, npc in DesignerConfig.Npc.items() if text.npc(id) == npc_name]

    print_introductions()

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
