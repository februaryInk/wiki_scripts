'''
Birthday Gift results table generator.
'''

from __future__ import annotations

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *

# ------------------------------------------------------------------------------

def run() -> None:
    relationship_levels = {
        'NormalStranger': 'Stranger',
        'NormalAssociate': 'Buddy',
        'Friend': 'Friend',
        'FriendGood': 'Good Friend',
        'FriendClose': 'Best Friend',
        'FriendBest': 'BFF',
        'Lover': 'Boyfriend/Girlfriend',
        'LoverDeepest': 'Soulmate',
        'MateHappy': 'Husband/Wife',
        'MateHappiest': 'Full Devotion'
    }
    relationship_level_keys = list(relationship_levels.keys())

    # Character, prob, relationship level, items. Character col spans all rows relating to them.
    table_lines = [
        '{| class="prettytable" style="min-width:100%; text-align:center;"',
        '|-',
        '! Character',
        '! Relationship',
        '! Probability',
        '! Items',
        '|-'
    ]
    
    npc_id_to_name = {id: text.npc(id) for id in DesignerConfig.Npc.keys()}
    npc_id_to_name = dict(sorted(npc_id_to_name.items(), key=lambda item: item[1]))

    for npc_id, npc_name in npc_id_to_name.items():
        npc = DesignerConfig.Npc[npc_id]
        gender = DesignerConfig.Actor[npc['templetID']]['gender']
        gift_config = next((gift for gift in DesignerConfig.BirthdayGift if gift['npcId'] == npc_id), None)

        if gift_config is None: continue

        gift_datas = gift_config['datas']
        gifts_by_level = {}

        for gift_data in gift_datas:
            min_level, max_level, probability, gift_ids = gift_data.split(',')
            gift_ids = [int(gift_id) for gift_id in gift_ids.split('_')]

            # Filter out gift_ids where the FestivalGift npc name does not match npc_name.
            gift_ids = [
                gift_id for gift_id in gift_ids
                if text.npc(DesignerConfig.FestivalGift[gift_id]['npcId']) == npc_name or (npc_name == 'Cooper')
            ]

            if not gift_ids: continue
            
            value = {
                'giftIds': gift_ids,
                'probability': f"{round(float(probability) * 100)}%"
            }

            # Check if any existing entry in gifts_by_level has the same value as 'value'
            existing_key = next((k for k, v in gifts_by_level.items() if v == value), None)
            if existing_key:
                # Replace the key with the new [min_level, max_level]
                old_min_level = existing_key[0]
                gifts_by_level.pop(existing_key)
                gifts_by_level[(old_min_level, max_level)] = value
            else:
                gifts_by_level[(min_level, max_level)] = value

        if not gifts_by_level: continue
        
        num_rows = len(gifts_by_level)
        table_lines.append(f'! rowspan="{num_rows}" | {{{{NPC2|{npc_name}}}}}')
        
        for levels, gifts in gifts_by_level.items():
            gift_ids     = gifts['giftIds']
            probability  = gifts['probability']
            min_level, max_level = levels

            min_level = relationship_levels[min_level]
            max_level = relationship_levels[max_level]

            if '/' in min_level:
                min_level = min_level.split('/')[gender]
            if '/' in max_level:
                max_level = max_level.split('/')[gender]
            
            if min_level == max_level:
                all_levels = min_level
            else:
                all_levels = f'{min_level} to <br>{max_level}'
            
            item_groups = []

            for gift_id in gift_ids:
                gift = DesignerConfig.FestivalGift[gift_id]
                item_ids = gift['drops'].split(',')
                items = [f'{{{{i2|{text.item(int(item_id.split("_")[0]))}|{item_id.split("_")[1]}|br = no}}}}' for item_id in item_ids]
                item_groups.append(" ''and'' ".join(items))
            
            table_lines.append(f'| {all_levels}')
            table_lines.append(f'| {probability}')
            table_lines.append(f'| style="text-align: left;" | {"  ''or''<br>".join(item_groups)}')
            table_lines.append(f'|-')
        
    table_lines.append('|}')
    table = '\n'.join(table_lines)
    print(table)

if __name__ == '__main__':
    run()
