# FIXME

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.generator       import expand_generator
from sandrock.lib.text            import wiki
from sandrock.preproc             import get_catchable_resource_points, get_interest_points

# ------------------------------------------------------------------------------

name_to_category = {
    'Desert Mushroom Strains': 'Desert Mushroom',
    'Sand Leek Seed': 'Sand Leek',
    'Sandrice Seed': 'Sandrice',

    'Bronze Bars': 'Copper/Bronze Bars',
    'Copper Bars': 'Copper/Bronze Bars',
    "Mi-an's Jerky": 'Jerky',

    'Chat Log 1': 'Chat Log',
    'Chat Log 2': 'Chat Log',
    'Chat Log 3': 'Chat Log',

    'Junk Pile': None,
    'Stone Pile': None,
    'Wood Pile': None,

    'Old Newspaper': None,
    'Ripped Jeans': None,
    'Rotted Wood': None,
}

def main():
    gathering_points = get_gathering_points()
    cache            = set()
    cache_names      = set()

    for point in gathering_points:
        key = (point['name_id'], point['generator_group_id'])
        if key in cache:
            continue
        cache.add(key)

        name_seasons = tuple([point['name_id'], *point['seasons']])
        assert name_seasons not in cache_names
        cache_names.add(name_seasons)

        # TODO: What we doing down here?
        name = wiki(point['name_id'])
        if point['seasons'] != [0, 1, 2, 3]:
            assert len(point['seasons']) == 1
            season = ['Spring', 'Summer', 'Autumn', 'Winter'][point['seasons'][0]]
        else:
            season = None

    points = merge_points(gathering_points)
    points = sorted(points, key=(lambda point: point['name']))

    categories = {}

    markers = []
    for i, point in enumerate(points):
        # Are these points off the map?
        if abs(point['x']) > 1612 or abs(point['y']) > 1612:
            continue

        markers.append({
            'categoryId': point['category'],
            'position': [point['x'], point['y']],
            'popup': {
                'title': point['name'],
                'description': point['formated_items'],
            },
            #'id': str(i),
        })

        if point['category'] not in categories:
            icon = _get_icon(point['category'], point['items'])
            categories[point['category']] = {
                'id': point['category'],
                'listId': None,
                'name': point['category'],
                'color': '#000000',
                'icon': icon + '.png',
            }

    categories = sorted(categories.values(), key=(lambda cate: cate['name']))
    for i, cate in enumerate(categories):
        cate['listId'] = i + 1

    map_data = {
        'mapImage': 'map-main.png',
        'mapBounds': [[-1612, -1612], [1612, 1612]],
        'categories': categories,
        'markers': markers,
        'pageCategories': ['Interactive_maps'],
    }
    write_json('map/gathering.json', map_data)

def _get_icon(category, items):
    priori = {
        'Bird Nest': 'Bird Nest',
        'Chat Log': 'Chat Log 1',
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
    name = wiki(point['name_id'])
    if name not in name_to_category:
        return name
    return name_to_category[name]

def merge_points(points):
    ret = []

    for i in range(len(points)):
        if points[i] is None:
            continue

        category = get_category(points[i])
        if category is None:
            points[i] = None
            continue
        threshold = 1612 * 0.02

        merged_points = [points[i]]
        points[i] = None

        for j in range(len(points)):
            if points[j] is None:
                continue

            for merged_point in merged_points:
                cate = get_category(points[j])
                dx = abs(points[j]['x'] - merged_point['x'])
                dy = abs(points[j]['y'] - merged_point['y'])
                if cate == category and dx <= threshold and dy <= threshold:
                    merged_points.append(points[j])
                    points[j] = None
                    break

        names = sorted(set(wiki(point['name_id']) for point in merged_points))
        name = ' / '.join(names)

        item_seasons = defaultdict(list)
        for point in merged_points:
            for item_id in expand_generator(point['generator_group_id']):
                item = wiki.item(item_id)
                item_seasons[item] += point['seasons']
        item_seasons = {item: sorted(set(seasons)) for item, seasons in sorted(item_seasons.items())}
        item_text = ''
        for item, seasons in sorted(item_seasons.items()):
            seasons = sorted(set(seasons))
            if seasons == [0, 1, 2, 3]:
                item_text += '{{i2|' + item + '}}'
            else:
                season_names = ['Spring', 'Summer', 'Autumn', 'Winter']
                season_text = ', '.join(season_names[s] for s in seasons)
                item_text += '{{i2|' + item + '|' + season_text + '}}'

        ret.append({
            'name': name,
            'category': category,
            'items': sorted(item_seasons.keys()),
            'formated_items': item_text,
            'x': sum(point['x'] for point in merged_points) / len(merged_points),
            'y': sum(point['y'] for point in merged_points) / len(merged_points),
        })

    return ret

@cache
def get_gathering_points():
    catchables = get_catchable_resource_points()
    interests = get_interest_points()

    points = []

    for interest in interests:
        if interest['scene'] != 'main':
            continue
        if interest['type'] != 'ResourceArea':
            continue

        behav = read_json(interest['behaviour'])
        trans = read_json(interest['transform'])
        scene_area = read_json(interest['scene_area'])

        positions = []
        for pos_rot in scene_area['points']:
            positions.append([
                trans['m_LocalPosition']['x'] + pos_rot['pos']['x'],
                trans['m_LocalPosition']['z'] + pos_rot['pos']['z'],
            ])

        res_ids = [conf['id'] for conf in behav['weightConfigs'] if conf['weight'] > 0]

        for res_config in behav['weightConfigs']:
            if res_config['weight'] <= 0:
                continue
            res = DesignerConfig.ResourcePoint.get(res_config['id'])
            if res is None:
                continue

            if res['prefabModel'] in catchables:
                continue

            if res['showNameID'] == 0:
                continue

            if behav['maxCount'] == 0:
                continue

            for pos in positions:
                points.append({
                    'name_id': res['showNameID'],
                    'generator_group_id': res['generatorGroup'],
                    'seasons': res['season'],
                    'weathers': res['weatherType'],
                    'x': pos[0],
                    'y': pos[1],
                    'min_scale': res_config['minScale'],
                    'max_scale': res_config['maxScale'],
                })

    return points

if __name__ == '__main__':
    main()
