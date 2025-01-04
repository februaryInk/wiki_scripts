'''
Scratch script for testing ad hoc output.
'''

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

def run() -> None:
    print(text.item(19800017))
    print(text.item(12400026))
    print(text.item(19112021))

    print(text.item(19000008))

    print(text.item(82000001))
    print(text.item(82100001))
    print(text.item(82200001))
    print(text.item(82300002))

    print(text.item(83000001))

def print_scenes() -> None:
    for scene in DesignerConfig.Scene:
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
