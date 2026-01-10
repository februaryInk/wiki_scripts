'''
Output missions that were cut from the game, but still have text entries.

80030964

Requires:
    - text
'''

from sandrock import *

mission_text_id_ranges = {
    'Mr Fitness': [80032364, 80032531], # Owen
    'Our Fleeting Youth': [80032661, 80032725], # Pablo
    'Ranch Family': [80032726, 80032881], # Elsie
    'Catori\'s Debts': [80015349, 80015393], # Catori
    'Walk in the Rain': [80031782, 80031869], # Arvio
    'The Butler': [80031870, 80032006], # Ernest
    'Andy\'s Machine': [80032007, 80032018], # Logan
    'Generations': [80032137, 80032256] # Heidi
}

def run() -> None:
    story_output_dir = config._root / 'out_story' / 'Unfinished Missions'
    story_output_dir.mkdir(exist_ok=True)

    for mission_name, (start_id, end_id) in mission_text_id_ranges.items():
        print(f'Processing mission: {mission_name}')

        mission_txt_content = []

        for text_id in range(start_id, end_id + 1):
            entry = text(text_id)

            if entry is None:
                continue

            mission_txt_content.append(entry)
            mission_txt_content.append('')

        mission_txt_path = story_output_dir / f'{mission_name}.txt'

        with open(mission_txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(mission_txt_content))

if __name__ == '__main__':
    run()
