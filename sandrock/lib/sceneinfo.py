'''
The sceneinfo bundle helps us match scene meta names and bundle names to the 
scene IDs.
'''

from sandrock.common    import *
from sandrock.lib.asset import Bundle

# ------------------------------------------------------------------------------

class _SceneInfoEngine:
    
    _scene_bundle: Bundle = Bundle(config.assets_root / 'sceneinfo')
    _scene_system_name_to_id: dict[str, int] = None

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
        keys = []
        scene_system_name_to_id = cls.get_scene_system_name_to_id()

        for key in scene_system_name_to_id.keys():
            if key.lower().replace('_', '') == name.lower().replace('_', ''):
                keys.append(key)
        assert len(keys) == 1

        return scene_system_name_to_id[keys[0]]
    
    @classmethod
    def scene_system_name(cls, id: int) -> str:
        keys = []
        scene_system_name_to_id = cls.get_scene_system_name_to_id()

        for key, val in scene_system_name_to_id.items():
            if val == id:
                keys.append(key)
        assert len(keys) == 1
        
        return keys[0]
    
    @classmethod
    def get_scene_system_name_to_id(cls) -> dict[str, int]:
        if not cls._scene_system_name_to_id:
            cls._scene_system_name_to_id = {}
            for scene in cls._scene_bundle:
                if scene.script == 'SceneInfoObj':
                    id = cls.get_scene_id_from_data(scene.data)
                    name = scene.data['m_Name']
                    if id == 90 or id == 60:
                        print(id)
                        print(name)
                    assert name not in cls._scene_system_name_to_id
                    cls._scene_system_name_to_id[name] = id

        # Test the assumption that every scene has a unique system name.
        # It fails. Both 60 and 90 have multiple names:
        # 60, Gecko Station Abandoned Ruins: VoxelDungeon2, BuriedRoomTest
        # 90, Dead Sea Ruins: InfiniteTrialDungeon, TrialDungeon_Infinite, RollerCoaster
        # assert len(cls._scene_system_name_to_id) == len(set(cls._scene_system_name_to_id.values()))
        return cls._scene_system_name_to_id
    
# ------------------------------------------------------------------------------

scenes = _SceneInfoEngine()