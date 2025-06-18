from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.preproc             import get_config_paths

# ------------------------------------------------------------------------------

# Manual overrides to force an id for a given name, for situations where item 
# ids are not being resolved otherwise by this script. Use as minimally as 
# possible; sometimes necessary for items misspelled or seemingly duplicated.
_priori = {
    'Cistanche': 16200019,
    'Egg': 19300011,
    'Fish Fossil Piece 1': 19210002,
    'Sand Hat': 12200011, # 21 different Sand Hats. NPC variants?
    'Sand Leek': 16200027,
    'Spoon': 15300022,
    'Tomato': 16200004,
    'Tomato and Egg Soup': 15000012
}

_misspellings = {
    'Boxing Jacks': 'Boxing Jack',
    'SuperStarby': 'Super Starby'
}

# One-off name variants. Assigning an id a variant name here will remove the 
# item from the pool of items that qualify for the base name.
_non_standard_variant_names = {
    14000001: 'Water Tank (assembly)',
    14000044: 'Drill Arm (assembly)',
    15000124: 'Spicy Bean Paste (dish)',
    15000170: 'Spicy Bean Paste (ingredient)',
    15600005: 'Passya Game Kid (toy)',
    19200004: 'Processor (material)',
    19800034: 'Plasticizer (material)',
    19810052: 'Train Model (crafted)',
    85000124: 'Spicy Bean Paste (book for dish)',
    85000170: 'Spicy Bean Paste (book for ingredient)'
}

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

@cache
def load_wiki_names() -> dict[str, int]:
    items         = DesignerConfig.ItemPrototype
    name_to_items = defaultdict(list)
    result        = {}

    item_to_npc = _get_npc_clothing_item_ids()

    for id, item in items.items():
        base_name = text.item(id)

        if "￥not use￥" in base_name:
            continue

        name = _preemptively_choose_variant_name(item, base_name, item_to_npc)
        name_to_items[name].append(item)

    # Overwrite names with priority manual overrides.
    for priori_name, priori_id in _priori.items():
        if priori_id is None:
            if priori_name in name_to_items:
                name_to_items.pop(priori_name)
        else:
            name_to_items[priori_name] = [items[priori_id]]
    
    for name, name_items in name_to_items.items():
        if not name:
            continue
        # Only one candidate for this item name. Easy.
        if len(name_items) == 1:
            item = name_items[0]
            result[item['id']] = name
        # Multiple candidates for this item name. 
        else:
            # Find out if some of these items are variants for which we can 
            # programatically determine an alternative name.
            items_by_variant_name = defaultdict(list)

            for item in name_items:
                variant_name = _choose_variant_name(item, name)
                items_by_variant_name[variant_name].append(item)
            
            for variant_name, variant_items in items_by_variant_name.items():
                if len(variant_items) == 1:
                    variant_item = variant_items[0]
                    result[variant_item['id']] = variant_name
                # We still have more than one item in this variant group.
                else:
                    print(f'Warning: More than one item for {variant_name}, attempting to resolve...')
                    # See if we can figure out the "right" one to use.
                    variant_item = _choose_item(variant_items)
                    if variant_item is None:
                        min_id = min([i["id"] for i in variant_items if "id" in i])
                        print(f'Could not resolve: {variant_name}; using lowest item ID {min_id}. \n')
                        result[min_id] = variant_name
                    else:
                        result[variant_item['id']] = variant_name
    
    return result

# ------------------------------------------------------------------------------

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
                    name = cls.text(name_id)
                    return _misspellings.get(name, name)
            
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
    @classmethod
    def item(cls, item_id: int | dict[str, Any]) -> str:
        return load_wiki_names().get(item_id, None)

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

# ------------------------------------------------------------------------------

def _choose_item(items):
    conditions = [
        lambda item: item['maleIconPath'].lower() != 'null',
        lambda item: text(item['infoId']),
        lambda item: item['id'] < 20000000
    ]
    for condition in conditions:
        items = [item for item in items if condition(item)]
        if len(items) == 0:
            print(f'Warning: No items meet conditions.')
            return None
        if len(items) == 1:
            return items[0]
    
    # Items with color variants often use the same maleIconPath with a number 
    # appended. We'll use the base (lowest number) item to refer to all
    # color variants.
    lowest_version      = None
    lowest_version_item = None
    common_base_mip     = None

    # Favors lowest ID item, in the event that the mips are all the same.
    items = sorted(items, key=lambda x: (x['id']))
    for item in items:
        mip           = item['maleIconPath'].lower()
        version_match = re.search(r'_(([0-9]+_?)+)$', mip)

        if version_match:
            version_str = version_match.group(1)
            item_version = float('.'.join(version_str.split('_')))
            base_mip = re.sub(r'(_[0-9]+)+$', '', mip)
        else:
            item_version = 0
            base_mip = mip

        if common_base_mip is None:
            common_base_mip = base_mip
        elif base_mip != common_base_mip:
            print(f'Warning: {base_mip} not equal to {common_base_mip}; not color variants.')
            lowest_version_item = None
            break

        if lowest_version is None or item_version < lowest_version:
            lowest_version = item_version
            lowest_version_item = item
    
    return lowest_version_item

def _choose_variant_name(item, base_name):
    # Chromium Steel Bearings, possibly mismarked with tag 5?
    if id == 19112011:
        return base_name
    
    mip = item['maleIconPath'].lower()
    if mip is None: return base_name

    # Recipe books have the same names as the items they teach the builder to
    # produce. Most will have been caught by the preemptive name variant method,
    # but there are still a few left.
    if mip.startswith("item_book") or mip.startswith('book_') or mip == "item_instructionbook":
        if not base_name.lower().endswith('(book)'):
            return f'{base_name} (book)'
    
    return base_name

def _get_npc_clothing_item_ids() -> dict[int, str]:
    npc_clothing      = DesignerConfig.NpcClothItem
    result            = {}
    sections_to_check = [
        'accessoryItemIds',
        'bodyItemIds',
        'footItemIds',
        'headItemIds',
        'shoesItemIds'
    ]

    for clothing_data in npc_clothing:
        npc_name = text.npc(clothing_data['npcId'])

        for section in sections_to_check:
            section_data = clothing_data[section]

            for item_id in section_data:
                if item_id not in result:
                    result[item_id] = npc_name
                else:
                    # If the item is already assigned to a different NPC, we will
                    # not overwrite it.
                    if result[item_id] != npc_name:
                        print(f'Warning: Item {item_id} is assigned to multiple NPCs: {result[item_id]} and {npc_name}.')
    
    return result

# Names that the item should be assigned even if there isn't a conflict with another
# item.
def _preemptively_choose_variant_name(item, base_name, item_to_npc: dict[int, str]) -> str:
    id   = item['id']
    mip  = item['maleIconPath'].lower()
    tags = item['tags']

    if id in _non_standard_variant_names:
        return _non_standard_variant_names[id]
    
    if id > 70000000 and id < 80000000 and 5 in tags:
        return f'{base_name} (style)'
    
    if id > 81000000 and 5 in tags:
        return f'{base_name} (book)'

    # NPC clothes and accessories often have name overlap, so we'll indicate the
    # NPC name by default in the item name.
    if id in item_to_npc:
        npc_name = item_to_npc[id]
        return f'{base_name} ({npc_name})'
    
    return base_name

text = _TextEngine()
wiki = _WikiTextEngine()
