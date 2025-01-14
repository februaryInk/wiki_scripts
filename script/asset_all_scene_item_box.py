'''
Find the generators (item spawners) for treasure chests in all scenes. This does
not correspond to a single asset file, but rather is created by finding treasure
chest game objects in scene bundles.

Requires:
    - designer_config
    - scenes
    - sceneinfo
    - text
'''

from sandrock         import *
from sandrock.preproc import get_config_paths, get_interest_points

page_name = 'AssetAllSceneItemBox'

class SceneResult(TypedDict):
    value0: str
    value1: list[dict]
Results: TypeAlias = dict[str, SceneResult]

def run() -> None:
    config_paths = get_config_paths()
    results = {}
    i = 0

    for interest in get_interest_points():
        behav = read_json(interest['behaviour'])
        if interest['type'] == 'SceneItemBox' and behav['m_Enabled']:
            update_treasure(results, interest['scene'], behav)

    results = dict(sorted(results.items()))
    for id, result in results.items():
        results[id]['value1'] = sorted(results[id]['value1'], key=lambda x: x['id'])
    data = {
        'version': config.version,
        'key': 'ItemBox',
        'configList': results
    }
    write_lua(config.output_dir / f'lua/{page_name}.lua', data)

def update_treasure(results: Results, name: str, behaviour: Any) -> None:
    scene_id          = sceneinfo.scene_id(name)
    scene_system_name = sceneinfo.scene_system_name(scene_id)
    if scene_id not in results:
        results[scene_id] = {'value0': scene_system_name, 'value1': []}
    
    chest_data = {'id': behaviour['id'], 'generatorId': behaviour['generatorId']}
    results[scene_id]['value1'].append(chest_data)
    
if __name__ == '__main__':
    run()
