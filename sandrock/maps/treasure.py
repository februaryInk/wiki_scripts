# FIXME

from sandrock import *
from sandrock.lib import preproc
from sandrock.lib.generator import get_generator_group_items

from functools import cache

name_to_category = {
    'Desert Mushroom Strains': 'Desert Mushroom',
    'Sand Leek Seed': 'Sand Leek',
    'Sandrice Seed': 'Sandrice',

    'Bronze Bars': 'Copper/Bronze Bars',
    'Copper Bars': 'Copper/Bronze Bars',
    "Mi-an's Jerky": 'Jerky',

    'Junk Pile': None,
    'Stone Pile': None,
    'Wood Pile': None,

    'Old Newspaper': None,
    'Ripped Jeans': None,
    'Rotted Wood': None,
}

category_merge_distance = {
    'Stone Pile': 10,
    'Wood Pile': 10,
}

def main():
    markers = []

    interests = preproc.get_interest_points()
    ids = set()

    for interest in interests:
        if interest['scene'] != 'main':
            continue
        if interest['type'] != 'SceneItemBox':
            continue

        #print(interest)

        behav = read_json(interest['behaviour'])
        trans = read_json(interest['transform'])

        if behav['generatorId'] == 20930031:
            print(interest)
            print(behav)
            print()
            continue

        if not behav['m_Enabled']:
            continue

        x = trans['m_LocalPosition']['x']
        y = trans['m_LocalPosition']['z']

        marker = {
            'categoryId': 'default',
            'position': [x, y],
            'popup': {
                'title': 'Treasure Chest',
                'description': '{{generator|' + str(behav['generatorId']) + '}}'
            },
        }

        gid = behav['generatorId']
        items = get_generator_group_items(gid)

        if abs(x - 88.279) < 1 and abs(y - 130.07) < 1:
            if len(items) > 1:
                continue
            #print(x, y)
            #print('\n'.join(wiki.item(item) for item in items))
            #print(behav)

        item = wiki.item(items[0])

        cate = 'default'
        icon = None
        desc = None
        link = None

        if len(items) > 1:
            title = 'Treasure chest'
            desc = '{{generator|' + str(behav['generatorId']) + '}}'

            #print(gid)
            #print([wiki.item(i) for i in items])

            if gid == 13349:
                desc = '<br>'.join([
                    "One of the following:",
                    "5 [[Spinel]]",
                    "10 [[Data Disc]]",
                    "2 [[Gravity Motor]]",
                    "10 [[Power Stones]]",
                    "5 [[Water]]",
                ])

            if gid == 13353:
                icon = wiki.item(18000129) + '.png'
                desc = '<br>'.join([
                    '[[Masterpiece: City]]',
                    '10 [[Data Disc]]',
                    '5 [[Condensed Power Stone]]',
                ])

        elif item == 'Gols':
            group = DesignerConfig.GeneratorGroup[gid]
            gen_id = group['elements'][0]['idWeights'][0]['id']
            generator = DesignerConfig.Generator_Item[gen_id]
            num = round(generator['parameters'][0])
            title = f'{num} Gols'
            cate = 'gols'

        else:
            title = item
            desc = f'[[{item}]]'

            icon_file = DesignerConfig.ItemPrototype[items[0]]['maleIconPath']
            if icon_file in ['Item_InstructionBook', 'Item_Book_CookFomula_0']:
                icon = icon_file + '.png'
            else:
                icon = title + '.png'

            group = DesignerConfig.GeneratorGroup[gid]
            gen_id = group['elements'][0]['idWeights'][0]['id']
            gen = DesignerConfig.Generator_Item[gen_id]
            assert gen['randomType'] == 0
            num = round(gen['parameters'][0])
            if num != 1:
                title = f'{num} {item}'

            if items[0] >= 80000000:
                cate = 'book'
                desc = '[[' + item.removesuffix(' (Book)') + ']]'
                print(desc)

        marker = {
            'categoryId': cate or 'default',
            'position': [x, y],
            'popup': {
                'title': title,
            },
        }

        if icon:
            marker['icon'] = icon.replace(':', '-')
        if desc:
            marker['popup']['description'] = desc
        #if link:
        #    marker['link'] = { 'url': link, 'label': link }

        markers.append(marker)

    categories = []
    categories.append({
        'id': 'default',
        'listId': 1,
        'name': 'Item',
        'color': '#000000',
        'icon': 'treasure chest icon.png',
    })
    categories.append({
        'id': 'book',
        'listId': 2,
        'name': 'Crafting book',
        'color': '#000000',
        'icon': 'book icon.png',
    })

    categories.append({
        'id': 'gols',
        'listId': 3,
        'name': 'Gols',
        'color': '#000000',
        'icon': 'gols.png',
    })

    map_data = {
        'mapImage': 'map-main.png',
        'mapBounds': [[-1612, -1612], [1612, 1612]],
        'categories': categories,
        'markers': markers,
    }

    write_json('_out/map/treasure.json', map_data)

def _get_icon(category, items):
    priori = {
        'Bird Nest': 'Bird Nest',
        'Copper/Bronze Bars': 'Copper Bars',
        'Desert Mushroom': 'Desert Mushroom',
        'Junk Pile': 'Dregs',
        'Stone Pile': 'Stone',
        'Wood Pile': 'Wood',
    }
    if category in priori:
        return priori[category]
    if len(items) == 1:
        return items[0]
    if category in items:
        return category
    print(category, items)

def get_category(point):
    name = wiki_text(point['name_id'])
    if name not in name_to_category:
        return name
    return name_to_category[name]

main()
