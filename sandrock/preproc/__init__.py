from __future__ import annotations

from sandrock.common import *

# If we are enforcing types.
if TYPE_CHECKING:
    from .configs         import _FindConfigsResult
    from .interest_points import InterestPoint
    from .terrain_tree    import TerrainTree

# ------------------------------------------------------------------------------

# T for type.
T = TypeVar('T')

@cache
def get_config_paths() -> _FindConfigsResult:
    from .configs import find_configs
    return _presistent_cached('config_path', find_configs)

@cache
def get_interest_points() -> list[InterestPoint]:
    from .interest_points import find_interest_points
    return _presistent_cached('interest_points', find_interest_points)

@cache
def get_catchable_resource_points() -> dict[str, str]:
    from .catchable_resource import find_catchable_resource_points
    return _presistent_cached('salvaging_resource_points', find_catchable_resource_points)

@cache
def get_terrain_trees() -> list[TerrainTree]:
    from .terrain_tree import find_terrain_trees
    return _presistent_cached('terrain_trees', find_terrain_trees)

@cache
def get_mission_names() -> dict[int, str | int]:
    from .mission import find_mission_names
    data = _presistent_cached('mission_name', find_mission_names)
    return {int(k): v for k, v in data.items()}

_Func: TypeAlias = Callable[[], T]

def presistent_cached(cache_key: str) -> Callable[[_Func], _Func]:
    def decorator(func: _Func) -> _Func:
        def decorated_func() -> T:
            return _presistent_cached(cache_key, func)
        return decorated_func
    return decorator

def _presistent_cached(cache_key: str, func: Callable[[], T], purge: bool = False) -> T:
    cache_path = config.cache_root / f'{cache_key}.json'

    if not purge:
        try:
            cache = read_json(cache_path)
            if cache['version'] == config.version:
                return cache['data']
        except Exception:
            pass

    data = func()
    cache = {'version': config.version, 'data': data}
    write_json(cache_path, cache)
    return data
