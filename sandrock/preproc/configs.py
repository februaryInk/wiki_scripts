'''
Locate the asset files that we expect to have configList attributes.
'''

from __future__ import annotations

from sandrock.common    import *
from sandrock.lib.asset import Bundle

# ------------------------------------------------------------------------------

'''
{
    'text': {'english': './asset_bundles/localization/english/MonoBehaviour/AssetItemEnglish.json'},
    'designer_config': {
        'Npcs': 'asset_bundles/designer_config/MonoBehaviour/AssetItemNpcProtoData.json',
        ...
    }
}
'''
def find_configs() -> _FindConfigsResult:
    configs = {
        'text':            {},
        'designer_config': None,
    }

    for lang in config.languages:
        configs['text'][lang] = _find_text(config.assets_root / 'localization' / lang)

    configs['designer_config'] = _find_designer_configs(config.assets_root / 'designer_config')
    configs['pet'] =  _find_pet(config.assets_root / 'pet')    
    return configs

# -- Private -------------------------------------------------------------------
# Find designer config bundle files.
def _find_designer_configs(designer_config_path: Path) -> dict[str, str]:
    bundle      = Bundle(designer_config_path)
    key_to_path = {}

    # behaviours -> MonoBehaviour files.
    for behav in bundle.behaviours:
        key              = behav.data['key']
        key_to_path[key] = str(behav.path)

    return sorted_dict(key_to_path)

def _find_pet(path: Path) -> dict[str, str]:
    bundle      = Bundle(path)
    key_to_path = {}

    # behaviours -> MonoBehaviour files.
    for behav in bundle.behaviours:
        key              = behav.data['m_Name']
        
        if key != '':
            key_to_path[key] = str(behav.path)

    return sorted_dict(key_to_path)

def _find_text(language_path) -> str:
    bundle = Bundle(language_path)
    for behav in bundle.behaviours:
        # Using that `script` attribute.
        if behav.script == 'AssetItem':
            return str(behav.path)

class _FindConfigsResult(TypedDict):
    text:            dict[str, str]
    designer_config: dict[str, str]
