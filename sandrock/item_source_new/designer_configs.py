'''
Item sources we can extract from the designer configs on their own.

- Stores
'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.text            import text
from .common                      import *

# ------------------------------------------------------------------------------

def update_designer_configs(results: Results) -> None:
    update_abandoned_ruins(results)
    update_delivery_services(results)
    update_developer_mails(results)
    update_event_gifts(results)
    update_guild_ranking_rewards(results)
    update_hazard_ruins(results)
    update_marriage_mails(results)
    update_mort_photos(results)
    update_museum_rewards(results)
    update_party_services(results)
    update_pet_dispatches(results)
    update_sand_racing(results)
    update_sand_skiing(results)
    update_spouse_gifts(results)
    update_stores(results)

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

        for relic_set in ruin['treasureItem']:
            for relic in relic_set['dataAry']:
                update_generator(results, source + ['relic'], relic['id0'])

        chests = ruin['normalChest'] + ruin['goodChest']
        for chest in chests:
            update_generator(results, source + ['treasure'], chest['id0'])
        
        for treasure in ruin['treasureData']:
            update_generator(results, source + ['treasure_room'], treasure)
        
        # Salvage piles, but there aren't any in abandoned ruins?
        # resource_points = DesignerConfig.ResourcePoint
        # ruin_resource_points = [point['dataAry'] for point in ruin['resourcePoint']]
        # ruin_treasure_room_resource_points = [point['dataAry'] for point in ruin['treasureRoomResourcePoint']]
        # for resource_point in ruin_resource_points + ruin_treasure_room_resource_points:
        #     point = resource_points[resource_point['id0']]
        #     update_generator(results, source + ['resource_point'], point['generatorGroup'])

def update_delivery_services(results: Results) -> None:
    for delivery_service in DesignerConfig.PreOrderPoint:
        for choice_id in delivery_service['choices']:
            choice = DesignerConfig.PreOrderChoice[choice_id]
            for item in choice['items']:
                source = ('delivery', f'delivery:{delivery_service["id"]}')
                results[item['x']].add(source)

def update_developer_mails(results: Results) -> None:
    for market in DesignerConfig.MarketFKData:
        print(market)
        if market['operation'][0] == 'SendMail':
            source = ('developer', market['channelName'])
            update_mail(results, source, int(market['operation'][1]))
    
    # TODO: Check all mail for developer gifts and DLC. Also, KS rewards.

def update_event_gifts(results: Results) -> None:
    festival_gifts = DesignerConfig.FestivalGift

    for npc_gifts in DesignerConfig.FestivalGiftNpcConfig:
        child_birth_gift_ids = sum([gift_data['gifts'] for gift_data in npc_gifts['giftsChildBirth']], [])
        child_birth_gifts = [festival_gifts[gift_id] for gift_id in child_birth_gift_ids]
        wedding_gift_ids = sum([gift_data['gifts'] for gift_data in npc_gifts['giftsWedding']], [])
        wedding_gifts = [festival_gifts[gift_id] for gift_id in wedding_gift_ids]

        for gift in child_birth_gifts:
            source = ('npc', 'child', f'npc:{text(gift["npcId"])}')
            drop_ids = [drop.split('_')[0] for drop in gift['drops'].split(',')]

            for drop_id in drop_ids:
                results[int(drop_id)].add(source)
        
        for gift in wedding_gifts:
            source = ('npc', 'wedding', f'npc:{text(gift["npcId"])}')
            drop_ids = [drop.split('_')[0] for drop in gift['drops'].split(',')]

            for drop_id in drop_ids:
                results[int(drop_id)].add(source)

    for birthday_gifts in DesignerConfig.BirthdayGift:
        npc_id = birthday_gifts['npcId']
        if npc_id < 0: continue

        for gift_data in birthday_gifts['datas']:
            relationship_min, relationship_max, _prob, gift_str = gift_data.split(',')
            gifts = [festival_gifts[int(id)] for id in gift_str.split('_')]

            drop_ids = [drop.split('_')[0] for drop in gift['drops'].split(',')]

            for drop_id in drop_ids:
                source = ('npc', 'birthday', f'npc:{text(gift["npcId"])}')
                results[int(drop_id)].add(source)
    
    # Day of Bright Sun gifts. See festivals (bundle)/FestivalSendGift (MonoBehavior).
    for i in range(1000, 1101):
        gift = DesignerConfig.FestivalGift[i]
        source = ('npc', 'day_of_bright_sun', f'npc:{text(gift["npcId"])}')
        drop_ids = [drop.split('_')[0] for drop in gift['drops'].split(',')]

        for drop_id in drop_ids:
            results[int(drop_id)].add(source)

def update_guild_ranking_rewards(results: Results) -> None:
    for reward in DesignerConfig.GuildRankingReward:
        for group in reward['monthRewards']:
            update_generator(results, ['guild_ranking'], group)
        for group in reward['annualAwards']:
            update_generator(results, ['guild_ranking'], group)

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

def update_marriage_mails(results: Results) -> None:
    for npc in DesignerConfig.SocialNpcConfig:
        source = ('npc', 'marry', f'npc:{npc["npcId"]}')
        update_mail(results, source, npc['marryMail'])

def update_mort_photos(results: Results) -> None:
    for info in DesignerConfig.DropTaskInfo:
        for item_id in info['dropItemIds']:
            source = ('mort_photo',)
            results[item_id].add(source)

def update_museum_rewards(results: Results) -> None:
    for reward in DesignerConfig.MuseumReward:
        source = ('museum',)
        item_id = reward['prizeItem']['id']
        results[item_id].add(source)

def update_party_services(results: Results) -> None:
    services = [service for service in DesignerConfig.PartyService if service['iconPath'] == 'I_Party_img_Food_00']

    for service in services:
        source = ('party_food_package', f'service:{service["service"]}')
        num_dishes, dish_ids_str = service['datas']
        dish_ids = [int(dish_id) for dish_id in dish_ids_str.split(',')]
        for dish_id in dish_ids:
            results[dish_id].add(source)

def update_pet_dispatches(results: Results) -> None:
    for pet in DesignerConfig.PetDispatchConfig:
        update_generator(results, ['pet_dispatch'], pet['itemGroupId'])

def update_sand_racing(results: Results) -> None:
    for prize in DesignerConfig.SandCarItem:
        source = ('sand_racing',)
        for item in prize['dropIdCounts']:
            results[item['id']].add(source)

def update_sand_skiing(results: Results) -> None:
    for prize in DesignerConfig.SandSkiingItem:
        source = ('sand_sledding',)
        for item in prize['dropIdCounts']:
            results[item['id']].add(source)

def update_spouse_gifts(results: Results) -> None:
    mission_rewards = DesignerConfig.NormalMissionRewards

    for mission in DesignerConfig.NormalMissionData:
        mission_name = mission['nameId']
        # "A Gift from Your Spouse" or "Speak to Your Partner"
        if mission_name == 80031295 or mission_name == 80031297:
            npc = mission['deliverNpc']
            reward = next((obj for obj in mission_rewards if obj["proto"] == mission['rewardId']), None)
            reward_item_ids = [item['id'] for item in reward['rewardItems']]
            if mission_name == 80031295:
                source = ('npc', 'spouse_gift', f'npc:{npc}')
            else:
                source = ('npc', 'spouse_gift_expecting', f'npc:{npc}')

            for item_id in reward_item_ids:
                # print(f'{npc} gives {text.item(item_id)}')
                results[item_id].add(source)

def update_stores(results: Results) -> None:
    for store_id, store in DesignerConfig.StoreBaseData.items():
        # Second Myseterious Man store that sells only pet DLC items and is not 
        # accessible in-game.
        if store_id == 18: continue

        source = ('store', f'store:{store_id}')
        goods = []

        # Sets of products of a particular type that are sold in the store.
        # Format: {"id", "count", "chance"}
        for group_id in store['groupGoods']:
            goods += DesignerConfig.GroupProduct[group_id]['goods']
        # Additional products that don't belong to any group.
        goods += store['goodsSetting']

        for good in goods:
            product = DesignerConfig.SellProduct[good['id']]
            # "placeholder for future version"?
            # Racer Sandrunning Goggles
            # Expedition Sandrunning Goggles
            # Sporty Sandrunning Goggles
            # Mechanic Sandrunning Goggles
            # Racer Sandrunning Goggles
            if product['globalStr'].lower() == 'temp':
                print(f"Skipping temp item {text.item(product['itemId'])} in store {store_id}")
                continue

            results[product['itemId']].add(source)
