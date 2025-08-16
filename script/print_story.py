'''
Print out every mission, event, and controller in the story asset bundle, along 
with a table of contents.
'''

from __future__   import annotations
from pathvalidate import sanitize_filename

from sandrock                  import *
from sandrock.structures.story import *

# ------------------------------------------------------------------------------

broken = [
    1200079, # Triggers mission that doesn't exist?
    1200174, # Conversation 1409 stuck in infinite loop.
    1200289, # Missing segment.
    1200378, # Conversation 5614 has too many talks.
    1200404, # Conversation 8237 has too few talks.
    1600329, # Conversation key error.
    1700171, # Conversation 1185 has too few talks.
    1700181, # Conversation is stuck in an infinite loop.
    1700386, # Missing segment.
    1800486, # Recursive parent-child relationship.
    1800487, # Recursive parent-child relationship.
    1800488, # Recursive parent-child relationship.
    1800489, # Recursive parent-child relationship.
    1800490, # Recursive parent-child relationship.
    1800491, # Recursive parent-child relationship.
    1800492, # Recursive parent-child relationship.
    1800493, # Recursive parent-child relationship.
    1800496, # Conversation 7887 has missing segment.
]

# ------------------------------------------------------------------------------

def run() -> None:
    mission_to_ids   = defaultdict(list)
    story            = Story()
    story_output_dir = config._root / 'out_story'

    processed_missions_count = 0
    total_missions_count     = len(story.missions)

    story_output_dir.mkdir(parents=True, exist_ok=True)

    # Clear the output directory.
    for file in story_output_dir.glob('*.txt'):
        file.unlink()

    for mission_id, mission in story.missions.items():
        if mission_id in broken: continue

        mission_name = mission.name or f'Unnamed Mission'
        mission_to_ids[mission.name].append(mission_id)

        print(f'Processing mission {mission_id}: {mission_name}')

        mission_output_dir = story_output_dir / sanitize_filename(mission.name)
        mission_output_dir.mkdir(parents=True, exist_ok=True)

        mission_txt_content = '\n'.join(mission.read())
        mission_txt_path = mission_output_dir / f'{mission_id}.txt'

        with open(mission_txt_path, 'w', encoding='utf-8') as f:
            f.write(mission_txt_content)
        
        processed_missions_count += 1
        percent_processed = (processed_missions_count / total_missions_count) * 100
        print(f'Processed {processed_missions_count}/{total_missions_count} missions ({percent_processed:.2f}%)')
    
    table_of_contents = []

    for mission_name, ids in sorted(mission_to_ids.items()):
        table_of_contents.append(f'== {mission_name} ==')

        for id in sorted(ids):
            table_of_contents.append(f'  * [[{id}]]')

        table_of_contents.append('')

    toc_txt_path = story_output_dir / 'table_of_contents.txt'

    with open(toc_txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(table_of_contents))

if __name__ == '__main__':
    run()
