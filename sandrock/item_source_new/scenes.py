'''
Search scenes for monster spawn points, resource areas, and treasure chests.
Some of this information can be discovered from the designer configs, but we go 
to the trouble of pursing the scenes in order to discover what has actually been 
implemented and what is just in the configs.
'''

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
        if interest['type'] == 'SpawnMono_Point':
            update_monster(results, interest['scene'], behav)
            print(json.dumps(interest, indent=2))
        if interest['type'] == 'ResourceArea':
            update_resource(results, interest['scene'], behav)
        if interest['type'] == 'SceneItemBox':
            update_treasure(results, interest['scene'], behav)

def update_monster(results: Results, scene: str, behaviour: Any) -> None:
    monster_id = behaviour['protoId']
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
    source = ['treasure', f'scene:{scene}']
    update_generator(results, source, behaviour['generatorId'])

@cache
def _load_catchable(key: str) -> dict | None:
    path = get_catchable_resource_points().get(key)
    if path is None:
        return None
    return read_json(path)
