'''
The sceneinfo bundle helps us match scene meta names and bundle names to the 
scene IDs.
'''

from sandrock.common              import *
from sandrock.lib.asset           import Asset, Bundle
from sandrock.lib.designer_config import DesignerConfig

# ------------------------------------------------------------------------------

# The sceneinfo bundle does not contain data for *all* scenes, but the remainder
# that are given in AssetConfigSceneConfig are either duplicates or unnamed.
# 
# Is this supposed to be a clue? I don't know what "ScenarioModule" is:
# Pathea.ScenarioNs.AdditiveScene & Pathea.ScenarioNs.ScenarioModule
#
# In AssetConfigSceneConfig, but absent from _scene_system_name_to_id:
# 48: No name
# 52: 'Eufaula Salvage Abandoned Ruins', see 64
# 61: 'Gecko Station Abandoned Ruins', see 60
# 89: No name

class _SceneInfoEngine:
    
    _scene_config: Asset = DesignerConfig.Scene
    _scene_bundle: Bundle = Bundle(config.assets_root / 'sceneinfo')
    _scene_system_name_to_id: dict[str, int] = None
    _manual: dict[str, int] = {
        'VoxelDungeon2':        60,
        'InfiniteTrialDungeon': 90
    }

    @staticmethod
    def get_scene_id_from_data(data: dict[str, Any]) -> int:
        ids = []
        data_to_check = [
            'sceneAreaDatas', 
            'sceneDramaDatas', 
            'sceneExtranceDatas',
            'scenePointDatas'
        ]
        for key in data_to_check:
            ids += [item['scene'] for item in data[key]]
        # PlayerHome has nothing in it by default, so it doesn't have any data 
        # to let us know the scene ID.
        if data['m_Name'].lower() == 'playerhome': ids += [5]
        ids = list(set(ids))

        assert len(ids) == 1
        return ids[0]

    @classmethod
    def scene_id(cls, name: str) -> int:
        scene_system_name_to_id = cls.get_scene_system_name_to_id()

        for key in scene_system_name_to_id.keys():
            if key.lower().replace('_', '') == name.lower().replace('_', ''):
                return scene_system_name_to_id[key]
    
    @classmethod
    def scene_name(cls, id: int) -> str:
        for config in cls._scene_config:
            if config['scene'] == id:
                return text(config['nameId'])
    
    @classmethod
    def scene_system_name(cls, id: int) -> str:
        scene_system_name_to_id = cls.get_scene_system_name_to_id()

        for key, val in scene_system_name_to_id.items():
            if val == id:
                return key
    
    @classmethod
    def get_scene_system_name_to_id(cls) -> dict[str, int]:
        if not cls._scene_system_name_to_id:
            cls._scene_system_name_to_id = {}
            for scene in cls._scene_bundle:
                if scene.script == 'SceneInfoObj':
                    id = cls.get_scene_id_from_data(scene.data)
                    name = scene.data['m_Name']
                    assert name not in cls._scene_system_name_to_id

                    if id in cls._manual.values():
                        print(f'Warning: Assigning manual value to scene {id} that has inferred name {name}')
                        continue

                    cls._scene_system_name_to_id[name] = id
            
            cls._scene_system_name_to_id = cls._scene_system_name_to_id | cls._manual

            sorted_scenes = dict(sorted(cls._scene_system_name_to_id.items(), key=lambda item: item[1]))
            print(json.dumps(sorted_scenes, indent=2))

        # Test the assumption that every scene has a unique system name.
        # It fails without manual assigment. Both 60 and 90 have multiple names:
        # 60, Gecko Station Abandoned Ruins: VoxelDungeon2, BuriedRoomTest
        # 90, Dead Sea Ruins: InfiniteTrialDungeon, TrialDungeon_Infinite, RollerCoaster
        # Went with PermDenied's values.
        assert len(cls._scene_system_name_to_id) == len(set(cls._scene_system_name_to_id.values()))
        return cls._scene_system_name_to_id
    
# ------------------------------------------------------------------------------

sceneinfo = _SceneInfoEngine()