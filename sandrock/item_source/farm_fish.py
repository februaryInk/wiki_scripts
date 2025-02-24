'''Check the source of farming and fishing products.'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from .common                      import *

def update_farming(results: Results) -> None:
    for crop in DesignerConfig.PlantConfig:
        seed_id = crop['ID']
        if seed_id not in results: continue
        
        source = ['farming', f'item:{seed_id}']
        groups = crop['dropDestroyIds'] + [crop['harvestId']]
        for group in groups:
            update_generator(results, source, group)

def update_fishing(results: Results) -> None:
    for pond in DesignerConfig.FishpondInfos:
        source = ('fishing', 'pond', str(pond['id']))
        for fish_id in pond['fishIds']:
            item_id = DesignerConfig.FishInfos[fish_id]['itemId']
            results[item_id].add(source)

        for bait_id in pond['validBaitIds']:
            if bait_id not in results: continue

            source = ('fishing', 'bait', f'item:{bait_id}')
            for bait in DesignerConfig.BaitInfos:
                if bait['itemId'] != bait_id:
                    continue
                fields = ['strongGroupIds', 'middleGroupIds', 'lowGroupIds', 'tinyGroupIds']
                for field in fields:
                    for fish_group_id in bait[field]:
                        fish_group = DesignerConfig.FishGroupInfos[fish_group_id]
                        for fish_id in fish_group['fishIds']:
                            item_id = DesignerConfig.FishInfos[fish_id]['itemId']
                            results[item_id].add(source)
