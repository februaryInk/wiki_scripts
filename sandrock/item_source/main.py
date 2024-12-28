from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc import _presistent_cached
from .common import *
from .craft import update_crafting
from .designer import update_designer_configs
from .farm_fish import update_farming, update_fishing
from .mission import update_missions
from .scenes import update_scenes
from .terrain import update_terrain

def get_item_sources(purge: bool = False) -> dict[int, list[ItemSource]]:
    data = _presistent_cached('item_sources', _get_item_sources, purge=purge)
    results = {}
    for item_id, sources in data.items():
        results[int(item_id)] = [tuple(source) for source in sources]
    return results

def _get_item_sources() -> dict[int, list[list[str]]]:
    results = defaultdict(set)

    update_designer_configs(results)
    print('analyzing logging & quarrying...')
    update_terrain(results)
    print('analyzing gathering, monsters, treasure chests...')
    update_scenes(results)
    print('analyzing missions...')
    update_missions(results)

    prev_total = 0
    while len(results) > prev_total:
        prev_total = len(results)

        update_crafting(results)
        update_farming(results)
        update_fishing(results)
        update_containers(results)

    json = {}
    for item_id, sources in sorted(results.items()):
        if item_id not in DesignerConfig.ItemPrototype:
            continue
        json[item_id] = [list(source) for source in sorted(sources)]
    return json

def update_containers(results: Results) -> None:
    for container in DesignerConfig.ItemUse:
        if container['id'] in results:
            source = ['container', f'item:{container["id"]}']
            update_generator(results, source, container['generatorGroupId'])
