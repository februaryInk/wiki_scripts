'''
Find all the sources we know of for all items.

In addtion to missing some items, we may be getting false positives. Some 
generators seem to be present but turned off, e.g., Pen's diamond ring drop.
And Logan drops rubber?

And why do some resources like Poplar Wood not get the expected source? Mining
and logging checks not working?

Also, what is AssetFixMissionItemFixMissionItem doing?

Account for BAG ADD ITEM REPLACE.

id: {
    id: ,
    name: ,
    nominal_source: ,
    primary_sources: ,
    secondary_sources:
}

Requires:
    - designer_config
    - resourcepoint
    - sceneinfo
    - scenes
    - season
    - text
'''

from sandrock                      import *
from sandrock.preproc              import get_mission_names
from sandrock.item_source_new.main import get_item_sources

# --------------------------------------------------------------------------------------

item_prototypes = DesignerConfig.ItemPrototype

def main() -> None:
    nominal_sources = get_nominal_sources()
    item_sources = get_item_sources()

    # print(json.dumps(item_sources, indent=2))

    

def get_nominal_sources():
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


if __name__ == '__main__':
    main()
