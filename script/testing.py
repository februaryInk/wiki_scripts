'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths
from sandrock.structures.conversation import *
from sandrock.structures.story import *

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------



def run() -> None:
    print_items_with_item_tag(212)

def print_conv_segment(id: int) -> None:
    seg = ConvSegment(id, [])
    seg.print()

def print_conv_talk(id: int) -> None:
    seg = ConvTalk(id, [])
    seg.print()

def print_items_with_item_tag(tag_id: int) -> None:
    for item in sorted(DesignerConfig.ItemPrototype, key=lambda item: item['id']):
        if tag_id in item['itemTag']:
            print(f'{item["id"]}: {text.item(item["id"])}')

def print_mission(id: int) -> None:
    story = Story()
    mission = story.get_mission(id)
    mission.print()

def print_mission_names() -> None:
    story = Story()
    misson_names = story.get_mission_names()
    print(json.dumps(misson_names, indent=2))

def print_scenes() -> None:
    for scene in sorted(DesignerConfig.Scene, key=lambda item: item['scene']):
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
