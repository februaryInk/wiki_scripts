'''
Find all the sources we know of for all items.

In addtion to missing some items, we may be getting false positives. Some 
generators seem to be present but turned off, e.g., Pen's diamond ring drop.
And Logan drops rubber?

And why do some resources like Poplar Wood not get the expected source? Mining
and logging checks not working?

Also, what is AssetFixMissionItemFixMissionItem doing?

Account for BAG ADD ITEM REPLACE.

Requires:
    - designer_config
    - resourcepoint
    - scenes
    - text
'''

from sandrock                  import *
from sandrock.preproc          import get_mission_names
from sandrock.item_source.main import get_item_sources

# Pathea.ScenarioNs.AdditiveScene & Pathea.ScenarioNs.ScenarioModule
# TODO: We could use sceneinfo to look these up now.
_scene_name_to_id = {
    'gecko_dungeon':                32, # Paradise Walk
    'green_house':                  40, # Moisture Farm
    'wild_cave':                    51, # Cave
    'metro_dungeon':                49, # Gecko Station
    'breach_dungeon':               53, # The Breach
    'wreck_dungeon':                63, # Shipwreck Ruins
    'voxel_dungeon_qiheng':         64, # Eufaula Salvage Abandoned Ruins
    'mysterious_cave_dungeon':      66, # Desert Cave
    'portia_tunnel':                69, # Portia Tunnel
    'mole_dungeon':                 70, # Abandoned Mine
    'logancave_dungeon':            71, # Logan's Hideout
    'logancave_1_dungeon':          83,
    'warehouse_dungeon':            73, # Sandrock Storage
    'aviation_dungeon':             74, # Northern Starship Ruins
    'reservoir_dungeon':            78, # Starship Ruins Reservoir
    'stoneforest_dungeon':          79,
    'biologicallaboratory_dungeon': 80,
    'grace_mission_cave':           92, # Cave
}

_manual_implemented = [
    "admiral salt's well-liked fringe group ensemble",
    'album',
    'astronomical telescope',
    'astronomical telescope piece 1',
    'astronomical telescope piece 2',
    'astronomical telescope piece 3',
    'mr. teddy',
    'no thanks, computer',
    'party invitation',
    'pet management chip',  # ?
    'photo of mort and martle',
    'scarab wings',
    'shiny scorpion',
    'xiaohongshu',
]

def main():
    item_sources = get_item_sources()
    format_wiki(item_sources)
    format_unimplemented_items(item_sources)

def format_wiki(item_sources):
    result = defaultdict(dict)
    for item_id, sources in item_sources.items():
        formatted = [format_wiki_source(source, item_id) for source in sources]
        grouped = {}
        for source in formatted:
            if source is None:
                continue
            assert len(source) in [1, 2], source
            if len(source) == 1:
                grouped[source[0]] = True
            else:
                old = grouped.get(source[0])
                if old:
                    grouped[source[0]] = sorted(set(old + [source[1]]))
                else:
                    grouped[source[0]] = [source[1]]
        result[item_id] = sorted_dict(grouped)

    result[10000008]['ruin_abandoned'] = ['Gecko Station Ruins']
    result[10000016]['mission'] = ['Remember the Good Times']
    result[10000102]['ruin_hazard'] = ['The Breach']
    result[10000107]['ruin_hazard'] = ['The Breach']
    result[11000020]['ruin_hazard'] = ['The Breach']
    result[11900000]['mission'].append('Sandrock Strikes Back')
    result[14000009]['mission'] = ['Belly of the Beast']
    result[15000001]['mission'] += ['Goodbye, Nia', 'Welcome to Sandrock!']
    result[15000077]['mission'] = ['Bring a Smile']
    result[15000145]['mission'] = ['Ernest in the Sky With Diamonds']
    result[15000171]['mission'] = ['Fragrant Memories']
    # ...
    result = sorted_dict(result)

    write_lua('lua/ItemSource.lua', result, indent='    ')

def get_name(s: str) -> str:
    type_, id_str = s.split(':')
    return getattr(wiki, type_)(int(id_str))

def get_scene_name(s: str) -> str:
    type_, name_or_id = s.split(':')
    if type_ == 'scene':
        return wiki.scene(int(name_or_id))
    assert type_ == 'scene_name'
    if name_or_id in ['main', 'chamber', 'company', 'guildhall', 'saloon']:
        return '_main_'
    scene_id = _scene_name_to_id.get(name_or_id)
    assert scene_id, name_or_id
    return wiki.scene(scene_id)

