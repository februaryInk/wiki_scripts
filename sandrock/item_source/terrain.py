from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc import get_terrain_trees
from .common import *

def update_terrain(results: Results) -> None:
    trees_by_prefab = {tree['terrainTreePrefab']: tree for tree in DesignerConfig.TerrainTree}
    for tree in get_terrain_trees():
        proto = trees_by_prefab[tree['prefab']]
        tree_id = proto['id']

        if proto['targetType'] == 1:
            action = 'quarrying'
        else:
            action = 'logging'
        source = [action, tree['scene'], f'tree:{tree_id}']
        update_generator(results, source, proto['chopTrunkDropGroupId'])
        update_generator(results, source, proto['chopStumpDropGroupId'])

        source[0] = 'kicking'
        update_generator(results, source, proto['kickDropGroupId'])
