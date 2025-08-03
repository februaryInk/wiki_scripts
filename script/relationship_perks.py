'''
Relationship types and levels table generator.
'''

from __future__ import annotations

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *
from collections import defaultdict

# ------------------------------------------------------------------------------

attribute_bonuses = {
    'AttackUp': 'Attack',
    'CpUp': 'Endurance',
    'CriticalUp': 'Critical Chance',
    'DefenseUp': 'Defense',
    'HpUp': 'Health Points',
    'LuckyPoint': 'Luck',
    'ResistSword': 'Toughness',
    'SpUp': 'Stamina',
    'WeaponBuff': 'Weapon Buff',
}

discount_bonuses = {
    'StoreDiscount': 'Store',
}

economic_bonuses = {
    'AdverDiscount': 'Advertisement',
    'BreedSellPrice': 'Animal Sale Price',
    'CustomInGameDiscount': 'Pablo\'s Parlor',
    'FarmElseMoney': 'Structure Upgrade Cost',
    'FarmMoney': 'Workshop Expansion',
    'HomeMaterial': 'Structure Upgrade Materials',
    'InquiryCookDiscount': 'Talk Recipes',
    'OrderFoodFree': 'Free Food',
    'OrderRewardMoney': 'Comission Money',
    'ProficiencyResetDiscount': 'Acupuncture',
    'RandomGainMiniGameMoney': 'Extra Game Center Token'
}

gift_bonuses = {
    'SendMail': 'Send Mail'
}

other_bonuses = {
    'OrderRewardReputation': 'Comission Reputation',
    'PKFavor': 'Spar Favor',
}

weapon_types = {
    '1': 'Sword and Shield',
    '2': 'Spear',
    '3': 'Dagger',
    '4': 'Greatsword'
}

# ------------------------------------------------------------------------------

def run() -> None:
    npcs          = DesignerConfig.Npc
    perk_groups   = DesignerConfig.FavorInfluence
    social_levels = DesignerConfig.SocialLevel
    stores        = DesignerConfig.StoreBaseData

    perks_by_category = {}

    for perk_group in perk_groups:
        if perk_group['npcId'] > 9999: continue
        npc_name = text.npc(perk_group['npcId'])

        for perk in perk_group['relationParams']:
            param = perk['param']
            perk_type, values = param.split('_', 1)
            category = 'Other'

            if perk_type in attribute_bonuses:
                category = 'Attribute'
            elif perk_type in discount_bonuses and npc_name != 'Magic Mirror':
                category = 'Discount'
            elif perk_type in economic_bonuses or (perk_type == 'StoreDiscount' and npc_name == 'Magic Mirror'):
                category = 'Economic'
            elif perk_type in gift_bonuses:
                category = 'Gift'
            elif perk_type.startswith('Pathea.Designer'):
                category = 'Follower'

            if category not in perks_by_category:
                perks_by_category[category] = []

            perk_data = {
                'npc_name': npc_name,
                'social_level_id': perk['socialLevel'],
                'text': text(perk['textId']),
                'type': perk_type,
                'values': values
            }

            perks_by_category[category].append(perk_data)
    
    for category, perks in perks_by_category.items():
        perks.sort(key=lambda x: (x['npc_name'], x['social_level_id']))
        lines = [
            f'==={category} Perks===',
            '{| class="prettytable sortable"'
        ]

        if category == 'Attribute':
            lines += build_attribute_table(perks)
        elif category == 'Discount':
            lines += build_economic_table(perks)
        elif category == 'Economic':
            lines += build_economic_table(perks)
        elif category == 'Follower':
            lines += build_generic_table(perks)
        elif category == 'Gift':
            lines += build_gift_table(perks)
        elif category == 'Other':
            lines += build_generic_table(perks)

        lines.append('|}')
        print('\n'.join(lines))

