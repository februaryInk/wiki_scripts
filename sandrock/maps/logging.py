from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.generator import expand_generator
from sandrock.lib.text import wiki
from sandrock.preproc import get_terrain_trees

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
        if tree_config['targetType'] == 1:
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
            'id': len(markers),
            'categoryId': point['category'],
            'position': [point['x'], point['y']],
            'popup': {
                'title': title,
                #'description': point['formated_items'],
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
    map_data['categories'] = map_data['categories']
    map_data['markers'] = map_data['markers']
    write_json('map/logging.json', map_data)

def _get_icon(category):
    priori = {
        'Bitterbean': 'Bitter Beans',
        'Hyacinth Orchid': 'Hyacinth Orchid',
        'Sand Flower': 'Sand Flower',
        'Yellow Lavender': 'Yellow Lavender',
        #'Cactus Flower Tree': 'Cactus Flower',
        'Foggy Bassia': 'Foggy Bassia',
        #'Dry Boxtree': 'Boxwood',

        'Deadwood': 'Hard Wood',
        'Illusion Tree': 'Medicinal Sap',
        'Large Deadwood': 'Petrified Wood',
        'Pepper Tree': 'Seesai Pepper',
        'Popping Oil Tree': 'Popping Oil Fruit',
        'Sisal Tree': 'Sisal',

        'Avocado Tree': 'Avocado',
        'Acacia Tree': 'Acacia Wood',
        'Dracaena': "Dragon's Blood",
        'Needle Stonecrop': 'Needle Stonecrop',
    }
    if category in priori:
        return priori[category]
    print(category)
    return category + '-icon'

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
        threshold = 0.02

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
            #'prefab': merged_points[0]['prefab'],  # FIXME
            'category': category,
            'num': len(merged_points),
            'x': avg_x * w * 2 - w,
            'y': avg_y * w * 2 - w,
        })

    return ret

main()
