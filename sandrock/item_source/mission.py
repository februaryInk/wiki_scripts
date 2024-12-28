from sandrock.common import *
from sandrock.lib.asset import Bundle
from sandrock.lib.designer_config import DesignerConfig
from .common import *

def update_missions(results: Results) -> None:
    update_rewards(results)
    update_scripts(results)

def update_rewards(results: Results) -> None:
    for reward in DesignerConfig.MissionRewards:
        mission_id = reward['missionId']
        source = ('mission', 'reward', f'mission:{mission_id}')
        for item in reward['itemList']:
            results[item['id']].add(source)

def update_scripts(results: Results) -> None:
    bundle = Bundle('story_script')
    for asset in bundle.assets:
        if asset.type == 'TextAsset':
            xml = asset.read_xml()
            update_script_xml(results, asset.name, xml)

def update_script_xml(results: Results, script_id: str, element: ElementTree.Element) -> None:
    if element.tag == 'STMT':
        attrs = element.attrib
        if attrs['stmt'] == 'BAG MODIFY' and int(attrs['addRemove']) == 0:
            source = ('mission', 'script', f'script:{script_id}')
            item_id = int(attrs['item'])
            results[item_id].add(source)
        if attrs['stmt'] == 'MAIL SEND TO BOX':
            mail_id = int(attrs['mailId'])
            mail = DesignerConfig.MailTemplate[mail_id]
            for attach in mail['attachData']:
                if attach['type'] == 1:
                    source = ('mission', 'mail', f'script:{script_id}')
                    item_id = attach['data']['id']
                    results[item_id].add(source)
    for child in element:
        update_script_xml(results, script_id, child)
