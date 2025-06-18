'''
Monsters that spawn under certain circumstances, such as during sandstorms.

MonsterSpawnAsset format:

{
    'datas': [
        {
            'additiveScene': '1001',
            ['teams' / 'groups']: [
                {
                    'dropId`: 0,
                    'dropIds': [],
                    'modifierDatas': [],
                    'points': [
                        {
                            'protoId': 10000001,
                            'dropId': 0,
                            'dropIds': [],
                            'modifiers': [],
                        }
                    ],
                    'pointGroups': [
                        {
                            'points': [
                                {
                                    'protoId': 10000001,
                                    'dropId': 0,
                                    'dropIds': [],
                                    'modifiers': [],
                                }
                            ]
                        }
                    ]
                }
            ],
            'singles': [
                {
                    'modifierDatas': [],
                    'point': {
                        'protoId': 10000001,
                        'dropId': 0,
                        'dropIds': [],
                        'modifiers': [],
                    },
                    'pointGroup': {
                        'points': [
                            {
                                'protoId': 10000001,
                                'dropId': 0,
                                'dropIds': [],
                                'modifiers': [],
                            }
                        ]
                    ]
                }
            ],
        }
    ]
}
'''

from sandrock.common              import *
from sandrock.lib.asset           import Bundle
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.text            import text
from .common                      import *

# Dynamic monster spawns.
def update_dynamic_monsters(results: Results) -> None:
    update_scrooge_mcmole(results)
    update_spawn_sets(results)

# Can't find the rules that spawn Scrooge McMole.
def update_scrooge_mcmole(results: Results) -> None:
    monsters = DesignerConfig.Monster
    for monster in monsters.values():
        name = text(monster['nameId'])
        if name.lower() == 'scrooge mcmole':
            source = ['monster', 'scene:60', f'monster:{monster["id"]}']
            for drop in monster['dropDatas']:
                update_generator(results, source, drop['y'])

def update_spawn_sets(results: Results) -> None:
    monsters              = DesignerConfig.Monster
    monster_spawns_bundle = Bundle('monsterspawnasset')
    dynamic_spawns        = next((b for b in monster_spawns_bundle.behaviours if b.name.startswith("SpawnMonsterAsset")), None)
    
    for spawn_data in dynamic_spawns.data['datas']:
        scene_id = spawn_data['additiveScene']

        for spawn_set in spawn_data['teams'] + spawn_data['groups'] + spawn_data['singles']:
            set_modifiers = spawn_set['modifierDatas']
            generator_mods = [mod for mod in set_modifiers if mod['modifierType'] == 4]
            name_mods = [mod for mod in set_modifiers if mod['modifierType'] == 11]

            points = spawn_set.get('points') if 'points' in spawn_set else [spawn_set['point']]
            point_groups = spawn_set.get('pointGroups') if 'pointGroups' in spawn_set else [spawn_set['pointGroup']]
            points += [point for group in point_groups for point in group['points']]

            for point in points:
                monster_id = point['protoId']
                monster    = monsters.get(monster_id)
                name       = text(monster['nameId'])

                point_gen_mods = [mod for mod in point['modifiers'] if mod['modifierType'] == 4] + generator_mods
                point_name_mods = [mod for mod in point['modifiers'] if mod['modifierType'] == 11] + name_mods

                assert len(point_name_mods) <= 1, f'Monster {name} has multiple name modifiers: {point_name_mods}'
                if len(point_name_mods) == 1:
                    name = text(int(point_name_mods[0]['modifierData']))
                enraged = name.lower().startswith('enraged')

                if len(point_gen_mods) > 0 and not enraged:
                    print(f'Generator mods for {name}: {point_gen_mods}')

                if enraged:
                    source = ['enraged_monsters', f'scene:{scene_id}', f'monster:{monster_id}']
                    for gen in point_gen_mods:
                        update_generator(results, source, int(gen['modifierData']))
                
                source = ['monster', f'scene:{scene_id}', f'monster:{monster_id}']

                for drop in monster['dropDatas']:
                    update_generator(results, source, drop['y'])
