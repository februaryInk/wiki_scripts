'''
Print out story and cutscene photos in a format suitable for wiki.
'''

from __future__ import annotations

from sandrock                  import *
from sandrock.lib.text         import load_text
from sandrock.structures.story import *

# ------------------------------------------------------------------------------

class _Photo:

    def __init__(self, data: dict) -> None:
        self.data = data
        self.id = data['id']
    
    def lines(self) -> list[str]:
        return [
            '{{AlbumPhoto',
            f'|id = {self.id}',
            f'|image = {self.image_file}',
            f'|title = {self.name}',
            f'|from = {self.photo_from}',
            f'|description = {self.caption}',
            '}}'
        ]

# ------------------------------------------------------------------------------

class _EventPhoto(_Photo):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        
        description = text(self.data['descriptionId']).split(' - ', 1)
        if len(description) != 2: description = ['', description[0]]
        self.name, self.caption = description
        self.mission = DesignerConfig.Story.get_mission(self.data['missionId'])
        self.is_event = self.mission.is_event if self.mission else False
        self.is_main = self.mission.is_main if self.mission else False

    @cached_property
    def photo_from(self) -> str:
        if self.mission:
            if self.mission.name:
                return f'{{{{e|{self.mission.name}}}}}' if self.is_event else f'{{{{m|{self.mission.name}}}}}'
            else:
                return 'Unknown'
        else:
            return 'Unknown'

# ------------------------------------------------------------------------------

