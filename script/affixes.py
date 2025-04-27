'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *

from collections import defaultdict
from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

def run() -> None:
    item_affixes = DesignerConfig.ItemAffix
    affixes_to_items = defaultdict(list)

    affix_levels = {
        0: 'None',
        1: "{{img|Affix_Green.png|size=text}}",
        2: "{{img|Affix_Blue.png|size=text}}",
        3: "{{img|Affix_Purple.png|size=text}}"
    }

    affix_level_colors = {
        0: "background-color: rgba(255, 255, 255, 0.1);",
        1: "background-color: rgba(68, 189, 137, 0.1);",
        2: "background-color: rgba(93, 138, 206, 0.1);",
        3: "background-color: rgba(184, 78, 178, 0.1);"
    }

    for id, item_affix in item_affixes.items():
        key = tuple(item_affix["affixSceneSlot"])
        affixes_to_items[key].append(id)
    
    for affix_group, item_ids in affixes_to_items.items():
        table_lines = [
            '{| class="prettytable" style="min-width:100%; text-align:center;"'
            '|-',
            '! colspan="4" | Items',
            '|-',
            '| colspan="4" | '
        ]

        item_names = [text.item(id) for id in item_ids]
        item_names.sort()

        for item_name in item_names:
            table_lines.append(f'{{{{i|{item_name}}}}}')

        for i, generator_id in enumerate(affix_group):
            table_lines.append('|-')
            table_lines.append(f'! colspan="4" | Slot {i + 1}')
            table_lines.append('|-')
            table_lines.append('! Type')
            table_lines.append('! Min Level')
            table_lines.append('! Max Level')
            table_lines.append('! style="text-align: left;" | Description')
            table_lines.append('|-')

            if generator_id == 0:
                table_lines.append(f'| colspan="4" | None')
                continue

            generator = GeneratorGroup(generator_id)
            elements = generator.elements
            elements.sort(key=lambda x: x.outcomes[0].min_level)

            assert len(elements) == 1, f"Multiple elements for generator {generator_id}"
            outcomes = elements[0].outcomes
            outcomes.sort(key=lambda x: [x.min_level, x.require_grade])

            for outcome in outcomes:
                if outcome.probability == 0: continue

                table_lines.append(f'|- style="{affix_level_colors[outcome.required_grade]}" |')
                table_lines.append(f'| {affix_levels[outcome.require_grade]}')
                table_lines.append(f'| {outcome.min_level}')
                table_lines.append(f'| {outcome.max_level}')
                table_lines.append(f'| style="text-align: left;" | {outcome.description}')
        
        table_lines.append('|}')

        print('\n'.join(table_lines))
        print('\n\n')
            

if __name__ == '__main__':
    run()
