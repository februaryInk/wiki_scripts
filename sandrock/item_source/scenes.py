from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import get_interest_points, get_catchable_resource_points
from .common                      import *

# ------------------------------------------------------------------------------

def update_scenes(results: Results) -> None:
    for interest in get_interest_points():
        behav = read_json(interest['behaviour'])
        if not behav['m_Enabled']:
            continue
        if interest['type'] == 'SpawnMono_Point':
            update_monster(results, interest['scene'], behav)
            monster_id = behav['protoId']
            print(json.dumps(interest, indent=2))
        if interest['type'] == 'ResourceArea':
            update_resource(results, interest['scene'], behav)
        if interest['type'] == 'SceneItemBox':
            update_treasure(results, interest['scene'], behav)

def update_monster(results: Results, scene: str, behaviour: Any) -> None:
    monster_id = behaviour['protoId']
    source     = ['monster', f'scene_name:{scene}', f'monster:{monster_id}']
    monster    = DesignerConfig.Monster.get(monster_id)
    if monster is not None:
        for drop in monster['dropDatas']:
            update_generator(results, source, drop['y'])

def update_resource(results: Results, scene: str, behaviour: Any) -> None:
    res_confs = [conf for conf in behaviour['weightConfigs'] if conf['weight'] > 0]
    res_ids = [conf['id'] for conf in res_confs if conf['id']]

    # junk piles that yield items per hit
    # TODO: We using this?
    catchables = get_catchable_resource_points()

    for res_id in res_ids:
        res = DesignerConfig.ResourcePoint.get(res_id)
        if res is None:
            continue

        source = ['gathering', f'scene_name:{scene}', f'resource:{res_id}']
        groups = [res['generatorGroup']]

        catch = _load_catchable(res['prefabModel'])
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
    source = ['treasure', f'scene_name:{scene}']
    update_generator(results, source, behaviour['generatorId'])

@cache
def _load_catchable(key: str) -> dict | None:
    path = get_catchable_resource_points().get(key)
    if path is None:
        return None
    return read_json(path)
