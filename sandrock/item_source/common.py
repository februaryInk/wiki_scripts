__all__ = [
    'ItemSource',
    'Results',
    'update_generator',
    'update_mail',
]

from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig

ItemSource: TypeAlias = tuple[str] | tuple[str, str] | tuple[str, str, str] | tuple[str, str, str, str]
Results: TypeAlias = dict[int, list[ItemSource]]

def update_generator(results: Results, source: ItemSource, group_id: int) -> None:
    group = DesignerConfig.GeneratorGroup.get(group_id)
    if group is None:
        return

    source = tuple(source)
    for element in group['elements']:
        for id_w in element['idWeights']:
            assert id_w['weight'] > 0
            gen = DesignerConfig.Generator_Item[id_w['id']]
            if gen['randomType'] == 0 and gen['parameters'][0] == 0:
                continue
            results[gen['itemId']].add(source)

def update_mail(results: Results, source: ItemSource, mail_id: int) -> None:
    mail = DesignerConfig.MailTemplate.get(mail_id)
    if mail is None:
        return
    for attach in mail['attachData']:
        if attach['type'] == 1:
            item_id = attach['data']['id']
            results[item_id].add(tuple(source))
