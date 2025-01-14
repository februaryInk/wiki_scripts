'''
There are over 90 bundles in scenes/additive, and I don't wish to export them 
one by one. Easier to export the whole folder, but then it isn't organized by
asset type. Is there a simpler way to fix it than this? Probably yes.
'''

from sandrock import *

import re
import shutil
from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

def run() -> None:
    scene_directory = config.assets_root / 'scene/additive'
    manifest        = _ManifestXml(scene_directory / 'assets.xml')

    bundle_directories = [subdir for subdir in scene_directory.iterdir() if subdir.is_dir()]

    # Iterating over the bundle directories and sorting just the files in that
    # one directory at a time is hugely faster than iterating over the asset
    # manifest as our main loop. Plus, we can target a specific bundle if we 
    # want.
    for bundle_directory in bundle_directories:
        print(f'Processing {bundle_directory.relative_to(config.assets_root)}...')

        if bundle_directory.name.endswith('_export'):
            new_name = bundle_directory.name.removesuffix('_export')
            bundle_directory.rename(scene_directory / new_name)
            bundle_directory = scene_directory / new_name
        
        xml_file = bundle_directory / 'assets.xml'
        tree, root = _create_or_read_manifest(xml_file)

        for asset_info in manifest:
            source           = asset_info.find('Source').text
            source_file_name = source.rsplit('\\', 1)[-1]
            normalized_bundle_name = _extract_bundle_name(source_file_name)

            if normalized_bundle_name == bundle_directory.name.lower().replace('_', ''):
                name    = asset_info.find('Name').text
                path_id = asset_info.find('PathID').text
                type    = asset_info.find('Type').text
                ext     = 'json' if type == 'MonoBehaviour' else 'txt'

                file_path = bundle_directory / source_file_name / sanitize_filename(f'{name} @{path_id}.{ext}', replacement_text='_')

                if file_path.exists():
                    file_new_directory = bundle_directory / type
                    file_new_directory.mkdir(parents=True, exist_ok=True)

                    shutil.move(str(file_path), str(file_new_directory / file_path.name))
                    root.append(asset_info)
                #else:
                    #print(f'Warning: No file at {file_path.relative_to(config.assets_root)}')
        
        tree.write(bundle_directory / 'assets.xml', encoding='utf-8', xml_declaration=True)
        for directory in bundle_directory.iterdir():
            if directory.is_dir() and not any(directory.iterdir()):
                print(f'Deleting empty directory {directory.relative_to(config.assets_root)}...')
                directory.rmdir()


def _extract_bundle_name(bundle_file_name: str) -> str:
    # Extract the middle part between hyphen and dot.
    match = re.search(r'-(.*?)(?:\..*)?$', bundle_file_name)
    assert match
    extracted = match.group(1)
    # Convert to snake_case.
    return extracted.lower().replace('_', '')

def _create_or_read_manifest(xml_file: Path) -> tuple[ElementTree.ElementTree, ElementTree.Element]:
    if xml_file.exists():
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
    else:
        root = ElementTree.Element('Assets')
        tree = ElementTree.ElementTree(root)
    
    return (tree, root)

def _append_to_manifest(bundle_directory: Path, asset: ElementTree.Element):
    xml_file = bundle_directory / 'assets.xml'
    if xml_file.exists():
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
    else:
        root = ElementTree.Element('Assets')
        tree = ElementTree.ElementTree(root)
        
    root.append(asset)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)

class _ManifestXml():
    def __init__(self, path: PathLike):
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()

    def __iter__(self) -> Iterator[ElementTree.Element]:
        return iter(self.root.findall('Asset'))

if __name__ == '__main__':
    run()
