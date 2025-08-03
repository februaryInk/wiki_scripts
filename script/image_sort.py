'''
Sort all the exported Texture2D files into folders, to make it easier to find 
useful or interesting ones.
'''

from __future__ import annotations

from sandrock                     import *
from sandrock.lib.text            import load_text
from script.structures.generators import *
from collections import defaultdict

# ------------------------------------------------------------------------------

item_icons = [item['maleIconPath'].lower() for id, item in DesignerConfig.ItemPrototype.items()]

folder_to_detectors = {
    'character_customization': [
        lambda name: name.startswith('hair_')
    ],
    'character_art': [
        lambda name: name.endswith('_picture'),
        lambda name: name.endswith('_picture_half'),
        lambda name: 'picture' in name and 'pet' in name,
    ],
    'clouds': [
        lambda name: 'cloud' in name
    ],
    'constellations': [
        lambda name: 'constellation' in name
    ],
    'guide': [
        lambda name: name.startswith('guide_')
    ],
    'handbook': [
        lambda name: name.startswith('handbook')
    ],
    'item_icons': [
        lambda name: name in item_icons
    ],
    'story': [
        lambda name: name.startswith('cg_'),
        lambda name: name.startswith('cgshot_'),
        lambda name: name.startswith('dialog'),
        lambda name: name.startswith('mailpicture'),
        lambda name: 'news' in name,
        lambda name: 'photo' in name,
    ],
    'town_art': [
        lambda name: "paper" in name and "cityobj" in name,
        lambda name: "paper" in name and "_tex" in name,
        lambda name: "picture" in name and "cityobj" in name
    ],
    'texture_catori_world': [
        lambda name: "basinobj" in name and "_tex" in name,
        lambda name: "basinbuild" in name and "_tex" in name,
    ],
    'texture_character': [
        lambda name: "lucy" in name and "_tex" in name,
        lambda name: "max" in name and "_tex" in name,
        lambda name: "monster" in name and "_tex" in name,
    ],
    'texture_food': [
        lambda name: "food" in name and "_tex" in name,
        lambda name: "food" in name and "cityobj" in name,
    ],
    'texture_furniture': [
        lambda name: "furniture" in name and "_tex" in name
    ],
    'texture_object': [
        lambda name: "building" in name and "_tex" in name,
        lambda name: "cityobj" in name and "_tex" in name,
        lambda name: "terrain" in name,
    ],
    'texture_other': [
        lambda name: "_tex" in name,
        lambda name: "densitytex" in name,
    ],
    'other': [
        lambda name: name.startswith('fx'),
        lambda name: name.startswith('ldr'),
        lambda name: "lightmap" in name,
        lambda name: "particle" in name,
        lambda name: "icon" in name,
    ]
}

# ------------------------------------------------------------------------------

def run() -> None:
    texture_directory = config.assets_root / 'all_texture_2d'
    unsorted_directory = texture_directory / 'unsorted'

    if not unsorted_directory.exists():
        print(f'No unsorted directory found at {unsorted_directory}.')
        return
    
    # For file in unsorted_directory:
    for file in unsorted_directory.iterdir():
        for folder, detectors in folder_to_detectors.items():
            detectable_name = file.stem.lower()
            if any(detector(detectable_name) for detector in detectors):
                folder_path = texture_directory / folder
                folder_path.mkdir(exist_ok=True)
                file.rename(folder_path / file.name)
                break

if __name__ == '__main__':
    run()