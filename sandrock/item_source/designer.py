from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from .common import *

def update_designer_configs(results: Results) -> None:
    update_stores(results)
    update_abandoned_ruins(results)
    update_hazard_ruins(results)
    update_misc(results)

def update_stores(results: Results) -> None:
    for store_id, store in DesignerConfig.StoreBaseData.items():
        source = ('store', f'store:{store_id}')

        goods = []
        for group_id in store['groupGoods']:
            goods += DesignerConfig.GroupProduct[group_id]['goods']
        goods += store['goodsSetting']

        for good in goods:
            product = DesignerConfig.SellProduct[good['id']]
            if product['globalStr'] == 'Temp':  # placeholder for future version
                continue
            results[product['itemId']].add(source)

def update_abandoned_ruins(results: Results) -> None:
    voxel_types = {voxel['type']: voxel for voxel in DesignerConfig.VoxelTypeInfo}

    for ruin in DesignerConfig.AbandonedDungeon:
        scene_id = ruin['scene']
        source = ['abandoned_ruin', f'scene:{scene_id}']

        voxel_fields = ['baseVoxel', 'normalVoxel', 'goodVoxel', 'rareVoxel']
        for field in voxel_fields:
            for type_weight in ruin[field].split(','):
                type_id = int(type_weight.split('_')[0])
                voxel = voxel_types[type_id]
                update_generator(results, source + ['mining'], voxel['itemDropId'])

        for relics in ruin['treasureItem']:
            for relic in relics['dataAry']:
                update_generator(results, source + ['relic'], relic['id0'])

        chests = ruin['normalChest'] + ruin['goodChest']
        for chest in chests:
            update_generator(results, source + ['treasure'], chest['id0'])

def update_hazard_ruins(results: Results) -> None:
    for i, ruin in enumerate(DesignerConfig.TrialDungeonRule):
        scene_id = ruin['scene']
        source = ['hazard_ruin', f'scene:{scene_id}']

        update_generator(results, source + ['first_completion'], ruin['firstRewardGeneratorId'])

        for reward in ruin['rewardStr']:
            group = int(reward.split(',')[0])
            update_generator(results, source + ['rank'], group)

        chests = ruin['normalChest'] + ruin['goodChest']
        for chest in chests:
            update_generator(results, source + ['treasure'], chest['id0'])

def update_misc(results: Results) -> None:
    for info in DesignerConfig.DropTaskInfo:
        for item_id in info['dropItemIds']:
            source = ('mort_photo',)
            results[item_id].add(source)

    for reward in DesignerConfig.GuildRankingReward:
        for group in reward['monthRewards']:
            update_generator(results, ['ranking'], group)
        for group in reward['annualAwards']:
            update_generator(results, ['ranking'], group)

    for reward in DesignerConfig.MuseumReward:
        source = ('museum',)
        item_id = reward['prizeItem']['id']
        results[item_id].add(source)

    for pet in DesignerConfig.PetDispatchConfig:
        update_generator(results, ['pet'], pet['itemGroupId'])

    for delivery_service in DesignerConfig.PreOrderPoint:
        for choice_id in delivery_service['choices']:
            choice = DesignerConfig.PreOrderChoice[choice_id]
            for item in choice['items']:
                source = ('delivery', f'delivery:{delivery_service["id"]}')
                results[item['x']].add(source)

    for prize in DesignerConfig.SandSkiingItem:
        source = ('skiing',)
        for item in prize['dropIdCounts']:
            results[item['id']].add(source)

    #for research in DesignerConfig.ResearchItem:
    #    item_id = research['blueprintId']
    #    blueprint = DesignerConfig.Blueprint[item_id]
    #    if not blueprint['isDefaultLock']:
    #        continue
    #    source = ('research',)
    #    results[blueprint['bookId']].add(source)

    for npc in DesignerConfig.SocialNpcConfig:
        source = ('npc', 'marry', f'npc:{npc["npcId"]}')
        update_mail(results, source, npc['marryMail'])

    for market in DesignerConfig.MarketFKData:
        print(market)
        if market['operation'][0] == 'SendMail':
            source = ('developer', market['channelName'])
            update_mail(results, source, int(market['operation'][1]))