class _StoryPhoto(_Photo):
    wiki_info = {
        1: {'title': 'Weapon Rack', 'from': "{{m|Where's Mi-an}}", 'file': 'Weapon Rack (photo)'},
        2: {'title': 'Drawing on the Wall', 'from': "{{m|Where's Mi-an}}", 'file': 'Drawing on the Wall (photo)'},
        3: {'title': "Haru's Worktable", 'from': "{{m|Where's Mi-an}}", 'file': "Haru's Worktable (photo)"},
        4: {'title': 'Marked Map', 'from': "{{m|Where's Mi-an}}", 'file': 'Marked Map (photo)'},
        5: {'title': "Logan's Book", 'from': "{{m|Where's Mi-an}}", 'file': "Logan's Book (photo)"},
        6: {'title': 'Wedding Photo', 'from': "{{m|Where's Mi-an}}", 'file': 'Wedding Photo (photo)'},
        7: {'title': 'Desk of Inventions', 'from': "{{m|Where's Mi-an}}", 'file': 'Desk of Inventions (photo)'},
        8: {'title': 'Lucien Castle Photo', 'from': '{{m|Old Familiar Face}}', 'file': 'Lucien Castle Photo (photo)'},
        9: {'title': 'Picture of Lucien', 'from': '{{m|Old Familiar Face}}', 'file': 'Picture of Lucien (photo)'},
        10: {'title': 'Once in a Blue Moon', 'from': '{{m|Once in a Blue Moon}}', 'file': 'Once in a Blue Moon'},
        11: {'title': 'Photo of a tree', 'from': "Nia's [[Reply|letters]].", 'file': 'Photo of a tree'},
        12: {'title': 'Photo of Nia', 'from': "Nia's [[Reply|letters]].", 'file': 'Photo of young Nia'},
        13: {'title': 'Train Station', 'from': 'Taken by the player during {{m|Public Image}}.', 'file': 'Public Image Train Station'},
        14: {'title': 'Bumble Ant', 'from': 'Taken by the player during {{m|Public Image}}.', 'file': 'Public Image Bumble Ant'},
        15: {'title': 'Water Tower', 'from': 'Taken by the player during {{m|Public Image}}.', 'file': 'Public Image Water Tower'},
        16: {'title': "Burgess's Shop", 'from': 'Taken by the player during {{m|Public Image}}.', 'file': 'Public Image Water World'},
        17: {'title': 'Photo of Mort and Martle', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of Mort and Martle full'},
        18: {'title': 'Photo of the Straw Grid', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of the Straw Grid full'},
        19: {'title': 'Photo of Mort and Zeke', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of Mort and Zeke full'},
        20: {'title': 'Photo of the Old Water Tower', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of the Old Water Tower full'},
        21: {'title': 'Photo of Old Sandrock', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of Old Sandrock full'},
        22: {'title': 'Photo of the Old Blue Moon', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Photo of the Old Blue Moon full'},
        23: {'title': 'Picture of Nia', 'from': 'Sent by Nia before {{m|The Childhood Friend}}.', 'file': 'Picture of Nia'},
        24: {'title': 'Nia in Sandrock', 'from': 'Taken by the player at the start of {{m|Farmin\' Moisture}}.', 'file': 'Nia in Sandrock'},
        25: {'title': 'Photo for the Time Capsule', 'from': '{{m|Mysterious Box}}', 'file': 'Time Capsule'},
        26: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 1'},
        27: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 2'},
        28: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 3'},
        29: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 4'},
        30: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 5'},
        31: {'title': 'Road to Portia', 'from': 'Received at the start of {{m|Rock Out}}.', 'file': 'Road to Portia presentation 6'},
        32: {'title': 'Howlett in quarantine', 'from': '{{m|The Goat}}.', 'file': 'Howlett in quarantine'},
        33: {'title': 'Bombing the temple', 'from': '{{m|The Goat}}.', 'file': 'Bombing the temple'},
        34: {'title': 'Relic weapon', 'from': '{{m|The Goat}}.', 'file': 'Relic weapon'},
        35: {'title': 'Wanted posters in town', 'from': '{{m|The Goat}}.', 'file': 'Wanted posters in town'},
        36: {'title': 'Howlett in coma', 'from': '{{m|The Goat}}.', 'file': 'Howlett in coma'},
        37: {'title': 'Logan finds Andy', 'from': '{{m|The Goat}}.', 'file': 'Logan finds Andy'},
        38: {'title': 'Andy playground', 'from': 'Optional conversation during {{m|The Goat}}.', 'file': 'Andy playground'},
        39: {'title': 'Grace the spy', 'from': '{{m|The Goat}}.', 'file': 'Grace the spy'},
        40: {'title': 'Howlett hunting monsters', 'from': 'Optional conversation during {{m|The Goat}}.', 'file': 'Howlett hunting monsters'},
        41: {'title': 'Bad news', 'from': '{{m|The Goat}}.', 'file': 'Bad news'},
        42: {'title': 'Locking mechanism', 'from': '{{m|The Goat}}.', 'file': 'Locking mechanism'},
        43: {'title': 'Blueprint of the Sandrock Storage', 'from': '{{m|The Goat}}.', 'file': 'Blueprint of the Sandrock Storage'},
        44: {'title': 'Lumi warning Logan', 'from': '{{m|The Goat}}.', 'file': 'Lumi warning Logan'},
        45: {'title': 'Superstars', 'from': '{{e|Luna\'s Invitation}}.', 'file': 'Superstars'},
        46: {'title': 'Happy birthday Alo', 'from': '{{m|The Stars Align}}.', 'file': 'The Stars Align'},
        47: {'title': 'The Before Times', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'The Before Times'},
        48: {'title': 'Minister Zeke', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Minister Zeke'},
        49: {'title': 'Last photo of Martle', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Last photo of Martle'},
        50: {'title': 'Wedding at the Tree', 'from': 'Randomly found after completing {{m|Gone with the Wind}}.', 'file': 'Wedding at the Tree'},
        52: {'title': 'Fun in the Sun', 'from': 'Sent by [[Ginger]] after {{m|Sunrise}}.', 'file': 'Fun in the Sun'},
        53: {'title': 'Family photo - Young Arvio and Amirah', 'from': "[[Amirah/Dialogue#Engagement_letter|Amirah]] or [[Arvio/Dialogue#Engagement_letter|Arvio's]] engagement letter", 'file': 'Family photo - Young Arvio and Amirah'},
        54: {'title': 'Catori and son', 'from': "[[Catori/Dialogue#Engagement_letter|Catori's engagement letter]]", 'file': 'Catori and son'},
        55: {'title': 'Ranch Family photo - Baby Elsie', 'from': "[[Elsie/Dialogue#Engagement_letter|Elsie's engagement letter]]", 'file': 'Ranch Family photo - Baby Elsie'},
        56: {'title': 'Ranch Family photo - Young Elsie', 'from': "[[Elsie/Dialogue#Engagement_letter|Elsie's engagement letter]]", 'file': 'Ranch Family photo - Young Elsie'},
        57: {'title': 'Young Mabel and Cooper', 'from': "[[Elsie/Dialogue#Engagement_letter|Elsie's engagement letter]]", 'file': 'Young Mabel and Cooper'},
        58: {'title': 'Family photo - Young Heidi', 'from': "[[Heidi/Dialogue#Engagement_letter|Heidi's engagement letter]]", 'file': 'Family photo - Young Heidi'},
        59: {'title': "Heidi's parents wedding", 'from': "[[Heidi/Dialogue#Engagement_letter|Heidi's engagement letter]]", 'file': "Heidi's parents wedding"},
        60: {'title': "Heidi's mother", 'from': "[[Heidi/Dialogue#Engagement_letter|Heidi's engagement letter]]", 'file': "Heidi's mother"},
        61: {'title': 'Blue Moon family photo', 'from': "[[Owen/Dialogue#Engagement_letter|Owen's engagement letter]]", 'file': 'Blue Moon family photo'},
        62: {'title': 'Family photo - Young Owen', 'from': "[[Owen/Dialogue#Engagement_letter|Owen's engagement letter]]", 'file': 'Family photo - Young Owen'},
        63: {'title': 'Family photo - Young Qi', 'from': "[[Qi/Dialogue#Engagement_letter|Qi's engagement letter]]", 'file': 'Family photo - Young Qi'},
        64: {'title': 'Qi and his parents', 'from': "[[Qi/Dialogue#Engagement_letter|Qi's engagement letter]]", 'file': 'Qi and his parents'},
        65: {'title': "Logan's parents wedding", 'from': "[[Logan/Dialogue#Engagement_letter|Logan's engagement letter]]", 'file': "Logan's parents wedding"},
        66: {'title': 'Howlett and his wife', 'from': "[[Logan/Dialogue#Engagement_letter|Logan's engagement letter]]", 'file': 'Howlett and his wife'},
        67: {'title': 'Young Logan', 'from': "[[Logan/Dialogue#Engagement_letter|Logan's engagement letter]]", 'file': 'Young Logan'},
        68: {'title': "Fang's fifth birthday", 'from': "[[Fang/Dialogue#Engagement_letter|Fang's engagement letter]]", 'file': "Fang's fifth birthday"},
        69: {'title': "Tallsky Marriage Certificate Photo", 'from': "{{m|In the Family Now}}", 'file': "Tallsky Marriage Certificate Photo"},
        70: {'title': "The Apple", 'from': "{{m|The Apple}}", 'file': "The Apple"},
        71: {'title': "Garden School Blues", 'from': "{{m|Garden School Blues}}", 'file': "Garden School Blues"},
        72: {'title': "To be a Builder", 'from': "{{m|To be a Builder}}", 'file': "To be a Builder"},
        73: {'title': "So-Called \"Rebellion\"", 'from': "{{m|So-Called \"Rebellion\"}}", 'file': "So-Called Rebellion"},
        74: {'title': "X's Show", 'from': "{{m|X's Show}}", 'file': "X's Show"},
        75: {'title': "The Getaway", 'from': "{{m|The Getaway}}", 'file': "The Getaway"},
        76: {'title': "Hot Cocoa", 'from': "{{m|Hot Cocoa}}", 'file': "Hot Cocoa"},
        77: {'title': "Father and Son", 'from': "{{m|Father and Son}}", 'file': "Father and Son"},
        78: {'title': "Yimi Park", 'from': "After {{m|Late Bloomer}}", 'file': "Yimi Park"},
        
    }

    def __init__(self, data: dict) -> None:
        super().__init__(data)
        
        self.caption = text(self.data['descriptionId'])
        self.photo_from = self.wiki_info[self.id]['from'] if self.id in self.wiki_info else 'Unknown'
        self.image_file = f'{self.wiki_info[self.id]["file"]}.png' if self.id in self.wiki_info else f'{self.id} photo.png'
        self.name = self.wiki_info[self.id]['title'] if self.id in self.wiki_info else 'Unknown'
        self.order = self.data['order']

# ------------------------------------------------------------------------------

def run() -> None:
    print_story_photos()

def print_cutscene_photos() -> None:
    cutscene_photos = DesignerConfig.CutscenePhotos

    story = Story()

    linkable_words = []
    for id, npc in DesignerConfig.Npc.items():
        linkable_words.append(text(npc['nameID']))
    linkable_words = list(set(linkable_words))

    main_mission_lines = ['===Main Missions===', '{{FlexContainer|']
    side_mission_lines = ['===Side Missions===', '{{FlexContainer|']

    for id, photo in cutscene_photos.items():
        description = text(photo['descriptionId']).split(' - ', 1)
        if len(description) != 2: description = ['', description[0]]
        name, caption = description
        mission = story.get_mission(photo['missionId'])

        for word in linkable_words:
            if word in caption:
                caption = caption.replace(word, f'[[{word}]]')

        if mission:
            if mission.name:
                image_name = mission.name
            else:
                image_name = f'{name} cutscene.png'
            
            if mission.is_event:
                photo_from = f'{{{{e|{mission.name}}}}}'
            else:
                photo_from = f'{{{{m|{mission.name}}}}}'
        else:
            image_name = f'{name} cutscene.png'
            'Unknown'

        photo_lines = [
            '{{CutscenePhoto',
            f'|id = {id}',
            f'|image = {name}.png',
            f'|title = {name}',
            f'|from = {photo_from}',
            f'|description = {caption}',
            '}}'
        ]

        if mission and mission.is_main:
            main_mission_lines += photo_lines
            main_mission_lines.append('')
        else:
            side_mission_lines += photo_lines
            side_mission_lines.append('')
    
    main_mission_lines.append('}}')
    side_mission_lines.append('}}')
    lines = main_mission_lines
    print('\n'.join(lines))

def print_refine_type() -> None:
    refines = DesignerConfig.Refine

    for id, refine in refines.items():
        if refine['refineType'] == -1:
            print(f'{refine["refineType"]}: {text.item(id)}')
    
    for id, refine in refines.items():
        if refine['refineType'] == 0:
            print(f'{refine["refineType"]}: {text.item(id)}')
    
    equipment = DesignerConfig.Equipment
    for id, equip in equipment.items():
        print(f'{id}: {text.item(id)}')

def print_story_photos() -> None:
    story_photos = DesignerConfig.PrestorePhotos
    sorted_photos = sorted(story_photos.items(), key=lambda x: x[1]['order'])

    lines = ['{{FlexContainer|']

    for id, photo in story_photos.items():
        print(f'{id}: {photo['order']}')
        photo = _StoryPhoto(photo)
        lines += photo.lines()
        lines.append('')

    lines.append('}}')
    print('\n'.join(lines))

if __name__ == '__main__':
    run()
