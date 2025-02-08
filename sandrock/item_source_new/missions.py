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
        
        for mail_mission_id, mail_ids in mission.get_mail_ids().items():
            mail_mission = story.get_mission(mail_mission_id)
            mail_mission_type = 'event' if mail_mission.is_event else 'mission'

            for mail_id in mail_ids:
                mail = DesignerConfig.MailTemplate[mail_id]

                # This mail isn't directly related to a named mission, as far as
                # our mission parsing can detect.
                if mail_mission.is_controller:
                    title_id = mail['title']
                    source = ('mail', f'text:{title_id}', f'mail:{mail_id}')
                else:
                    source = (mail_mission_type, 'mail', f'mission:{mail_mission_id}', f'mail:{mail_id}')
                
                for attach in mail['attachData']:
                    # Type 1 is an item.
                    if attach['type'] == 1:
                        item_id = attach['data']['id']
                        results[item_id].add(source)
