from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import get_config_paths

# ------------------------------------------------------------------------------

_substitutions = {
    '<color=#00ff78>': '{{textcolor|green|',
    '<color=#3aa964>': '{{textcolor|green|',
    '</color>': '}}',
    '[ChildCallPlayer]': '\'\'Parent Name\'\'',
    '[MarriageCall|Name]': '\'\'Pet Name\'\'',
    '[NpcName|8121]': '\'\'Child 1\'\'',
    '[NpcName|8122]': '\'\'Child 2\'\'',
    '[Player|Name]': '\'\'Player\'\''
}

def _substitute(string: str) -> str:
    pattern = re.compile('|'.join(re.escape(key) for key in _substitutions.keys()))
    return pattern.sub(lambda match: _substitutions[match.group(0)], string)

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
        
        return _substitute(sep.join(texts))

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
        if True: # language:
            return name
        else:
            return f'({item}) {name}'

    @classmethod
    def monster(cls, id_: int) -> str:
        return cls._designer_config_text('Monster', id_, 'nameId')

    @classmethod
    def npc(cls, id_: int) -> str:
        if id_ == 8000:
            return 'Player'
        if id_ in DesignerConfig.Npc:
            return cls._designer_config_text('Npc', id_, 'nameID')
        else:
            for random_npc in DesignerConfig.RandomNPCData:
                id_low = random_npc['instanceIds']['x']
                id_high = random_npc['instanceIds']['y']

                if id_ >= id_low and id_ <= id_high:
                    # There could be multiple names, but for simplicity we will 
                    # use the first one.
                    name_id = random_npc['nameRange']['x']
                    return cls.text(name_id)
            
            # These names are assigned in story scripts.
            if id_ == 85361:
                return cls.text(80033738) # Linhua
            if id_ == 85362:
                return cls.text(80033737) # Polly-anne
            
            return cls.text(id_)

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

text = _TextEngine()
wiki = _WikiTextEngine()