_manual_mission = {
    1200127: 'Goodbye, Nia',
    1200128: 'Once More Into the Breach',
    10000007: 'Once More Into the Breach',
    10000009: 'Goodbye, Nia',
    10000020: 'Sandrock Strikes Back',
    11000030: 'Sandrock Strikes Back',
    12000008: 'Civil Business',
    12000010: 'Civil Business',
    12100008: 'Civil Business',
    12200011: 'Picking Up the Slack',
    12300009: 'Civil Business',
    12400003: 'The Childhood Friend',
    12400031: 'The Inspector',
    12400040: 'Welcome to Sandrock!',
    12410008: 'Goodbye, Nia',
    15000002: 'Welcome to Sandrock!',
    15000045: 'Welcome to Sandrock!',
    19810036: 'Belly of the Beast',
    19810037: 'In Trusses we Trust',
    85000017: 'The Childhood Friend',
    89800004: 'Once More Into the Breach',
}

def format_wiki_source(source, item_id=None):
    no_arg = [
        'developer',
        'farming',
        'fishing',
        'kicking',
        'logging',
        'museum',
        'pet',
        'quarrying',
        'ranking',
        'recycle',
        'skiing',
    ]
    if source[0] in no_arg:
        return [source[0]]

    if source[0] == 'abandoned_ruin':
        return ['ruin_abandoned', get_scene_name(source[1])]

    if source[0] == 'container':
        return ['container', get_name(source[1])]

    if source[0] == 'crafting':
        if source[1] == '_assemble_':
            stations = [
                None,
                'Assembly Station',
                'Intermediate Assembly Station',
                'Advanced Assembly Station',
            ]
            return ['assembly', stations[int(source[2])]]

        if source[1] == '_cooking_':
            stations = [
                'Apprentice Cooking Station',
                'Apprentice Cooking Station',
                "Chef's Cooking Station",
                'Advanced Cooking Station',
            ]
            return ['cooking', stations[int(source[2])]]

        if source[1].startswith('item:'):
            return ['crafting', get_name(source[1])]

    if source[0] == 'delivery':
        _, id_str = source[1].split(':')
        return ['delivery', wiki(DesignerConfig.PreOrderPoint[int(id_str)]['nameId'])]

    if source[0] in ['gathering', 'salvaging']:
        scene = get_scene_name(source[1])
        if scene == '_main_':
            return [source[0]]
        else:
            return ['location', scene]

    if source[0] == 'hazard_ruin':
        return  ['ruin_hazard', get_scene_name(source[1])]

    if source[0] == 'mission':
        _, script_id_str = source[2].split(':')
        name = get_mission_names()[int(script_id_str)]
        if isinstance(name, int) and wiki(name):
            return ['mission', wiki(name)]
        if item_id in _manual_mission:
            return ['mission', _manual_mission[item_id]]
        if isinstance(name, int):
            return ['unknownMission', str(name)]
        else:
            return ['unknownMission', name.split(':')[0]]

    if source[0] == 'monster':
        return ['monster', get_name(source[2])]

    if source[0] == 'mort_photo':
        return ['mission', 'Gone with the Wind']

    if source[0] == 'npc':
        if source[1] == 'marry':
            return ['npc', get_name(source[2])]

    if source[0] == 'ore_refining':
        return ['crafting', 'Ore Refinery']

    if source[0] == 'relic':
        return ['crafting', 'Relic Restoration Machine']

    if source[0] == 'store':
        return ['store', get_name(source[1])]

    if source[0] == 'treasure':
        scene = get_scene_name(source[1])
        if scene == 'Cave':
            if item_id in [10000105, 11000027]:
                return None
        return ['treasure', get_scene_name(source[1])]

    raise ValueError(f'Bad item source {source}')

def format_unimplemented_items(item_sources):
    unimplemented = set()
    for item in DesignerConfig.ItemPrototype:
        if item['id'] < 20000000 and text(item['infoId']):
            unimplemented.add(wiki.item(item).lower())
    unimplemented.discard('')
    for item in _manual_implemented:
        unimplemented.discard(item)
    for item_id in item_sources.keys():
        unimplemented.discard(wiki.item(item_id).lower())
    lines = ['return {']
    for item in sorted(unimplemented):
        item = item.replace('"', '\\"')
        lines.append(f'    ["{item}"] = true,')
    lines.append('}')
    write_text('lua/ItemUnimplemented.lua', '\n'.join(lines))

if __name__ == '__main__':
    main()
