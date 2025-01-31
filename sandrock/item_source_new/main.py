'''

'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import _presistent_cached

from .common import *

from .designer_configs import update_designer_configs

def get_item_sources(purge: bool = False) -> dict[int, list[ItemSource]]:
    results = _get_item_sources()
    return results

def _get_item_sources() -> dict[int, list[list[str]]]:
    results = defaultdict(set)
    print(json.dumps(results, indent=2))
    update_designer_configs(results)
    print(results)
    return results

# Do this last so we aren't using unavailable item containers.
def update_containers(results: Results) -> None:
    for container in DesignerConfig.ItemUse:
        if container['id'] in results:
            source = ['container', f'item:{container["id"]}']
            update_generator(results, source, container['generatorGroupId'])
