from sandrock import *
from sandrock.lib.text import load_text
from sandrock.preproc import get_config_paths

pages = [
    'AssetAttrGeneratorConfigGenerator_Attr',
    'AssetCreationConfigCreation',
    'AssetCreationPartConfigCreationPart',
    'AssetEquipmentProtoEquipment',
    'AssetGeneratorGroupConfigGeneratorGroup',
    'AssetGiftItemDataGiftItem',
    'AssetGroupProductBaseDataGroupGoods',
    'AssetGrowthDataGrowthModelConfig',
    'AssetGrowthItemItemGrowth',
    'AssetIllustrationCatalogConfigIllustrationCatalog',
    'AssetIllustrationConfigIllustration',
    'AssetItemAttrGrowthDataAttrGrowth',
    'AssetItemEnglish',
    'AssetItemGeneratorConfigGenerator_Item',
    'AssetItemPrototypeItem',
    'AssetMachineConfigMachine',
    'AssetRefineConfigRefine',
    'AssetRequireProtoRequire',
    'AssetSellProductBaseDataGoods',
    'AssetSendGiftDataGift',
    'AssetStoreBaseDataShop',
    'AssetSyntheticConfigSynthetics',
]

def do() -> None:
    config_paths = get_config_paths()

    text_ids: list[str] = []

    for key, path in config_paths['designer_config'].items():
        for page_name in pages:
            if page_name not in path:
                continue

            items = read_json(path)['configList']
            text_ids += _find_text_ids(items)

            # the order of Encyclopedia items does matter, but lua tables do not keep order
            if 'id' in items[0] and key != 'Illustration':
                items = {item['id']: item for item in items}

            data = {
                'version': config.version,
                'key': key,
                'configList': items
            }
            write_lua(config.output_dir / f'lua/{page_name}.lua', data)

    text_ids = sorted(set(text_ids))
    all_text = load_text(config.wiki_language)
    text = {}
    for id_ in text_ids:
        text[id_] = all_text[id_]

    text_page = 'AssetItem' + config.wiki_language.title()
    write_lua(config.output_dir / f'lua/{text_page}.lua', text)

_text_keys = ['name', 'desc', 'info']

def _find_text_ids(data: Any) -> list[int]:
    text_ids = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, int):
                if any(text_key in key.lower() for text_key in _text_keys):
                    text_ids.append(value)
            else:
                text_ids += _find_text_ids(value)
    if isinstance(data, list):
        for item in data:
            text_ids += _find_text_ids(item)
    return text_ids

if __name__ == '__main__':
    do()
