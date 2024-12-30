'''
Classes for managing Sandrock's asset data.
'''

# Delayed type annotations. Can remove for recent Python versions?
from __future__ import annotations

from sandrock.common import *

# ------------------------------------------------------------------------------

class Asset:
    def __init__(self, bundle: Bundle, info: _AssetInfoJson):
        self.bundle     = bundle
        self.id         = info['path_id']
        self.type       = info['type']
        self.name       = info.get('name')
        self._data: Any = None

    # Lazy load data when it is called.
    @property
    def data(self) -> Any:
        if self._data is None:
            if self.type == 'TextAsset':
                self._data = self.path.read_text()
            else:
                self._data = read_json(self.path)
        return self._data

    # Why do we need this? Ah, for lazy loading the file.
    @property
    def path(self) -> Path:
        if self.type == 'TextAsset':
            ext = 'txt'
        else:
            ext = 'json'
        
        if self.name:
            rel_path = f'{self.type}/{self.name} #{self.id}.{ext}'
        else:
            rel_path = f'{self.type}/{self.id}.{ext}'
        return self.bundle.path / rel_path

    # Is this an output path?
    @property
    def image_path(self) -> Path:
        if self.name:
            rel_path = f'_image_/{self.name} #{self.id}.png'
        else:
            rel_path = f'_image_/{self.id}.png'
        return self.bundle.path / rel_path

    # Script types are being used to determine how we handle their corresponding
    # MonoBehaviours.
    @property
    def script(self) -> str:
        assert self.type == 'MonoBehaviour'
        script_id = self.data['m_Script']['m_PathID']
        return self.bundle.scripts.get(script_id)

    # What are we doing with GameObjects?
    @property
    def transform(self) -> Asset:
        assert self.type == 'GameObject'
        comp_ids = [comp['component']['m_PathID'] for comp in self.data['m_Component']]
        for asset in self.bundle.assets:
            if asset.type == 'Transform' and asset.id in comp_ids:
                return asset

    @property
    def components(self) -> list[Asset]:
        assert self.type == 'GameObject'
        comp_ids = [comp['component']['m_PathID'] for comp in self.data['m_Component']]
        comps = []
        for asset in self.bundle.assets:
            if asset.id in comp_ids:
                comps.append(asset)
        return comps

    @property
    def game_object(self) -> Asset:
        obj_id = self.data['m_GameObject']['m_PathID']
        
        for asset in self.bundle.assets:
            if asset.type == 'GameObject' and asset.id == obj_id:
                for comp in asset.data['m_Component']:
                    comp_id = comp['component']['m_PathID']
                    if comp_id == self.id:
                        return asset
        raise ValueError(f'GameObject not found: {obj_id}')

    # Mission assets are XML format.
    def read_xml(self) -> ElementTree:
        assert self.type == 'TextAsset'
        return ElementTree.fromstring(self.data)

class Bundle:
    def __init__(self, path: PathLike):
        if Path(path).is_absolute():
            self.path = Path(path)
        else:
            self.path = config.assets_root / path

        manifest     = read_json(self.path / 'manifest.json', _ManifestJson)
        self.assets  = [Asset(self, asset_info) for asset_info in manifest['assets'] if not asset_info.get('fail')]
        # Scripts? How are these used?
        self.scripts = {script['id']: script['name'] for script in manifest['scripts']}

    def __iter__(self) -> Iterator[Asset]:
        return iter(self.assets)

    @property
    def behaviours(self) -> list[Asset]:
        return [asset for asset in self.assets if asset.type == 'MonoBehaviour']

# -- Private -------------------------------------------------------------------

# What generates this manifest?
class _ManifestJson(TypedDict):
    assets:  list[_AssetInfoJson]
    scripts: list[_ScriptInfoJson]

class _AssetInfoJson(TypedDict):
    type:      str
    path_id:   int
    container: NotRequired[str]
    name:      NotRequired[str]
    fail:      NotRequired[bool]

_ScriptInfoJson = TypedDict('_ScriptInfoJson', {
    'id':        int,
    'name':      str,
    'class':     str,
    'namespace': str,
})
