'''
Classes for managing Sandrock's asset bundles (Bundle) and files (Asset).
'''

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
                self._data = self.path.read_text(encoding='utf-8')
            elif self.type == 'MonoBehaviour':
                self._data = read_json(self.path)
            else:
                self._data = read_asset_dump(self.path) 
        return self._data

    # Why do we need this? Ah, for lazy loading the file.
    @property
    def path(self) -> Path:
        if self.type == 'MonoBehaviour':
            ext = 'json'
        elif self.type == 'TextAsset':
            ext = 'xml'
        else:
            ext = 'txt'
        
        if self.name:
            rel_path = f'{self.type}/{self.name} @{self.id}.{ext}'
        else:
            rel_path = f'{self.type}/{self.id}.{ext}'
        return self.bundle.path / rel_path

    # Is this an output path? What assets have images associated?
    @property
    def image_path(self) -> Path:
        if self.name:
            rel_path = f'{self.type}/{self.name} @{self.id}.png'
        else:
            rel_path = f'{self.type}/{self.id}.png'
        return self.bundle.path / rel_path

    # Script types are being used to determine how we handle their corresponding
    # MonoBehaviours.
    @property
    def script(self) -> str:
        if self.type == 'MonoBehaviour':
            script_id = self.data['m_Script']['m_PathID']
            return self.bundle.scripts.get(script_id)
        
    # What are we doing with GameObjects?
    @property
    def transform(self) -> Asset:
        assert self.type == 'GameObject'
        comp_ids = [comp['component']['m_PathID'] for comp in self.data['m_Component']['Array']]
        for asset in self.bundle.assets:
            if asset.type == 'Transform' and asset.id in comp_ids:
                return asset

    @property
    def components(self) -> list[Asset]:
        assert self.type == 'GameObject'
        comp_ids = [comp['component']['m_PathID'] for comp in self.data['m_Component']['Array']]
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
                #print(asset.path)
                #print(json.dumps(asset.data, indent=2))
                for comp in asset.data['m_Component']['Array']:
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

        # manifest     = read_json(self.path / 'manifest.json', _ManifestJson)
        # self.assets  = [Asset(self, asset_info) for asset_info in manifest['assets'] if not asset_info.get('fail')]
        # Scripts? How are these used? Oh...we don't need the script files, just
        # inclusion in the manifest so we can check names.
        # self.scripts = {script['id']: script['name'] for script in manifest['scripts']}
        self.assets = []
        self.scripts = {}

        manifest = _ManifestXml(self.path / 'assets.xml')
        for asset_info in manifest:
            if asset_info['type'] == 'MonoScript':
                self.scripts[asset_info['path_id']] = asset_info['name']
            else:
                self.assets.append(Asset(self, asset_info))

    def __iter__(self) -> Iterator[Asset]:
        return iter(self.assets)

    @property
    def behaviours(self) -> list[Asset]:
        return [asset for asset in self.assets if asset.type == 'MonoBehaviour']

class BundleGroup:
    def __init__(self, path: PathLike):
        if Path(path).is_absolute():
            self.path = Path(path)
        else:
            self.path = config.assets_root / path

# -- Private -------------------------------------------------------------------

class _ManifestXml():
    def __init__(self, path: PathLike):
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()

    def __iter__(self) -> Iterator[_AssetInfoJson]:
        for asset in self.root.findall('Asset'):
            asset_dict = {child.tag: child.text for child in asset}
            asset_dict = {
                'container': asset.find('Container').text,
                'name': asset.find('Name').text,
                'path_id': int(asset.find('PathID').text),
                'type': asset.find('Type').text,
                'type_id': int(asset.find('Type').get('id'))
            }
            yield asset_dict

# What generates this manifest? The only one I can get from AssetStudioMod is 
# XML.
class _ManifestJson(TypedDict):
    assets:  list[_AssetInfoJson]
    scripts: list[_ScriptInfoJson]

class _AssetInfoJson(TypedDict):
    type:      str
    path_id:   int
    container: NotRequired[str]
    name:      NotRequired[str]
    fail:      NotRequired[bool]
    type_id:   NotRequired[int]

_ScriptInfoJson = TypedDict('_ScriptInfoJson', {
    'id':        int,
    'name':      str,
    'class':     str,
    'namespace': str,
})
