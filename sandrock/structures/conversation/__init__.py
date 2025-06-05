'''
Classes that piece together conversations that occur in the game.

Notable asset bundles:
ConvSequence: Character behavior that occurs before (maybe?) a conversation 
segment. Look here, walk there, emote. Not utilized here.
ConvTalk: Series of dialogue segments that are delivered together. May end in a 
player dialogue choice that leads to a "next talk".
TODO: Is there ever a "next talk" in the absence of a dialogue choice?
    - segmentIdList
    - nextTalkId
ConvSegement: Indivdual dialogue lines and delivery.
    - content (text id)
    - speakerId
    - sequenceId
ConvChat: Speech bubbles. NOT in-mission bubbles.
    - npcId
    - bubbleId (text id for bubble content)
EventBubbles: Series of speech bubbles for event speeches.
    - ids (ConvChat id)
EventTalk: !!! Special dialogues NPCs have after some occurrence.
InMissionTalk: Dialogue that select NPCs respond with while a mission is active.
    - missionId
    - npcIds
    - dialog (ConvSegment id)
'''

from __future__ import annotations

from sandrock                                      import *
from sandrock.structures.conversation.conv_builder import *
from sandrock.structures.conversation.conv_elements import *

# -- Private -------------------------------------------------------------------

_conv_chats    = DesignerConfig.ConvChat
_event_bubbles = DesignerConfig.EventBubbles
_event_talks   = DesignerConfig.EventTalk

# ------------------------------------------------------------------------------

class Bubble:
    def __init__(self, speaker_id: int, text_id: int):
        self._speaker_id: int = speaker_id
        self._text_id: int = text_id
    
    @property
    def _line(self) -> str:
        args = ['dialogue', self.speaker_name, self.content]
        return '{{' + '|'.join(args) + '}}'
    
    @property
    def content(self) -> str:
        return text(self._text_id)
    
    @property
    def speaker_name(self) -> str:
        return text.npc(self._speaker_id)

    def read(self) -> list[str]:
        return [
            'In a speech bubble:'
            '',
            self._line
        ]

class ConvChat:
    def __init__(self, id: int):
        self.id: int         = id
        self._data: dict     = _conv_chats[id]
        self._bubble: Bubble = Bubble(self.speaker_id, self.text_id)

    @property
    def speaker_id(self) -> int:
        return self._data['npcId']
    
    @property
    def text_id(self) -> int:
        bubble_ids = self._data['bubbleId']
        assert len(bubble_ids) == 1
        return bubble_ids[0]
    
    def read(self) -> list[str]:
        return self._bubble.read()

class EventBubble:
    def __init__(self, npc_id: int, tag: str):
        self.npc_id: int     = npc_id
        self.tag: str        = tag
        # Event bubbles don't have unique IDs, though the combination of
        # npc_id and tag should be unique.
        self._data: dict = next(
            data for data in _event_bubbles
            if data['tag'] == tag and data['id'] == npc_id
        )
    
    @cached_property
    def bubbles(self) -> list[Bubble]:
        return [Bubble(self.npc_id, text_id) for text_id in self.text_ids]
    
    @property
    def text_ids(self) -> int:
        return self._data['ids']
    
    def print(self) -> None:
        print('\n'.join(self.read()))
    
    def read(self) -> list[str]:
        lines = [f'Event bubble for {text.npc(self.npc_id)} with tag "{self.tag}":']
        for bubble in self.bubbles:
            lines += bubble.read()
        return lines

class EventTalk:
    @classmethod
    def accomplished_mission_talks(cls, mission_id: int) -> list[EventTalk]:
        talks = []

        for talk_id, data in _event_talks.items():
            if data['accomplishedMission'] == str(mission_id):
                talks.append(cls(talk_id))
        
        return sorted(talks, key=lambda talk: talk.npc)
    
    @classmethod
    def failed_mission_talks(cls, mission_id: int) -> list[EventTalk]:
        talks = []

        for talk_id, data in _event_talks.items():
            if data['failedMission'] == str(mission_id):
                talks.append(cls(talk_id))
        
        return sorted(talks, key=lambda talk: talk.npc)
    
    @classmethod
    def global_str_talks(cls, str: str) -> list[EventTalk]:
        talks = []

        for talk_id, data in _event_talks.items():
            if data['globalStr'] == str:
                talks.append(cls(talk_id))
        
        return sorted(talks, key=lambda talk: talk.npc)

    def __init__(self, id: int):
        self.id: int = id
        self._data: dict = _event_talks[id]

    @property
    def npc(self) -> str:
        return text.npc(self.npc_id)

    @property
    def npc_id(self) -> int:
        return self._data['npcId']
    
    @property
    def conv_segments(self) -> list[ConvSegment]:
        return [ConvSegment(id) for id in self.conv_segment_ids]
    
    @property
    def conv_segment_ids(self) -> list[int]:
        return [int(id) for id in self._data['dialog'].split(',')]
    
    def read(self) -> list[str]:
        lines = []
        for seg in self.conv_segments:
            lines += seg.read()
        return lines
