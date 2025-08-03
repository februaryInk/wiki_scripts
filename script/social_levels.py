'''
Relationship types and levels table generator.
'''

from __future__ import annotations

import random

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *

# ------------------------------------------------------------------------------

types = {
    -1: {
        'name': 'Unused',
        'birthday': False,
        'confession': False,
        'icon': 'star',
        'party': False,
        'propose': False
    },
    0: {
        'name': 'Default',
        'birthday': True,
        'confession': True,
        'icon': 'star',
        'party': True,
        'propose': False
    },
    1: {
        'name': 'Romantic',
        'birthday': True,
        'confession': False,
        'icon': 'heart',
        'party': True,
        'propose': True
    },
    2: {
        'name': 'Spouse',
        'birthday': True,
        'confession': False,
        'icon': 'heart',
        'party': True,
        'propose': False
    },
    3: {
        'name': 'Child',
        'birthday': False,
        'confession': False,
        'icon': 'star',
        'party': False,
        'propose': False
    },
    4: {
        'name': 'Pet',
        'birthday': False,
        'confession': False,
        'icon': 'paw',
        'party': False,
        'propose': False
    }
}

image_alignments = ['left', 'center', 'right']

# ------------------------------------------------------------------------------

def run() -> None:
    social_levels = DesignerConfig.SocialLevel
    level_type_groups = defaultdict(dict)

    for level in social_levels:
        level_type_groups[level['type']][level['level']] = {
            'name': text(level['nameId']),
            'min_points': level['range']['x'],
            'max_points': level['range']['y'],
            'party_probability': level['partyProbability'],
            'birthday_probability_min': level['birthdayProbability']['x'],
            'birthday_probability_max': level['birthdayProbability']['y'],
            'confession_probability_min': level['confessionProbability']['x'],
            'confession_probability_max': level['confessionProbability']['y'],
            'propose_probability_min': level['proposeProbability']['x'],
            'propose_probability_max': level['proposeProbability']['y']
        }

    output_lines = []
    current_alignment = None

    for level_type_id, levels in level_type_groups.items():
        level_type = types[level_type_id]
        levels = dict(sorted(levels.items(), key=lambda x: x[0]))

        if level_type['name'] == 'Unused':
            continue

        lines = []
        lines.append(f'==={level_type["name"]}===')
        lines.append('{{RelationshipTable|open}}')

        for level_id, level in levels.items():
            index = list(levels.keys()).index(level_id)
            if level_type_id == 0:
                index = max(0, index - 2)

            # Random that is not the same as the previous one
            possible_alignments = [a for a in image_alignments if a != current_alignment]
            current_alignment = random.choice(possible_alignments)

            lower_level_id = level_id - 1
            lower_level = levels[lower_level_id] if lower_level_id in levels else None

            points_range = level['max_points'] - level['min_points']
            points_low = lower_level['max_points'] if lower_level else level['min_points']
            points_high = level['max_points']
            points_downgrade = level['min_points']

            # Birthday calculations
            birthday_range = level['birthday_probability_max'] - level['birthday_probability_min']
            birthday_high = level['birthday_probability_max']
            birthday_downgrade = level['birthday_probability_min']
            birthday_low = ((points_low - points_downgrade) / points_range * birthday_range + birthday_downgrade) if points_range else birthday_downgrade

            birthday_high = "" if birthday_high == 0 else f"{birthday_high * 100:.0f}%"
            birthday_low = "" if birthday_low == 0 else f"{birthday_low * 100:.0f}%"
            birthday_downgrade = "" if birthday_downgrade == 0 else f"{birthday_downgrade * 100:.0f}%"

            # Confession calculations
            confession_range = level['confession_probability_max'] - level['confession_probability_min']
            confession_high = level['confession_probability_max']
            confession_downgrade = level['confession_probability_min']
            confession_low = ((points_low - points_downgrade) / points_range * confession_range + confession_downgrade) if points_range else confession_downgrade

            confession_high = "" if confession_high == 0 else f"{confession_high * 100:.0f}%"
            confession_low = "" if confession_low == 0 else f"{confession_low * 100:.0f}%"
            confession_downgrade = "" if confession_downgrade == 0 else f"{confession_downgrade * 100:.0f}%"

            # Propose calculations
            propose_range = level['propose_probability_max'] - level['propose_probability_min']
            propose_high = level['propose_probability_max']
            propose_downgrade = level['propose_probability_min']
            propose_low = ((points_low - points_downgrade) / points_range * propose_range + propose_downgrade) if points_range else propose_downgrade

            propose_high = "" if propose_high == 0 else f"{propose_high * 100:.0f}%"
            propose_low = "" if propose_low == 0 else f"{propose_low * 100:.0f}%"
            propose_downgrade = "" if propose_downgrade == 0 else f"{propose_downgrade * 100:.0f}%"

            party = "" if level['party_probability'] == 0 else f"{level['party_probability'] * 100:.0f}%"

            level_lines = [
                '{{RelationshipTableEntry',
                f'|birthdayDowngrade = {birthday_downgrade}',
                f'|birthdayHigh = {birthday_high}',
                f'|birthdayLow = {birthday_low}',
                f'|confessionDowngrade = {confession_downgrade}',
                f'|confessionHigh = {confession_high}',
                f'|confessionLow = {confession_low}',
                f'|level = {level["name"]}',
                f'|imageAlignment = {current_alignment}',
                f'|indicator = {{{{relationship|{level_type["icon"]}|{index}}}}}',
                '|interactions =',
                '|other =',
                f'|party = {party}',
                f'|pointsDowngrade = {points_downgrade}',
                f'|pointsHigh = {points_high}',
                f'|pointsLow = {points_low}',
                f'|proposalDowngrade = {propose_downgrade}',
                f'|proposalHigh = {propose_high}',
                f'|proposalLow = {propose_low}',
                '}}'
            ]

            lines += level_lines
            if level_id + 1 in levels:
                lines.append('{{RelationshipTable|break}}')

        lines.append('{{RelationshipTable|close}}')
        lines.append('')
        output_lines.extend(lines)

    print('\n'.join(output_lines))

if __name__ == '__main__':
    run()
