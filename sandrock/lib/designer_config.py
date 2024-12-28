# Go away?
from __future__ import annotations

from sandrock.common    import *
from sandrock.lib.asset import Bundle
from sandrock.preproc   import get_config_paths

# ------------------------------------------------------------------------------

# Shouldn't this be private? Only called in this file?
# Load an asset file under designer_config that has the given key.
@cache
def load_designer_config(key: str) -> _DesignerConfigData | None:
    # config_paths: Paths to assets we expect to have a `configList` attribute.
    config_paths = get_config_paths()
    path         = config_paths['designer_config'][key]
    data         = read_json(path)
    configs      = data['configList']
    
    if not configs:
        return None
    if isinstance(configs[0].get('id'), int):
        return sorted_dict({conf['id']: conf for conf in configs})
    elif isinstance(configs[0].get('ID'), int):
        return sorted_dict({conf['ID']: conf for conf in configs})
    else:
        return configs

# -- Private -------------------------------------------------------------------

_DesignerConfigItem: TypeAlias = dict[str, Any]
_DesignerConfigData: TypeAlias = dict[int, _DesignerConfigItem] | list[_DesignerConfigItem]

class _DesignerConfigLoader:
    # Square bracket syntax.
    def __getitem__(self, key: str) -> _DesignerConfigWrapper:
        config = load_designer_config(key)
        assert config is not None
        return _DesignerConfigWrapper(config)

    # Dot syntax.
    def __getattr__(self, key: str) -> _DesignerConfigWrapper:
        return self[key]

# Wraps the data and behaves essentially as though it IS the data.
class _DesignerConfigWrapper:
    def __init__(self, data: _DesignerConfigData):
        self._data = data

    def __getitem__(self, key: int) -> _DesignerConfigItem:
        return self._data[key]

    # x in this?
    def __contains__(self, key: int | _DesignerConfigItem) -> bool:
        if isinstance(key, int):
            assert isinstance(self._data, dict)
            return key in self._data
        if isinstance(self._data, dict):
            return key in self._data.values()
        else:
            return key in self._data

    # Iteration behavior.
    def __iter__(self) -> Iterator[_DesignerConfigItem]:
        if isinstance(self._data, dict):
            return iter(self._data.values())
        else:
            return iter(self._data)

    def items(self) -> Iterable[tuple[int, _DesignerConfigItem]]:
        assert isinstance(self._data, dict)
        return self._data.items()

    def keys(self) -> Iterable[int]:
        assert isinstance(self._data, dict)
        return self._data.keys()

    def values(self) -> Iterable[_DesignerConfigItem]:
        assert isinstance(self._data, dict)
        return self._data.values()

    def get(self, key: int) -> _DesignerConfigItem | None:
        assert isinstance(self._data, dict)
        return self._data.get(key)

# -- Export --------------------------------------------------------------------

DesignerConfig = _DesignerConfigLoader()