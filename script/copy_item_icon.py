from sandrock import *

from PIL import Image

items = [
    "Patterned Stone Floor",
    "Old World Tiled Floor",
    "Ceramic Green Tiled Floor",
    "Ceramic Red Tiled Floor",
    "Ceramic Blue Tiled Floor",
    "Ceramic Brown Tiled Floor",
    "Faded Brown Tiled Floor",
    "Light Brick Floor",
    "Dark Brick Floor",
    "Brushed Ceramic Floor",
    "Purple Tiled Floor",
    "Gray Tiled Floor",
    "Honeycomb Floor",
    "Pink Tiled Floor",
    "Grey Honeycomb Floor",
    "Turquoise Tiled Floor",
    "Sandy Floor",
    "Cubic Floor",
    "Patterned Brick Floor",
    "Patterned Paved Floor",
    "Wavy Brick Floor",
    "Classic Wood Floor",
    "Parquet Floor",
    "Warm Parquet Floor",
    "Concentric Wood Floor",
    "Alternating Wood Floor",
    "Warm Wood Floor",
    "Supported Wood Floor",
    "Looped Wood Floor",
    "Knotted Wood Floor",
    "Triangular Wood Floor",
    "Patterned Wood Floor",
    "Triangular Warm Wood Floor"
]

sprite_bundle = Bundle('uisystem_sprite')

def main() -> None:
    (config.output_dir / 'icon').mkdir(parents=True, exist_ok=True)
    for item in DesignerConfig.ItemPrototype:
        name = wiki.item(item['id'])
        all_names = text.item(item['id'])
        print(name)
        print(all_names)
        for target in items:
            if str(target).lower() in all_names.lower():
                male_icon = item['maleIconPath']
                female_icon = item['femaleIconPath']
                if female_icon:
                    print(name, ':', male_icon, '/', female_icon)
                    copy_icon(name + ' (Max)', male_icon)
                    copy_icon(name + ' (Lucy)', female_icon)
                else:
                    print(name, ':', male_icon)
                    copy_icon(name, male_icon)


def copy_icon(item_name: str, icon_name: str) -> None:
    for asset in sprite_bundle:
        if asset.name == icon_name:
            resize_icon(asset.image_path, config.output_dir / 'icon' / (item_name + '.png'))
            return
    print('Cannot find icon', icon_name)

def resize_icon(src_path: Path, dst_path: Path) -> None:
    src_img = Image.open(src_path)
    src_w, src_h = src_img.size

    dst_size = max(src_w, src_h, 64)
    dst_img = Image.new('RGBA', [dst_size, dst_size])

    left = (dst_size - src_w) // 2
    top = (dst_size - src_h) // 2
    dst_img.paste(src_img, [left, top])

    dst_img.save(dst_path, compress_level=9)

if __name__ == '__main__':
    main()
