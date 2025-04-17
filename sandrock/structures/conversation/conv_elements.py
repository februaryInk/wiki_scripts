'''

'''

from __future__ import annotations

from sandrock import *

if TYPE_CHECKING:
    from sandrock.structures.conversation.conv_builder import ConvBuilder

# -- Private -------------------------------------------------------------------

_indents = [
    'none',
    'true',
    'double',
    '3',
    '4',
    '5'
]

_conv_segments = DesignerConfig.ConvSegement
_conv_talks    = DesignerConfig.ConvTalk

# ------------------------------------------------------------------------------

type ConvPath = list[ConvBuilder | ConvOption | ConvSegment | ConvTalk]

# ------------------------------------------------------------------------------

# TODO: If nextTalk is in the parent stack, print that the conversation repeats
# for the given option. Otherwise, will we loop infinitely?
class ConvOption:
    def __init__(self, content_id, talk_id, choice_type, index, parent_stack: list[Any] = []):
        self.index: int         = index
        self._choice_type: int  = choice_type
        self._content_id        = content_id
        self._talk_id           = talk_id
        self._parent_stack      = parent_stack
        self.id: str            = f'{self.parent.id}_{index}'

        self.parse()
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, ConvOption))
    
    @property
    def choice_type(self) -> str:
        type_map = {
            -1: None,
            4: 'flirt'
        }
        
        return type_map[self._choice_type]
    
    @property
    def first_parent(self) -> ConvBuilder | ConvTalk:
        return self._parent_stack[0]

    @property
    def identifier(self) -> str:
        return f'Option|{self.id}'
    
    @property
    def is_builder(self) -> bool:
        return False
    
    @property
    def is_independently_terminal(self) -> bool:
        return self._talk_id == -1 and not self.parent.is_terminal
    
    @property
    def is_talk(self) -> bool:
        return False
    
    @property
    def line(self) -> list[str]:
        indent = self._indent_count * ':'
        type = '{{flirt}}' if self.choice_type == 'flirt' else ''
        return f'{indent}*{type}\'\'{self.content}\'\''
    
    @property
    def parent(self) -> ConvSegment:
        parent = self._parent_stack[-1]
        return parent
    
    def get_response_talk(self) -> ConvTalk:
        if self._talk_id == -1: return None
        return ConvTalk(self._talk_id, self._parent_stack + [self])
    
    def parse(self) -> None:
        self.content       = text.text(self._content_id)
        self.response_talk = self.get_response_talk()

        if self.is_independently_terminal:
            self.return_stack()

    def read_response_talk(self) -> list[str]:
        if not self.response_talk: return []
        return self.response_talk.read()
    
    def read_response_talk_up_to(self, identifier: str, parent_talks: list[ConvTalk]) -> list[str]:
        if self.response_talk:
            return self.response_talk.read_up_to(identifier, parent_talks)
        else:
            return []

    def return_stack(self):
        if len(self._parent_stack) and self.first_parent.is_builder:
            builder = self.first_parent
            builder.add_stack(self._parent_stack + [self])

# ------------------------------------------------------------------------------

