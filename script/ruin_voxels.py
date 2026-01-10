'''
Abandoned ruin terrain voxel table generator.
'''

from __future__ import annotations

from sandrock                       import *
from sandrock.lib.text              import load_text
from sandrock.structures.abandoned_ruins import abandoned_ruins

# ------------------------------------------------------------------------------

def run() -> None:
    for id, abandoned_ruin in abandoned_ruins.items():
        table_lines = [
            '{| class="prettytable fandom-table sortable text-center tdl3"',
            f'|+ Mining drops in {abandoned_ruin.name} Abandoned Ruins',
            '!Patch color',
            '!ID',
            '!Exp',
            '!Layers',
            '!class=unsortable|Mining drops',
        ]

        for voxel_id, voxel_info in abandoned_ruin.voxel_map.items():
            layers = voxel_info['layers']
            voxel = voxel_info['voxel']

            if len(layers) == abandoned_ruin.layer_count:
                layer_str = 'All'
            else:
                layer_str = f'{layers[0]} - {layers[-1]}'

            voxel_lines = [
                '|-',
                f'| {voxel.image}',
                f'| {voxel_id}',
                f'| {voxel.experience}',
                f'| {layer_str}',
                f'| '
            ] + voxel.generator.lines
            
            table_lines += voxel_lines
        
        table_lines.append('|}')

        print('\n'.join(table_lines))
        print('\n\n')
            

if __name__ == '__main__':
    run()
