'''
Search scenes for monster spawn points, resource areas, and treasure chests.
Some of this information can be discovered from the designer configs, but we go 
to the trouble of parsing the scenes in order to discover what has actually been 
implemented versus what is just in the configs.
'''

from sandrock.lib.sceneinfo                import sceneinfo
from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import get_interest_points, get_catchable_resource_points
from .common                      import *

# ------------------------------------------------------------------------------

def update_scenes(results: Results) -> None:
    # Get data for all the game objects we care about.
    for interest in get_interest_points():
        # Read in JSON from the GameObject's MonoBehaviour path.
        behav = read_json(interest['behaviour'])
        if not behav['m_Enabled']:
            continue
        if interest['type'] == 'MonsterArea_IMap':
            update_monster(results, interest['scene'], behav)
        if interest['type'] == 'SpawnMono_Point':
            update_monster(results, interest['scene'], behav)
        if interest['type'] == 'ResourceArea':
            update_resource(results, interest['scene'], behav)
        if interest['type'] == 'SceneItemBox':
            update_treasure(results, interest['scene'], behav)
        if interest['type'] == 'VoxelSpawnerMarkHub':
            update_voxel(results, interest['scene'], behav)

def update_monster(results: Results, scene: str, behaviour: Any) -> None:
    # protoId for SpawnMono_Point, monsterId for MonsterArea_IMap.
    monster_id = behaviour.get('protoId', behaviour.get('monsterId'))
    # TODO: This is the first fight against Logan, but it's impossible to 
    # actually defeat him, so I do not believe he has any drops? Yet his monster 
    # data has the same drop table as the Caretaker.
    if monster_id == 5044: return
    source     = ['monster', f'scene:{scene}', f'monster:{monster_id}']
    monster    = DesignerConfig.Monster.get(monster_id)
    if monster is not None:
        for drop in monster['dropDatas']:
            update_generator(results, source, drop['y'])

# Junk piles that yield items per hit.
def update_resource(results: Results, scene: str, behaviour: Any) -> None:
    resource_point_confs = [conf for conf in behaviour['weightConfigs'] if conf['weight'] > 0]
    resource_point_ids = [conf['id'] for conf in resource_point_confs if conf['id']]

    for resource_point_id in resource_point_ids:
        resource_point = DesignerConfig.ResourcePoint.get(resource_point_id)
        if resource_point is None:
            continue

        source = ['gathering', f'scene:{scene}', f'resource_point:{resource_point_id}']
        groups = [resource_point['generatorGroup']]

        catch = _load_catchable(resource_point['prefabModel'])
        if catch:
            source[0] = 'salvaging'
            if catch['useAutoGeneratorGroup']:
                catch_groups = [catch['autoGeneratorGroup']['generatorGroupId']]
            else:
                catch_groups = [group['generatorGroupId'] for group in catch['generatorGroups']]
            catch_groups = [group for group in catch_groups if group]
            if catch_groups:
                groups = catch_groups
                
        for group in groups:
            update_generator(results, source, group)

def update_treasure(results: Results, scene: str, behaviour: Any) -> None:
    source = ['treasure', f'scene:{scene}', f'generator:{behaviour["generatorId"]}']
    update_generator(results, source, behaviour['generatorId'])

_voxel_types = {voxel['type']: voxel for voxel in DesignerConfig.VoxelTypeInfo}
_static_scene_spawners = {scene['scene']: scene for scene in DesignerConfig.StaticSceneSpawner}
_translate = {
    'BaseVoxel': 'baseVoxel',
}
def update_voxel(results: Results, scene: str, behaviour: Any) -> None:
    scene_id = sceneinfo.scene_id(scene)
    source = ('scene', f'scene:{scene_id}', 'mining')
    type_tag = _translate.get(behaviour['typeTag'], behaviour['typeTag'])
    scene_voxel_data = _static_scene_spawners.get(scene_id, {})

    if not scene_voxel_data: return

    for type_weight in scene_voxel_data[type_tag].split(','):
        type_id = int(type_weight.split('_')[0])
        voxel = _voxel_types[type_id]
        update_generator(results, source, voxel['itemDropId'])

@cache
def _load_catchable(key: str) -> dict | None:
    path = get_catchable_resource_points().get(key)
    if path is None:
        return None
    return read_json(path)
