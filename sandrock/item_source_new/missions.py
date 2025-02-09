'''
Check for items that are received from missions, either as rewards or as part of
the mission conduct.
'''

from sandrock.common              import *
from sandrock.lib.asset           import Bundle
from sandrock.lib.designer_config import DesignerConfig
from sandrock.structures.story    import Story
from .common                      import *

# ------------------------------------------------------------------------------

def update_missions(results: Results) -> None:
    update_rewards(results)
    update_story_script(results)

def update_rewards(results: Results) -> None:
    for reward in DesignerConfig.MissionRewards:
        mission_id = reward['missionId']
        source = ('mission', 'reward', f'mission:{mission_id}')
        for item in reward['itemList']:
            results[item['id']].add(source)

def update_story_script(results: Results) -> None:
    story = Story()
    for mission_id, mission in story:
        for item_causal_event, item_ids in mission.get_received_items().items():
            for item_id in item_ids:
                results[item_id].add(item_causal_event)
        
        source = ('mission', 'gift', f'mission:{mission_id}')
        for gift_mission_id, gift_ids in mission.get_received_gifts().items():
            for gift_id in gift_ids:
                gift = DesignerConfig.FestivalGift[gift_id]
                drop_ids = [drop.split('_')[0] for drop in gift['drops'].split(',')]

                for drop_id in drop_ids:
                    results[int(drop_id)].add(source)
        
        for mail_mission_id, mail_ids in mission.get_mail_ids().items():
            mail_mission = story.get_mission(mail_mission_id)
            mail_mission_type = 'event' if mail_mission.is_event else 'mission'

            for mail_id in mail_ids:
                mail = DesignerConfig.MailTemplate[mail_id]

                # This mail isn't directly related to a named mission, as far as
                # our mission parsing can detect.
                if mail_mission.is_controller:
                    source = ('mail', f'text:{mail['title']}', f'mail:{mail_id}')
                else:
                    source = (mail_mission_type, 'mail', f'mission:{mail_mission_id}', f'mail:{mail_id}')
                
                update_mail(results, source, mail_id)
