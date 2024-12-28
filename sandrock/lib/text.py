from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc import get_config_paths

# ------------------------------------------------------------------------------

@cache
def load_text(language: str) -> dict[int, str]:
    config_paths = get_config_paths()
    path         = config_paths['text'][language]
    data         = read_json(path)
    texts        = {config['id']: config['text'] for config in data['configList']}

    return sorted_dict(texts)

class _TextEngine:
    @staticmethod
    def text(text_id: int, language: str | None = None, sep: str = '  ') -> str:
        texts = []
        for lang, code in zip(config.languages, config.language_codes):
            if language and language != lang and language != code:
                continue
            s = load_text(lang).get(text_id)
            if s:
                texts.append(s)
        return sep.join(texts)

    @classmethod
    def __call__(cls, text_id: int, lang_or_sep: str | None = None) -> str:
        if lang_or_sep is None:
            return cls.text(text_id)
        lang = None
        sep = '  '
        if lang_or_sep in config.languages or lang_or_sep in config.language_codes:
            lang = lang_or_sep
        else:
            sep = lang_or_sep
        return cls.text(text_id, lang, sep)

    # Find the text for a particular asset (config_key), item id, and attribute.
    @classmethod
    def _designer_config_text(cls, config_key: str, id_: int, field_name: str, language: str | None = None) -> str:
        return cls.text(DesignerConfig[config_key][id_][field_name], language)

    @classmethod
    def item(cls, item: int | dict[str, Any], language: str | None = None) -> str:
        if isinstance(item, dict):
            item = item['id']
        name = cls._designer_config_text('ItemPrototype', item, 'nameId', language)
        if language:
            return name
        else:
            return f'({item}) {name}'

    @classmethod
    def monster(cls, id_: int) -> str:
        return cls._designer_config_text('Monster', id_, 'nameId')

    @classmethod
    def npc(cls, id_: int) -> str:
        return cls._designer_config_text('Npc', id_, 'nameID')

    #@classmethod
    #def resource(cls, id_):
    #    return cls._designer_config_text('ResourcePoint', id_, 'showNameID')

    @classmethod
    def scene(cls, id_: int) -> str:
        scenes = [scene for scene in DesignerConfig.Scene if scene['scene'] == id_]
        return cls.text(scenes[0]['nameId'])

    @classmethod
    def store(cls, id_: int) -> str:
        return cls._designer_config_text('StoreBaseData', id_, 'shopName')

    #@classmethod
    #def tree(cls, id_):
    #    return cls._designer_config_text('TerrainTree', id_, 'nameId')

class _WikiTextEngine(_TextEngine):
    @staticmethod
    def text(text_id: str, *arg, **kwargs) -> str:
        return load_text(config.wiki_language)[text_id]

    @classmethod
    def item(cls, item: int | dict[str, Any]) -> str:
        # FIXME: disambiguation
        if isinstance(item, dict):
            item = item['id']
        name = cls._designer_config_text('ItemPrototype', item, 'nameId')
        if item >= 80000000:
            return name + ' (Book)'
        if item >= 70000000:
            return name + ' (Style)'
        return name

    @classmethod
    def scene(cls, id_: int) -> str:
        manual = {
            32: 'Paradise Lost',
            35: 'The Breach',
            63: 'Shipwreck Hazardous Ruins',
            71: "Logan's Hideout",
        }
        if id_ in manual:
            return manual[id_]
        return super().scene(id_)

    #@classmethod
    #def scene(cls, id_: int) -> str:
    #    name = super().scene(id_)
    #    manual_fix = {
    #        'Paradise Walk': 'Paradise Lost',
    #        'Shipwreck Hazardous Ruins': 'Shipwreck',
    #        'Shipwreck Ruins': 'Shipwreck Hazardous Ruins',
    #        'The Breach Hazardous Ruins': 'The Breach',
    #    }
    #    return manual_fix.get(name, name)

text = _TextEngine()
wiki = _WikiTextEngine()
