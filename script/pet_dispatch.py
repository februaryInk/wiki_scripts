'''
Pet Dispatch results table generator.
'''

from __future__ import annotations

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *

# ------------------------------------------------------------------------------

def run() -> None:
    # Name, icon, favor, hours, pet XP, items
    table_lines = [
        '{| class="prettytable" style="min-width:100%; text-align:center;"'
    ]

    icons = {
        'collect water': '{{i||Collect Water pet dispatch}}',
        'collection': '{{i||Collection pet dispatch}}',
        'combat': '{{i||Explore pet dispatch}}',
        'dig': '{{i||Dig pet dispatch}}',
        'explore': '{{i||Explore pet dispatch}}'
    }

    for _, dispatch in DesignerConfig.PetDispatchConfig.items():
        name = text(dispatch['nameId'])
        experience = dispatch['experience']
        favor = dispatch['favor']
        generator_group = GeneratorGroup(dispatch['itemGroupId'])
        hours = dispatch['duration']['y']
        icon = icons.get(name.lower(), '{{i||Pet dispatch}}')

        dispatch_lines = [
            '|-',
            f'! rowspan="4" | {icon}<br>{name}',
            '! Hours',
            '! Favor',
            '! Pet XP',
            '|-',
            f'| {hours}',
            f'| {favor}',
            f'| {experience}',
            '|-',
            '! colspan="3" | Items',
            '|-',
            '| colspan="3" style="text-align: left;" | '
        ]

        single_outcome_els = [el for el in generator_group.elements if el.has_single_outcome]
        multiple_outcome_els = [el for el in generator_group.elements if not el.has_single_outcome]

        if len(single_outcome_els) > 0:
            dispatch_lines += ['{{cols|2|']
            for element in single_outcome_els:
                dispatch_lines += element.lines
            dispatch_lines += ['}}', '']

        for element in multiple_outcome_els:
            dispatch_lines += ['One of the following:']
            dispatch_lines += ['{{cols|2|']
            dispatch_lines += element.lines
            dispatch_lines += ['}}', '']

        table_lines += dispatch_lines
        
    table_lines.append('|}')

    print('\n'.join(table_lines))
    print('\n\n')
            

if __name__ == '__main__':
    run()
