'''
Find all the sources we know of for all items.

id: {
    id: ,
    name: ,
    nominal_source: ,
    recipe_sources: ,
    all_sources:
}

Requires:
    - designer_config
    - resourcepoint
    - sceneinfo
    - scenes
    - season
    - text
'''

from sandrock                        import *
from sandrock.lib.designer_config    import DesignerConfig
from sandrock.lib.text               import text
from sandrock.structures.story       import Story

from sandrock.item_source_new.main   import get_item_sources
from sandrock.item_source_new.common import *

# ------------------------------------------------------------------------------

item_prototypes = DesignerConfig.ItemPrototype
scene_name_to_id = sceneinfo.get_scene_system_name_to_id()
story = Story()

_manual_additions = {
}

_manual_removals = {
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

    # Cyfuls strikes: Grace
    # The Protector: Pen's Last Words
    # Portian war drum, all NPCs
    # Magnesese ore, shipwreck ruins
    # Recipe sources
    #   - Cooking experiment
    #   - Research center
    #   - Machine unlocks

    results = format_results(item_sources, nominal_sources)
    results = dict(sorted(results.items()))
    write_lua(config.output_dir / 'lua/AssetItemSource.lua', results)

# -- Preparing Results ---------------------------------------------------------

def format_results(item_sources: dict[int, list[ItemSource]], nominal_sources: dict[int, dict]) -> dict[int, dict]:
    results = {}
    for item_id, sources in item_sources.items():
        formatted = format_sources(sources, item_id)
        results[item_id] = {
            'id':              item_id,
            'name':            text.item(item_id),
            'nominal_source':  nominal_sources[item_id],
            'primary_sources': [],
            'all_sources':     formatted
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
        'developer',
        'farming',
        'fishing',
        'guild_ranking',
        'kicking',
        'logging',
        'museum',
        'party_food_package',
        'pet_dispatch',
        'quarrying',
        'recycling',
        'salvaging',
        'sand_racing',
        'sand_sledding'
    ]

    # print(source)

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
                case 'wedding':
                    add_or_append(formatted, 'npc', [npc, 'Wedding Gift'])
                case 'spouse_gift' | 'spouse_gift_expecting':
                    if all_spouses_in_source(sources, event):
                        npc = 'All Spouses'
                    else:
                        npc = get_name(source[2])
                    add_or_append(formatted, 'npc', [npc, 'Spouse Gift'])
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
            raise ValueError(f'Bad item source {source}')

    
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

spouses = [(npc['id'], npc['nameID'], text.npc(npc['id'])) for npc in DesignerConfig.Npc if npc['canLove'] == 1]
def all_spouses_in_source(sources: list[ItemSource], event: str) -> bool:
    event_sources = [source for source in sources if source[0] == 'npc' and source[1] == event]
    if len(event_sources) == len(spouses):
        return True

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