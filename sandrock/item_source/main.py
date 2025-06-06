'''

'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import _presistent_cached

from .common import *

from .craft            import update_crafting
from .designer_configs import update_designer_configs
from .dynamic_monsters import update_dynamic_monsters
from .farm_fish        import update_farming, update_fishing
from .missions         import update_missions
from .scenes           import update_scenes
from .terrain          import update_terrain

from .unlockers        import update_unlockers

# ------------------------------------------------------------------------------

def get_item_sources(purge: bool = False) -> dict[int, list[ItemSource]]:
    results = _get_item_sources()
    return results

def get_item_unlockers(purge: bool = False) -> dict[int, list[ItemSource]]:
    results = _get_item_unlockers()
    return results

def _get_item_unlockers() -> dict[int, list[list[str]]]:
    results = defaultdict(set)
    
    print('Analyzing unlockers...')
    update_unlockers(results)
    
    return results

def _get_item_sources() -> dict[int, list[list[str]]]:
    results = defaultdict(set)
    
    print('Analyzing stores, ruins, gifts, and other sources...')
    update_designer_configs(results)

    print('Analyzing dynamic monster spawns...')
    update_dynamic_monsters(results)

    print('Analyzing logging & quarrying...')
    update_terrain(results)

    print('Analyzing gathering, monsters, treasure chests...')
    update_scenes(results)

    print('Analyzing missions...')
    update_missions(results)

    print('Analyzing crafting, farming, fishing, and containers...')
    # These items are dependent on the availability of other items, e.g., seeds
    # for crops or bait for fish, so we check them last and repeat until no new
    # accessible items are found.
    prev_total = -1
    while len(results) > prev_total:
        prev_total = len(results)

        update_crafting(results)
        update_farming(results)
        update_fishing(results)
        update_containers(results)
        update_machine_upgrades(results)
    
    return results

# Do this last so we aren't using unavailable item containers.
def update_containers(results: Results) -> None:
    for container in DesignerConfig.ItemUse:
        if container['id'] in results:
            source = ['container', f'item:{container["id"]}']
            update_generator(results, source, container['generatorGroupId'])

def update_machine_upgrades(results: Results) -> None:
    machines = DesignerConfig.Machine
    source = ('machine_upgrade',)
    for machine in machines:
        if machine['level'] <= 1: continue
        # Being lazy and not checking if the upgrade materials exist in results.
        previous_level_machine = next((m for m in machines if m['tag'] == machine['tag'] and m['level'] == machine['level'] - 1), None)
        if previous_level_machine is None or previous_level_machine['id'] not in results:
            continue
        if len(previous_level_machine['upgradeMaterials']) > 0:
            results[machine['id']].add(source)
