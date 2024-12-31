'''
There are over 90 bundles in scenes/additive, and I don't wish to export them 
one by one. Easier to export the whole folder, but then it isn't organized by
bundle/scene. Is there a simpler way to fix it than this? Probably yes.
'''

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths

import re
import shutil

# ------------------------------------------------------------------------------

def run() -> None:
    scene_directory = config.assets_root / 'scene/additive'
    manifest = _ManifestXml(scene_directory / 'assets.xml')
    count = 0

    for asset_info in manifest:
        count += 1
        if count % 100 == 0: print(f'Processing {count}th asset...')
        name = asset_info.find('Name').text
        path_id = asset_info.find('PathID').text
        type = asset_info.find('Type').text
        ext = 'json' if type == 'MonoBehaviour' else 'txt'

        file_path = scene_directory / f'{type}/{name} @{path_id}.{ext}'

        if file_path.exists():
            source           = asset_info.find('Source').text
            bundle_file_name = source.rsplit('\\', 1)[-1]
            bundle_name      = _extract_bundle_name(bundle_file_name)
            bundle_directory = Path(scene_directory) / bundle_name
            file_new_directory = bundle_directory / type

            file_new_directory.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(file_new_directory / file_path.name))
            _append_to_manifest(bundle_directory, asset_info)
        else:
            print(f'Warning: No file at {str(file_path)}')


def _extract_bundle_name(bundle_file_name: str) -> str:
    # Extract the middle part between hyphen and dot.
    match = re.search(r"-(.*?)(?:\..*)?$", bundle_file_name)
    assert match
    extracted = match.group(1)
    # Convert to snake_case.
    return re.sub(r'(?<!^)(?=[A-Z])', '_', extracted).lower()

def _append_to_manifest(bundle_directory: Path, asset: ElementTree.Element):
    xml_file = bundle_directory / "assets.xml"
    if xml_file.exists():
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
    else:
        root = ElementTree.Element("Assets")
        tree = ElementTree.ElementTree(root)
        
    root.append(asset)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)

class _ManifestXml():
    def __init__(self, path: PathLike):
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()

    def __iter__(self) -> Iterator[ElementTree.Element]:
        return iter(self.root.findall('Asset'))

if __name__ == '__main__':
    run()
