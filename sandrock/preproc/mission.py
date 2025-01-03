from sandrock.common    import *
from sandrock.lib.asset import Bundle
from sandrock.lib.text  import text

import urllib.parse

# ------------------------------------------------------------------------------

# Mission name ID by mission ID.
def find_mission_names() -> dict[int, str | int]:
    bundle = Bundle('story_script')
    mission_names = {}
    script_names = {}

    for asset in bundle.assets:
        if asset.type == 'TextAsset':
            script_id               = int(asset.name)
            root                    = asset.read_xml()
            # Script name is encoded Chinese.
            script_name             = urllib.parse.unquote(root.attrib['name'])
            script_names[script_id] = f'{asset.name}:{script_name}'

            # Name ID gives the localized name.
            name_id = int(root.attrib['nameId'])
            if not name_id:
                continue
            if all(text(name_id, lang) == 'XX' for lang in config.languages):
                continue

            mission_names[script_id] = name_id

            # Missons often come in parts that call each other. The child script
            # isn't assigned a name, but is still part of the parent mission.
            for stmt in root.findall('.//STMT[@stmt="RUN MISSION"]'):
                child_script_id = int(stmt.attrib['missionId'])
                old_name_id     = mission_names.get(child_script_id)
                if old_name_id and name_id and old_name_id != name_id:
                    print(f'{old_name_id} -> {name_id}')
                # assert not old_name_id or old_name_id == name_id
                if not old_name_id:
                    mission_names[child_script_id] = name_id

    script_names.update(mission_names)
    return script_names
