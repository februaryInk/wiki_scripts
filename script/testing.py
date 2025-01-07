'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths
from sandrock.structures.conversation import *

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------



def run() -> None:
    conv = ConvTalk(25, [])
    conv.print()

def print_scenes() -> None:
    for scene in DesignerConfig.Scene:
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
