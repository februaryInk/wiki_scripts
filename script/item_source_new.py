'''
Find all the sources we know of for all items.

id: {
    id: ,
    name: ,
    nominal_source: ,
    recipe_sources: ,
    sources:
}

Requires:
    - designer_config
    - resourcepoint
    - sceneinfo
    - scenes
    - season
    - text

Look into:
    - Wedding Candy
    - Civil Corps Medal of Honor
    - Ginger's Diary
'''

from sandrock                        import *
from sandrock.lib.designer_config    import DesignerConfig
from sandrock.lib.text               import text
from sandrock.structures.story       import Story

from sandrock.item_source_new.main   import get_item_sources
from sandrock.item_source_new.common import *

# Magnesese ore, shipwreck ruins

# Recipe sources
#   - Cooking experiment
#   - Research center
#   - Machine unlocks
#   - Owen and Mabel
#   - Scripted unlocks
#       - BLUEPRINT UNLOCK
#       - BLUEPRINT UNLOCK GROUP

# ------------------------------------------------------------------------------

item_prototypes = DesignerConfig.ItemPrototype
scene_name_to_id = sceneinfo.get_scene_system_name_to_id()
story = Story()

_manual_additions = {
    # Xiaohongshu: Gecko Station Abandoned Ruins
    10000008: [('abandoned_ruin', 'scene:60')],
    # Gungam X: Starship Abandoned Ruins
    10000034: [('abandoned_ruin', 'scene:75')],
    # Cynfuls Strike: Saving Grace, Starship Abandoned Ruins
    11000079: [('mission', 'script', 'mission:1200403'), ('abandoned_ruin', 'scene:75')],
    # Assembly Station: Default
    13000004: [('default',)],
    # Water Tank: Default
    13000016: [('default',)],
    # Party Invitation: Party
    15300007: [('party',)],
    # Portia War Drum: All NPCs
    18000177: [('npc', 'showdown_at_high_noon', 'text:52005')],
    # Shiny Scorpion: Sandrock
    19600004: [('gathering', 'scene:3')],
    # Admiral Salt's Well-liked Fringe Group Ensemble: Once More into the Breach
    19810015: [('mission', 'script', 'mission:1600122')],
    # No Thanks, Computer: Once More into the Breach
    19810016: [('mission', 'script', 'mission:1600122')],
    # The Protector: Pen's Last Words
    19810091: [('mission', 'script', 'mission:1700371')],
}

_manual_removals = {
    # Cynfuls Strike: Cave
    11000079: [('treasure', 'scene:grace_mission_cave')],
    # The Protector: Cave, Wild Cave
    19810091: [('treasure', 'scene:grace_mission_cave'), ('treasure', 'scene:wild_cave')]
}

def get_nominal_sources() -> dict[int, dict]:
    item_source_data = DesignerConfig.ItemSourceData
    item_sources = {}
    
    for id, source_data in item_source_data.items():
        description_id = source_data['itemFromDesId']
        machine_ids = source_data['homeMachineSources']

        description_name = text(description_id)
        machine_names = [text.item(machine_id) for machine_id in machine_ids]

        item_sources[id] = {
            'description': description_name,
            'machines': machine_names
        }
    
    return {item_id: [item_sources[source_id] for source_id in item_data['itemFromTypes']] for item_id, item_data in item_prototypes.items()}

def main() -> None:
    nominal_sources = get_nominal_sources()
    item_sources    = get_item_sources()

    for item_id, sources in _manual_additions.items():
        item_sources[item_id].update(sources)
    
    for item_id, sources in _manual_removals.items():
        item_sources[item_id].difference_update(sources)

    results = format_results(item_sources, nominal_sources)
    results = dict(sorted(results.items()))

    unimplemented = format_unimplemented_items(results)

    write_lua(config.output_dir / 'lua/AssetItemSource.lua', results)
    write_lua(config.output_dir / 'lua/AssetItemUnimplemented.lua', unimplemented)

# -- Preparing Results ---------------------------------------------------------

def format_results(item_sources: dict[int, list[ItemSource]], nominal_sources: dict[int, dict]) -> dict[int, dict]:
    results = {}
    for item_id, sources in item_sources.items():
        
        formatted = format_sources(sources, item_id)
        results[item_id] = {
            'name':            text.item(item_id),
            # 'nominal_source':  nominal_sources[item_id],
            'sources':         formatted
        }
    
    return results
    
def format_sources(sources: list[ItemSource], item_id: int) -> list[dict]:
    formatted = {}
    for source in sources:
        format_source(formatted, source, item_id, sources)
    
    return formatted

