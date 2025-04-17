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
        1: "{{img|Affix_Green.png|size=text}} Outstanding",
        2: "{{img|Affix_Blue.png|size=text}} Perfect",
        3: "{{img|Affix_Purple.png|size=text}} Rare"
    }

    affix_level_colors = {
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
            '! colspan="3" | Items',
            '|-',
            '| colspan="3" | '
        ]

        item_names = [text.item(id) for id in item_ids]
        item_names.sort()

        for item_name in item_names:
            table_lines.append(f'{{{{i|{item_name}}}}}')

        for i, generator_id in enumerate(affix_group):
            table_lines.append('|-')
            table_lines.append(f'! colspan="3" | {affix_levels[i + 1]} Affixes')
            table_lines.append('|-')
            table_lines.append('! Min Level')
            table_lines.append('! Max Level')
            table_lines.append('! style="text-align: left;" | Description')
            table_lines.append('|-')

            if generator_id == 0:
                table_lines.append(f'| colspan="3" | None')
                continue

            generator = GeneratorGroup(generator_id)
            elements = generator.possible_elements
            elements.sort(key=lambda x: x.min_level)

            for element in elements:
                table_lines.append(f'|- style="{affix_level_colors[i + 1]}" |')
                table_lines.append(f'| {element.min_level}')
                table_lines.append(f'| {element.max_level}')
                table_lines.append(f'| style="text-align: left;" | {element.description}')
        
        table_lines.append('|}')

        print('\n'.join(table_lines))
        print('\n\n')
            

if __name__ == '__main__':
    run()