class ConvSegment:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int       = id
        self._data: dict   = _conv_segments[id]
        self._parent_stack = parent_stack

        self.parse()
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, ConvOption))
    
    @property
    def _line(self) -> str:
        args = ['dialogue', self.speaker_name]

        if self._indent_count:
            args.append(f'indent={_indents[self._indent_count]}')
        
        if self.option_parent:
            args.append(f'answer={self.option_parent.content}\n')
        
        if self._modifiers:
            for modifier in self._modifiers:
                type, id, value = modifier
                if type == 'npc_favor':
                    # reward={{NPC2|Owen|rp=2}}
                    args.append(f'reward={{{{NPC2|{text.npc(id)}|rp={value}}}}}')
                elif type == 'item':
                    # reward={{i2|Yakboy Geometric Carpet|1}}
                    args.append(f'reward={{{{i2|{text.item(id)}|{value}}}}}')
        
        args.append(self.content)

        return '{{' + '|'.join(args) + '}}'
    
    @property
    def _modifiers(self) -> set[tuple]:
        if self.conv_builder is None: return set()

        native_modifiers = self.conv_builder.segment_modifiers.get(str(self.id), set())

        if self.option_parent:
            option_modifiers = self.conv_builder.option_modifiers.get(self.option_parent.id, set())
            
            return native_modifiers.union(option_modifiers)
        
        return native_modifiers
    
    @property
    def content(self) -> str:
        text_id = int(self._data['content'].split('|', 1)[0])
        return text.text(text_id)
    
    @property
    def first_parent(self) -> ConvBuilder | ConvTalk:
        return self._parent_stack[0]
    
    @property
    def identifier(self) -> str:
        if len(self.conv_option_content_ids):
            return f'ChoiceSegment|{self.id}'
        if self.is_terminal:
            return f'TerminalSegment|{self.id}'
        
        return f'Segment|{self.id}'
    
    @property
    def is_builder(self) -> bool:
        return False
    
    @property
    def is_last_in_talk(self) -> bool:
        if self.talk_parent:
            return self.id == self.talk_parent.segment_ids[-1]
        return False
    
    @property
    def is_talk(self) -> bool:
        return False
    
    @property
    def is_terminal(self) -> str:
        if self.talk_parent:
            talk_ids = self.talk_parent.next_talk_ids
            
            if self.is_last_in_talk and not any(x != -1 for x in talk_ids):
                return True
        
        return False
    
    @property
    def speaker_name(self) -> str:
        speaker_id = int(self._data['speakerId'])
        if speaker_id == -1:
            return ''
        else:
            return text.npc(speaker_id)
    
    @property
    def conv_builder(self) -> ConvBuilder:
        if len(self._parent_stack) and self.first_parent.is_builder:
            return self._parent_stack[0]
    
    @property
    def talk_parent(self) -> ConvTalk:
        for item in reversed(self._parent_stack):
            if item.is_talk:
                return item
    
    @property
    def option_parent(self) -> ConvOption:
        # There will be a talk between the segment and the option.
        if self.talk_parent and self.talk_parent.is_branch and self.id == self.talk_parent.segment_ids[0]:
            return self.talk_parent.parent
    
    @property
    def conv_option_content_ids(self) -> list[int]:
        split_content = self._data['content'].split('|', 1)
        if len(split_content) > 1:
            return [int(id) for id in split_content[1].split(',')]
        else:
            return []
    
    @property
    def choice_types(self) -> list[str]:
        choice_type = self._data['choiceType']
        if choice_type:
            return [int(type) for type in choice_type.split(',')]
        else:
            return [-1] * len(self.conv_option_content_ids)
    
    def get_conv_options(self) -> list[ConvOption]:
        if not len(self.conv_option_content_ids): return []
        
        # If there is a dialogue choice with no effect on the conversation,
        # it doesn't need to be the last segment in the talk. However, the
        # parent's next talk ids are only for the last segment.
        if self.talk_parent and self.is_last_in_talk:
            print(f'{self.id} is the last segment in parent talk')
            
            talk_ids = []
            stack_talk_ids = [item.id for item in self._parent_stack if isinstance(item, ConvTalk)]
            
            next_talk_ids = self.talk_parent.next_talk_ids

            for talk_id in next_talk_ids:
                if talk_id not in stack_talk_ids:
                    talk_ids.append(talk_id)
                else:
                    not_in_stack = [id for id in next_talk_ids if id not in stack_talk_ids]
                    # assert len(not_in_stack) == 1, f'Found {not_in_stack} not in stack {stack_talk_ids}'
                    talk_ids.append(not_in_stack[0])
        else:
            talk_ids = [-1] * len(self.conv_option_content_ids)
        
        assert len(talk_ids) == len(self.conv_option_content_ids), f'talks {talk_ids} not compatible with content {self.conv_option_content_ids} in segment {self.id}'

        choices = zip(self.conv_option_content_ids, talk_ids, self.choice_types)
        
        return [
            ConvOption(content_id, talk_id, choice_type, index, self._parent_stack + [self]) 
            for index, (content_id, talk_id, choice_type) in enumerate(choices)
        ]
    
    def get_next_talk(self) -> ConvTalk:
        if self.is_last_in_talk and not len(self.conv_option_content_ids):
            assert len(self.talk_parent.next_talk_ids) == 1
            
            next_talk_id = self.talk_parent.next_talk_ids[0]
            
            if next_talk_id != -1:
                return ConvTalk(next_talk_id, self._parent_stack)
        
        return None
    
    def parse(self) -> None:
        self.conv_options = self.get_conv_options()
        self.next_talk    = self.get_next_talk()

        if self.is_terminal:
            # assert not self.conv_options
            assert not self.next_talk
            self.return_stack()
    
    def read_up_to(self, identifier: str, parent_talks: list[ConvTalk]) -> list[str]:
        if self.identifier == identifier:
            return []
        
        lines = [self._line]
        if self.conv_options:
            assert not self.next_talk

            lines.append('')
            for option in self.conv_options:
                line = option.line
                response = option.response_talk

                if not response:
                    line += ' (No unique dialogue)'
                lines.append(line)
            
            lines.append('')
            for option in self.conv_options:
                lines += option.read_response_talk_up_to(identifier, parent_talks)
        
        if self.next_talk:
            lines += self.next_talk.read_up_to(identifier, parent_talks)

        return lines

    
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
    
    def return_stack(self):
        if len(self._parent_stack) and self.first_parent.is_builder:
            builder = self._parent_stack[0]
            builder.add_stack(self._parent_stack + [self])
    
    def print(self) -> None:
        print('\n'.join(self.read()))

# ------------------------------------------------------------------------------

class ConvTalk:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int                 = id
        self._data: dict             = _conv_talks[self.id]
        self._parent_stack: ConvPath = parent_stack
        self._stack                  = self._parent_stack + [self]

        self.segments = []

        self.parse()

    @property
    def identifier(self) -> str:
        return f'Talk|{self.id}'
    
    @property
    def is_branching(self) -> bool:
        return len([id for id in self.next_talk_ids if id != -1]) != 0

    @property
    def is_branch(self) -> bool:
        return self.parent and isinstance(self.parent, ConvOption)
    
    @property
    def is_builder(self) -> bool:
        return False
    
    @property
    def is_talk(self) -> bool:
        return True
    
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
    
    def get_segments(self) -> list[ConvSegment]:
        segments = []
        
        for id in self.segment_ids:
            segment = ConvSegment(id, self._stack)
            segments.append(segment)
            self._stack.append(segment)
        
        return segments
    
    def parse(self) -> None:
        self.segments = self.get_segments()
    
    def read_up_to(self, identifier: str, parent_talks: list[ConvTalk]) -> list[str]:
        lines = []
        
        for segment in self.segments:
            if segment.identifier == identifier:
                parent_talks.append(self)
                break

            lines += segment.read_up_to(identifier, parent_talks)
        
        return lines
    
    def read(self) -> list[str]:
        lines = []
        for segment in self.segments:
            lines += segment.read()
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.read()))