def build_attribute_table(perks):
    lines = [
        '! NPC !! Level !! Attribute !! Bonus',
        '|-'
    ]

    for perk in perks:
        npc_name = perk['npc_name']
        social_level = next((level for level in DesignerConfig.SocialLevel if level['level'] == perk['social_level_id']), None)
        social_level_text = text(social_level['nameId']) if social_level else 'Unknown'

        if perk['type'] == 'WeaponBuff':
            attribute = f'{weapon_types[perk["values"].split("_")[0]]} Attack'
            bonus = '5'
            icon = f'{{{{attr|{attribute}|label = true|anchor = Attack}}}}'
        else:
            attribute = attribute_bonuses.get(perk['type'], perk['type'])
            bonus = perk['values'].split('_')[0]
            icon = f'{{{{attr|{attribute}|label = true}}}}'

        lines.append(f'| {{{{NPC2|{npc_name}}}}} || {social_level_text} || {icon} || {bonus}')
        lines.append('|-')

    return lines

def build_economic_table(perks):
    level_ids = []
    grouped = defaultdict(list)

    for perk in perks:
        store_id = int(perk['values'].split('_')[0]) if perk['type'] == 'StoreDiscount' else ''
        key = (perk['npc_name'], perk['type'], store_id)
        grouped[key].append(perk)
        level_ids.append(perk['social_level_id'])
    
    level_ids = sorted(set(level_ids))
    
    headers = '! NPC !! Bonus'
    for level_id in level_ids:
        social_level = next((level for level in DesignerConfig.SocialLevel if level['level'] == level_id), None)
        if social_level:
            headers += f' !! {text(social_level["nameId"])}'
    
    lines = [
        headers,
        '|-'
    ]

    for (npc_name, perk_type, store_id), perk_group in grouped.items():
        if perk_type == 'StoreDiscount':
            store = next((store for store in DesignerConfig.StoreBaseData if store['id'] == store_id), None)
            store_name = f'[[{text(store['shopName'])}]]' if store else 'Unknown Store'
        else:
            store_name = economic_bonuses.get(perk_type, perk_type)

        line = f'| {{{{NPC2|{npc_name}}}}} || {store_name}'
        perk_by_level = {}

        for perk in perk_group:
            if perk_type in ['StoreDiscount', 'InquiryCookDiscount']:
                bonus = perk['values'].split('_')[1]
            else:
                bonus = perk['values'].split('_')[0]
            
            # If bonus is a decimal, format it into a percentage.
            if '.' in bonus:
                bonus_float = float(bonus)
                if bonus_float > 0:
                    bonus = f'+{bonus_float * 100:.0f}%'
                else:
                    bonus = f'{bonus_float * 100:.0f}%'

            perk_by_level[perk['social_level_id']] = bonus
        
        for level_id in level_ids:
            bonus = perk_by_level.get(level_id, '')
            line += f' || {bonus}'
        
        lines.append(line)
        lines.append('|-')

    return lines

def build_generic_table(perks):
    lines = [
        '! NPC !! Level !! Bonus',
        '|-'
    ]

    for perk in perks:
        npc_name = perk['npc_name']
        social_level = next((level for level in DesignerConfig.SocialLevel if level['level'] == perk['social_level_id']), None)
        social_level_text = text(social_level['nameId']) if social_level else 'Unknown'
        bonus = perk['text']

        lines.append(f'| {{{{NPC2|{npc_name}}}}} || {social_level_text} || {bonus}')
        lines.append('|-')

    return lines

def build_gift_table(perks):
    lines = [
        '! NPC !! Level !! Probability !! Gift',
        '|-'
    ]

    for perk in perks:
        npc_name = perk['npc_name']
        social_level = next((level for level in DesignerConfig.SocialLevel if level['level'] == perk['social_level_id']), None)
        social_level_text = text(social_level['nameId']) if social_level else 'Unknown'
        probability, mail_ids = perk['values'].split('_')
        mail_ids = [int(id.split('#')[0]) for id in mail_ids.split(',')]
        items = []

        print(perk['values'], mail_ids)

        for mail_id in mail_ids:
            mail = DesignerConfig.MailTemplate[mail_id]
            for itemData in mail['attachData']:
                item_name = text.item(itemData['data']['id'])
                count = itemData['data']['count']
                items.append(f'{{{{i2|{item_name}|{count}}}}}')

        lines.append(f'| {{{{NPC2|{npc_name}}}}} || {social_level_text} || {float(probability) * 100:.0f}% || {" ".join(items)}')
        lines.append('|-')

    return lines

if __name__ == '__main__':
    run()
