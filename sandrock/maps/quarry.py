from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.generator       import expand_generator
from sandrock.lib.text            import wiki
from sandrock.preproc             import get_terrain_trees

@cache
def find_tree_config(prefab):
    for config in DesignerConfig.TerrainTree:
        if config['terrainTreePrefab'] == prefab:
            return config

def main():
    terrain_trees = get_terrain_trees()
    trees = []

    for terrain_tree in terrain_trees:
        if terrain_tree['scene'] != 'main.summer':
            continue

        tree_config = find_tree_config(terrain_tree['prefab'])
        if tree_config['targetType'] != 1:
            continue

        trees.append(terrain_tree)

    points = merge_trees(trees)
    points = sorted(points, key=(lambda point: point['category']))

    categories = {}

    markers = []
    for point in points:
        if abs(point['x']) > 1612 or abs(point['y']) > 1612:
            continue

        title = point['category']
        if point['num'] > 1:
            title += ' ×' + str(point['num'])

        markers.append({
            'categoryId': point['category'],
            'position': [point['x'], point['y']],
            'popup': {
                'title': title,
                #'description': get_items(point['category']),
            },
        })

        if point['category'] not in categories:
            icon = _get_icon(point['category'])
            categories[point['category']] = {
                'id': point['category'],
                'listId': None,
                'name': point['category'],
                'color': '#000000',
                'icon': icon + '.png',
            }

    manual = {
        'categoryId': 'Raw Opal',
        'position': [355.7, 379.08],
        'popup': {
            'title': 'Raw Opal',
            'description': 'About 16 [[Opal]] on average.<br>Never respawn.',
        },
    }
    markers = [manual] + markers

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
    write_json('map/quarrying.json', map_data)

def get_items(name):
    item_ids = set()
    for conf in DesignerConfig.TerrainTree:
        if wiki.tree(conf['id']) == name:
            for item_id in expand_generator(conf['chopTrunkDropGroupId']):
                item_ids.add(item_id)
    item_names = [wiki.item(item_id) for item_id in item_ids]
    item_names = sorted(item_names)

    return '{{i2|' + '}}{{i2|'.join(item_names) + '}}'

def _get_icon(category):
    priori = {
        'Gravel': 'Gravel-concept',
        'Hard Rock': 'Hard Rock-concept',
        'Raw Lapis Lazuli': 'Lapis Lazuli',
        'Raw Minerals': 'Graphite',
        'Raw Opal': 'Opal',
    }
    if category in priori:
        return priori[category]
    return category

def get_category(point):
    conf = find_tree_config(point['prefab'])
    return wiki(conf['nameId'])

def merge_trees(points):
    ret = []

    for i, _ in enumerate(points):
        if points[i] is None:
            continue

        x = points[i]['position']['x'] * 4096 - 2048
        y = points[i]['position']['z'] * 4096 - 2048
        if abs(x) > 1612 or abs(y) > 1612:
            points[i] = None
            continue

        category = get_category(points[i])
        threshold = 0.005 if category == 'Raw Opal' else 0.01

        merged_points = [points[i]]
        points[i] = None

        for j, _ in enumerate(points):
            if points[j] is None:
                continue

            for merged_point in merged_points:
                cate = get_category(points[j])
                dx = abs(points[j]['position']['x'] - merged_point['position']['x'])
                dy = abs(points[j]['position']['z'] - merged_point['position']['z'])
                if cate == category and dx <= threshold and dy <= threshold:
                    merged_points.append(points[j])
                    points[j] = None
                    break
        
        avg_x = sum(point['position']['x'] for point in merged_points) / len(merged_points)
        avg_y = sum(point['position']['z'] for point in merged_points) / len(merged_points)

        w = 2048
        ret.append({
            'category': category,
            'num': len(merged_points),
            'x': avg_x * w * 2 - w,
            'y': avg_y * w * 2 - w,
        })

    return ret

main()
