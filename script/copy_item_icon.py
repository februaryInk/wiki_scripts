from sandrock import *

from PIL import Image

items = [
    "Pet Decoration Small Flower",
	"Pet Collar Ornament",
	"Pet Tail Decoration"
]

start = 12700101
end = 12702902
ids = range(start, end)

sprite_bundle = Bundle('uisystem_sprite')

def main() -> None:
    (config.output_dir / 'icon').mkdir(parents=True, exist_ok=True)
    for id, item in DesignerConfig.ItemPrototype.items():
        name = text(item['nameId'])
        wiki_name = wiki.item(item['id'])
        
        for target in items:
            if id in ids: # str(target).lower() == name.lower():
                if not wiki_name:
                    print('No wiki name for', name, '(', id, ')')
                    continue
                
                male_icon = item['maleIconPath']
                female_icon = item['femaleIconPath']

                if female_icon:
                    print(wiki_name, ':', male_icon, '/', female_icon)
                    copy_icon(wiki_name + ' (Max)', male_icon)
                    copy_icon(wiki_name + ' (Lucy)', female_icon)
                else:
                    print(wiki_name, ':', male_icon)
                    copy_icon(wiki_name, male_icon)


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
