'''
Parses information regarding abandoned ruins and their contents.
'''

from __future__ import annotations

from sandrock import *
from sandrock.structures.generators import GeneratorGroup

# ------------------------------------------------------------------------------

abandoned_ruins = {
    6: 'Eufaula Salvage',
    60: 'Gecko Station',
    72: 'Mole Cave',
    75: 'Starship'
}

voxel_types = [
    'base',
    'normal',
    'good',
    'rare'
]

abandoned_ruin_data = DesignerConfig.AbandonedDungeon
voxel_info_data = DesignerConfig.VoxelTypeInfo

# ------------------------------------------------------------------------------

class AbandonedRuin:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.name: str = abandoned_ruins.get(id, "Unknown")
        
        self.set_layers()
    
    def set_layers(self) -> None:
        layers = []

        for layer_data in abandoned_ruin_data:
            if layer_data['scene'] == self.id:
                layers.append(AbandonedRuinLayer(layer_data))

        self.layers = layers
    
    @property
    def layer_count(self) -> int:
        return len(self.layers)
    
    @property
    def voxel_map(self) -> dict[int, Voxel]:
        voxel_map = {}

        for i, layer in enumerate(self.layers):
            for voxel_id in layer.voxel_ids:
                if voxel_id not in voxel_map:
                    voxel_map[voxel_id] = {
                        'layers': [i],
                        'voxel': Voxel(voxel_id)
                    }
                else:
                    voxel_map[voxel_id]['layers'].append(i)

        return voxel_map

class AbandonedRuinLayer:
    def __init__(self, data: dict) -> None:
        self._data: dict = data

        self.set_voxel_settings()
    
    def set_voxel_settings(self) -> None:
        voxels = {}

        for type in voxel_types:
            voxels[type] = []

            # Is the second value actually a rarity weight, or is it something 
            # else?
            for voxel_id_weight in self._data[f'{type}Voxel'].split(','):
                id, weight = map(int, voxel_id_weight.split('_'))
                voxels[type].append({'id': id, 'weight': weight})

        self.voxel_settings = voxels

    @property
    def voxel_ids(self) -> list[int]:
        ids = []

        for voxel_list in self.voxel_settings.values():
            for voxel in voxel_list:
                ids.append(voxel['id'])
        
        return ids

class Voxel:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self._data: dict = next(
            (data for data in voxel_info_data if data['type'] == id),
            {}
        )
    
    @cached_property
    def experience(self) -> int:
        return self._data.get('exp', 0)
    
    @cached_property
    def generator(self) -> GeneratorGroup | None:
        group_id = self._data['itemDropId']

        return GeneratorGroup(group_id)
    
    @cached_property
    def image(self) -> str:
        return f'{{{{img|Abandoned_Ruin_Patch_{self._data["showType"]}|size=100px}}}}'
        
# ------------------------------------------------------------------------------

def load_abandoned_ruins() -> dict[int, AbandonedRuin]:
    ruins = {id: AbandonedRuin(id) for id in abandoned_ruins.keys()}

    return ruins

abandoned_ruins = load_abandoned_ruins()