def format_source(formatted: dict, source: ItemSource, item_id: int, sources: list[ItemSource]) -> None:
    assembly_stations = [
        None,
        'Assembly Station',
        'Intermediate Assembly Station',
        'Advanced Assembly Station'
    ]

    cooking_stations = [
        'Apprentice Cooking Station',
        'Apprentice Cooking Station',
        "Chef's Cooking Station",
        'Advanced Cooking Station'
    ]

    no_arg = [
        'default',
        'dlc',
        'farming',
        'fishing',
        'guild_ranking',
        'kicking',
        'kickstarter',
        'logging',
        'machine_upgrade',
        'museum',
        'party',
        'pet_dispatch',
        'quarrying',
        'recycling',
        'salvaging',
        'sand_racing',
        'sand_sledding'
    ]

    match source[0]:
        case s if s in no_arg:
            formatted[s] = True

        case 'abandoned_ruin':
            add_or_append(formatted, 'ruin_abandoned', get_name(source[1]))

        case 'container':
            add_or_append(formatted, 'container', get_name(source[1]))

        case 'crafting':
            match source[1]:
                case 'assemble':
                    add_or_append(formatted, 'assembly', assembly_stations[int(source[2])])
                case 'cooking':
                    add_or_append(formatted, 'cooking', cooking_stations[int(source[2])])
                case s if s.startswith('item:'):
                    add_or_append(formatted, 'crafting', get_name(source[1]))

        case 'delivery':
            _, id_str = source[1].split(':')
            add_or_append(formatted, 'delivery', wiki(DesignerConfig.PreOrderPoint[int(id_str)]['nameId']))

        case 'event':
            add_or_append(formatted, 'event', get_name(source[2]))
        
        case 'gathering':
            add_or_append(formatted, 'gathering', get_name(source[1]))

        case 'hazard_ruin':
            add_or_append(formatted, 'ruin_hazard', get_name(source[1]))
        
        case 'mail':
            add_or_append(formatted, 'mail', get_name(source[1]))

        case 'mission':
            add_or_append(formatted, 'mission', get_name(source[2]))

        case 'monster':
            add_or_append(formatted, 'monster', get_name(source[2]))

        case 'mort_photo':
            add_or_append(formatted, 'mission', 'Gone with the Wind')

        case 'npc':
            event = source[1]
            npc = get_name(source[2])

            match event:
                case 'birthday':
                    add_or_append(formatted, 'npc', [npc, 'Birthday Gift'])
                case 'child':
                    add_or_append(formatted, 'npc', [npc, 'New Child Gift'])
                case 'conversation':
                    add_or_append(formatted, 'npc', [npc, 'Conversation'])
                case 'day_of_bright_sun':
                    add_or_append(formatted, 'npc', [npc, 'Day of the Bright Sun'])
                case 'marry':
                    add_or_append(formatted, 'npc', [npc, 'Marriage Gift'])
                case 'relationship':
                    add_or_append(formatted, 'npc', [npc, source[3]])
                case 'showdown_at_high_noon':
                    add_or_append(formatted, 'npc', [npc, 'Showdown at High Noon'])
                case 'wedding':
                    add_or_append(formatted, 'npc', [npc, 'Wedding Gift'])
                case 'spouse_cooking':
                    add_or_append(formatted, 'npc', [npc, 'Spouse Cooking'])
                case 'spouse_gift' | 'spouse_gift_expecting':
                    translation = {
                        'spouse_gift': 80031295,
                        'spouse_gift_expecting': 80031297
                    }
                    npc = get_npc(sources, source, event)
                    add_or_append(formatted, 'npc', [npc, text(translation[event])])
                case _:
                    raise ValueError(f'Bad NPC source {source}')

        case 'ore_refining':
            add_or_append(formatted, 'ore_refining', get_name(source[1]))

        case 'relic':
            add_or_append(formatted, 'crafting', 'Relic Restoration Machine')

        case 'store':
            add_or_append(formatted, 'store', get_name(source[1]))

        case 'treasure':
            scene = get_name(source[1])
            if scene == 'Cave' and item_id in [10000105, 11000027]:
                return
            add_or_append(formatted, 'treasure', scene)

        case _:
            breakpoint()
            raise ValueError(f'Bad item source {source}')

def format_unimplemented_items(results: dict[int, dict]) -> list[str]:
    unimplemented = set()

    for item in DesignerConfig.ItemPrototype:
        if item['id'] < 20000000 and item['id'] not in results:
            unimplemented.add(wiki.item(item['id']).lower())
    
    for item_id in results.keys():
        unimplemented.discard(wiki.item(item_id).lower())
    
    unimplemented.discard('')
    unimplemented = sorted(list(unimplemented))
    unimplemented = {item: True for item in unimplemented}
    return unimplemented

def get_npc(sources: list[ItemSource], source: tuple, event: str) -> str:
    all_female_spouses = all_spouses_in_source(sources, event, 1)
    all_male_spouses = all_spouses_in_source(sources, event, 0)
    all_spouses = all_spouses_in_source(sources, event)

    if all_spouses:
        npc = 'all spouses'
    elif all_female_spouses:
        npc = 'all female spouses'
    elif all_male_spouses:
        npc = 'all male spouses'
    else:
        npc = get_name(source[2])
    
    return npc

def add_or_append(formatted: dict, key: str, value: str) -> None:
    if key in formatted:
        values = formatted[key]
        if isinstance(values, list):
            if value not in values:
                values.append(value)
        else:
            values = [values, value]
    else:
        formatted[key] = [value]

def all_spouses_in_source(sources: list[ItemSource], event: str, gender: int = -1) -> bool:
    sources_for_event = [source for source in sources if source[0] == 'npc' and source[1] == event]
    npc_ids_for_event = [int(source[2].split(':')[1]) for source in sources_for_event]

    npc_ids_for_gender = []
    for npc_id, npc_data in DesignerConfig.Npc.items():
        if npc_data['canLove'] != 1 or npc_data['nameID'] == 30020001: continue
        actor = DesignerConfig.Actor[npc_data['templetID']]
        if gender != -1 and actor['gender'] != gender: continue
        npc_ids_for_gender.append(npc_id)
    
    return set(npc_ids_for_event) == set(npc_ids_for_gender)

npc_name_ids = {npc['nameID']: npc['id'] for npc in DesignerConfig.Npc}
def get_name(s: str) -> str:
    type_, id_str = s.split(':')

    if type_ == 'scene':
        if not id_str.isdigit():
            id_str = sceneinfo.scene_id(id_str)
        scene = text.scene(int(id_str))
    
    id = int(id_str)
    if type_ == 'npc':
        if id in npc_name_ids:
            id = npc_name_ids[id]
    if type_ == 'mission':
        name = story.get_mission_name(id)
        if name:
            return name
        else:
            return f'Mission {id}'
    
    return getattr(wiki, type_)(id)

if __name__ == '__main__':
    main()