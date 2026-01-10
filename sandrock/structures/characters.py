'''
Parses information regarding named characters, mostly dialog.
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.structures.conversation import *

# ------------------------------------------------------------------------------

social_levels = DesignerConfig.SocialLevel
social_level_map = {level['level']: {'count': 0, 'icon': 'star', 'name': text(level['nameId'])} for level in social_levels}

# ------------------------------------------------------------------------------

def read_bubble(npc_id: int, id: int, extra_args: list = []) -> str:
    bubble = Bubble(npc_id, id, extra_args)
    return bubble.read(True)

def read_conv_builder(id: int) -> None:
    builder = ConvBuilder(id)
    return builder.read()

def read_conv_segment(id: int) -> None:
    seg = ConvSegment(id, [])
    return seg.read()

def read_conv_talk(id: int) -> None:
    talk = ConvTalk(id, [])
    return talk.read()

# ------------------------------------------------------------------------------

class Character:

    def __init__(self, id: int) -> None:
        self.id:        int  = id
        self._npc_data: dict = DesignerConfig.Npc[id]

        self._actor_data:            dict = DesignerConfig.Actor[self._npc_data['templetID']]
        self._general_dialog_data: dict = self.set_general_dialog_data()
        self._pet_dialog_data:     dict = self.set_pet_dialog_data()

        self.set_primary_attributes()

    def set_primary_attributes(self) -> None:
        self.name:        str = text(self._npc_data['nameID'])
        self.description: str = text(self._npc_data['identityID'])

    def set_general_dialog_data(self) -> dict:
        general_dialog_data: dict = DesignerConfig.GeneralDialog

        for dialog_data in general_dialog_data:
            npc_id_min: int = dialog_data['id']['id0']
            npc_id_max: int = dialog_data['id']['id1']

            if npc_id_min <= self.id <= npc_id_max:
                return dialog_data
        
        return {}
    
    def set_pet_dialog_data(self) -> dict:
        pet_dialog_data: dict = DesignerConfig.PetNpcConfig

        for dialog_data in pet_dialog_data:
            npc_id: int = dialog_data['npcId']

            if npc_id == self.id:
                return dialog_data
        
        return {}

    def festival_dialog(self, festival_id: int) -> list[str]:
        if self._general_dialog_data == {}:
            return []
        
        all_festival_dialog = self._general_dialog_data['festival']
        festival_dialog = next(
            (dialog for dialog in all_festival_dialog if dialog['id'] == festival_id),
            None
        )

        if festival_dialog:
            return self.read_talk_data(festival_dialog['talkData']['talkData'])
        
        return []
    
    # If the player is followed by one or two pets.
    def pets_one_dialog(self) -> list[str]:
        if self._pet_dialog_data == {}:
            return []
        
        bubble_data: list = self._pet_dialog_data['bubbleOnes']
        bubble_texts: list[str] = []

        for bubble_id in bubble_data:
            bubble_texts += read_bubble(self.id, bubble_id)
        
        return bubble_texts
    
    # Reaction to a specific type of pet.
    def pet_special_dialog(self) -> list[str]:
        if self._pet_dialog_data == {}:
            return []
        
        special_bubbles: list = self._pet_dialog_data['bubbleSpecials']
        bubble_texts: list[str] = []

        for bubble_data in special_bubbles:
            pet_id: int = bubble_data['petId']
            bubbles: list = bubble_data['bubbles']
            pet_name: str = text.actor(pet_id)
            answer: str = f'answer = When player is followed by {{{{NPC2|{pet_name}}}}}:'

            for bubble_id in bubbles:
                bubble_texts += read_bubble(self.id, bubble_id, [answer])
        
        return bubble_texts

    # If the player is followed by three or more pets.  
    def pets_three_dialog(self) -> list[str]:
        if self._pet_dialog_data == {}:
            return []
        
        bubble_data: list = self._pet_dialog_data['bubbleThrees']
        bubble_texts: list[str] = []

        for bubble_id in bubble_data:
            bubble_texts += read_bubble(self.id, bubble_id)
        
        return bubble_texts
    
    # [{'relation': 0, 'dialogUnit': '1001*1;1002*1;1003*1'}, ...]
    def read_talk_data(self, talk_datas: list) -> None:
        include_relation_header = len(talk_datas) > 1
        lines = []

        for talk_data in talk_datas:
            if include_relation_header:
                relation = social_level_map[talk_data['relation']]
                lines.append(f'==={relation}===')

            for segment_id_str in talk_data['dialogUnit'].split(';'):
                segment_id = int(segment_id_str.split('*')[0])
                lines += read_conv_segment(segment_id)

        return lines

# ------------------------------------------------------------------------------

def load_characters() -> dict[int, Character]:
    characters = {id: Character(id) for id in DesignerConfig.Npc.keys()}
    # Sort by name.
    characters = dict(sorted(characters.items(), key=lambda item: item[1].name))

    return characters

characters = load_characters()