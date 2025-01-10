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
ConvChat: Speech bubbles.
    - npcId
    - bubbleId (text id for bubble content)
InMissionTalk: Dialogue that select NPCs respond with while a mission is active.
    - missionId
    - npcIds
    - dialog (ConvSegment id)
'''

from __future__ import annotations

from sandrock import *

# -- Private -------------------------------------------------------------------

_indents = [
    'none',
    'true',
    'double',
    '3',
    '4',
    '5'
]

_substitutions = {
    '<color=#00ff78>': '{{textcolor|green|',
    '<color=#3aa964>': '{{textcolor|green|',
    '</color>': '}}',
    '[ChildCallPlayer]': '\'\'Parent Name\'\'',
    '[MarriageCall|Name]': '\'\'Pet Name\'\'',
    '[NpcName|8121]': '\'\'Child 1\'\'',
    '[NpcName|8122]': '\'\'Child 2\'\'',
    '[Player|Name]': '\'\'Player\'\''
}

_conv_chats    = DesignerConfig.ConvChat
_conv_segments = DesignerConfig.ConvSegement
_conv_talks    = DesignerConfig.ConvTalk

def _substitute(text):
    pattern = re.compile('|'.join(re.escape(key) for key in _substitutions.keys()))
    return pattern.sub(lambda match: _substitutions[match.group(0)], text)
class _ConvOption:
    def __init__(self, content_id, talk_id, parent_stack: list[Any] = []):
        self._content_id   = content_id
        self._talk_id      = talk_id
        self._parent_stack = parent_stack
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
    @property
    def content(self) -> str:
        return _substitute(text.text(self._content_id))
    
    @property
    def response_talk(self) -> ConvTalk:
        if self._talk_id == -1: return None
        return ConvTalk(self._talk_id, self._parent_stack + [self])
    
    @property
    def line(self) -> list[str]:
        indent = self._indent_count * ':'
        return f'{indent}*\'\'{_substitute(self.content)}\'\''
    
    def read_response_talk(self) -> list[str]:
        if self.response_talk:
            return self.response_talk.read()
        else:
            return []

# ------------------------------------------------------------------------------

class ConvChat:
    def __init__(self, id: int):
        self.id    = id
        self._data = _conv_chats[id]
    
    @property
    def content(self) -> str:
        return text.text(self._data['bubbleId'])

class ConvSegment:
    def __init__(self, id, parent_stack: list[Any] = []):
        self._id = id
        self._data = _conv_segments[id]
        self._parent_stack = parent_stack
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
    @property
    def _line(self) -> str:
        args = ['dialogue', self.speaker_name]
        if self._indent_count:
            args.append(f'indent={_indents[self._indent_count]}')
        if self.parent and self.parent.is_branch and self._id == self.parent.segment_ids[0]:
            args.append(f'answer={self.parent.parent.content}\n')
        args.append(self.content)
        return '{{' + '|'.join(args) + '}}'
    
    @property
    def content(self) -> str:
        text_id = int(self._data['content'].split('|', 1)[0])
        return _substitute(text.text(text_id))
    
    @property
    def speaker_name(self) -> str:
        speaker_id = int(self._data['speakerId'])
        return text.npc(speaker_id)
    
    @property
    def parent(self) -> ConvTalk:
        if len(self._parent_stack) == 0: return None
        return self._parent_stack[-1]
    
    @property
    def conv_option_content_ids(self) -> list[int]:
        split_content = self._data['content'].split('|', 1)
        if len(split_content) > 1:
            return [int(id) for id in split_content[1].split(',')]
        else:
            return []
    
    @property
    def conv_options(self) -> list[_ConvOption]:
        if not len(self.conv_option_content_ids):
            return []
        
        if self.parent:
            assert isinstance(self.parent, ConvTalk)
            assert self._id == self.parent.segment_ids[-1]

        if self.parent:
            talk_ids = self.parent.next_talk_ids
        else:
            talk_ids = [-1] * len(self.conv_option_content_ids)
        
        assert len(talk_ids) == len(self.conv_option_content_ids)
        return [_ConvOption(content_id, talk_id, self._parent_stack + [self]) for content_id, talk_id in zip(self.conv_option_content_ids, talk_ids)]
    
    def read(self) -> list[str]:
        lines = [self._line]
        if self.conv_options:
            lines.append('')
            for option in self.conv_options:
                line = option.line
                response = option.response_talk

                if not response:
                    line += ' (No unique dialogue)'
                lines.append(line)
            
            lines.append('')
            for option in self.conv_options:
                lines += option.read_response_talk()
        
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.read()))

class ConvTalk:
    def __init__(self, id, parent_stack: list[Any] = []):
        self._data = _conv_talks[id]
        self._parent_stack = parent_stack
    
    @property
    def is_branch(self) -> bool:
        return self.parent and isinstance(self.parent, _ConvOption)
    
    @property
    def next_talk_ids(self) -> list[int]:
        return self._data['nextTalkId']
    
    @property
    def parent(self) -> ConvTalk:
        if len(self._parent_stack) == 0: return None
        return self._parent_stack[-1]

    @property
    def segment_ids(self) -> list[int]:
        return self._data['segmentIdList']
    
    @property
    def segments(self) -> list[ConvSegment]:
        return [ConvSegment(id, self._parent_stack + [self]) for id in self.segment_ids]
    
    def read(self) -> list[str]:
        lines = []
        for segment in self.segments:
            lines += segment.read()
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.read()))
