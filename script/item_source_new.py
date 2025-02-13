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
    - Lovely Seashell

Add sources for NPC clothing articles, even though they're not able to be put in 
the inventory?
'''

from sandrock                        import *
from sandrock.lib.designer_config    import DesignerConfig
from sandrock.lib.text               import text
from sandrock.structures.story       import Story

from sandrock.item_source_new.main   import get_item_sources
from sandrock.item_source_new.common import *

# Magnesese ore, shipwreck ruins
# Civil Corps commissions
# Tumbleweeds
# Lovely Seashell is wrong?
# No boxing jack

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
    18000177: [('showdown_at_high_noon',)],
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
        item_nominal_sources = nominal_sources[item_id]
        main_sources, secondary_sources = get_main_sources(item_id, formatted, item_nominal_sources)

        results[item_id] = {
            'name':              text.item(item_id),
            # 'nominal_source':  nominal_sources[item_id],
            'mainSources':      main_sources,
            'secondarySources': secondary_sources,
            # 'sources':           formatted
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
        'civil_corps_commission',
        'day_of_bright_sun',
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
        'sand_sledding',
        'showdown_at_high_noon'
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
            mail_id = int(source[2].split(':')[1])
            add_or_append(formatted, 'mail', [get_name(source[1]), mail_id])

        case 'mission':
            add_or_append(formatted, 'mission', get_name(source[2]))

        case 'monster':
            add_or_append(formatted, 'monster', get_name(source[2]))

        case 'mort_photo':
            add_or_append(formatted, 'mission', 'Gone with the Wind')

        case 'npc':
            event = source[1]
            npc = get_name(source[2])
            if 'npc' not in formatted:
                formatted['npc'] = {}
            formatted_npc = formatted['npc']

            match event:
                case 'birthday':
                    add_or_append(formatted_npc, 'birthday', npc)
                case 'child':
                    add_or_append(formatted_npc, 'new_child', npc)
                case 'conversation':
                    add_or_append(formatted_npc, 'conversation', npc)
                case 'marry':
                    add_or_append(formatted_npc, 'marriage', npc)
                case 'relationship':
                    if source[3] == 'Married':
                        add_or_append(formatted_npc, 'marriage', npc)
                    else:
                        raise ValueError(f'Unhandled NPC source {source} with value {source[3]}')
                case 'wedding':
                    add_or_append(formatted_npc, 'wedding', npc)
                case 'spouse_cooking':
                    add_or_append(formatted_npc, 'spouse_cooking', npc)
                case 'spouse_gift' | 'spouse_gift_expecting':
                    npc = get_npc(sources, source, event)
                    add_or_append(formatted_npc, event, npc)
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

def find_matches(item_id: int, formatted: dict, item_nominal_sources: dict) -> list[str]:
    formatted_to_nominal = {
        'event': 'mission',
        'fang & x': 'clinic',
        'fishing': 'fishing spots',
        'game center shop': 'game center',
        'gathering': 'gather',
        'guild_ranking': 'workshop ranking',
        'farming': 'planting',
        'kicking': 'kick',
        'logging': 'log',
        'monster': 'monsters',
        'ore_refining': 'ore refinery',
        'quarrying': 'quarry',
        'treasure': 'treasure chest',
        'salvaging': 'junk pile',
    }
    
    main_sources = {}
    for nominal_source in item_nominal_sources:
        nominal_source_description = nominal_source['description'].lower()

        for key, value in formatted.items():
            compare = formatted_to_nominal.get(key.lower(), key.lower())
            if compare == nominal_source_description:
                main_sources[key] = value
                continue

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        compare = formatted_to_nominal.get(item.lower(), item.lower())
                        if compare == nominal_source_description:
                            if main_sources.get(key):
                                main_sources[key].append(item)
                            else:
                                main_sources[key] = [item]
            
            if isinstance(value, dict):
                sub_main_sources = find_matches(item_id, value, item_nominal_sources)
                if sub_main_sources:
                    main_sources[key] = sub_main_sources
    
    return main_sources

def get_main_sources(item_id: int, formatted: dict, item_nominal_sources: dict) -> list[str]:
    main_sources = find_matches(item_id, formatted, item_nominal_sources)

    if not main_sources:
        if len(item_nominal_sources):
            print(f'No main sources for {item_id} {text.item(item_id)}')
        main_sources = formatted
    else:
        # Stores are important sources; I say we always treat them as main 
        # sources.
        if 'store' in formatted:
            main_sources['store'] = formatted['store']
    
    secondary_sources = sources_difference(formatted, main_sources)
    
    return (main_sources, secondary_sources)

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
        return text.scene(int(id_str))
    
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

def sources_difference(sources: dict, main_sources: dict) -> dict:
    result = {}
    
    for key, value in sources.items():
        if key not in main_sources:
            result[key] = value
        else:
            main_value = main_sources[key]
            if isinstance(value, set):
                diff = value - main_value
                if diff:
                    result[key] = diff
            elif isinstance(value, list):
                diff = [item for item in value if item not in main_value]
                if diff:
                    result[key] = diff
            elif isinstance(value, dict):
                diff = sources_difference(value, main_value)
                if diff:
                    result[key] = diff
    
    return result

if __name__ == '__main__':
    main()