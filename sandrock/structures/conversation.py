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

Every time we have a set of options, we need to check if we can merge back into a single
conversational branch.

[
  ['T1', 'S1', 'S2', 'T2', 'S3',                         'S4', 'S5', 'T6', 'S10', 'S12'], 
  ['T1', 'S1', 'S2', 'T3', 'S6', 'S7', 'S8', 'T4', 'S9', 'S4', 'S5', 'T7', 'S11', 'S12'],
  ['T1', 'S1', 'S2', 'T3', 'S6', 'S7', 'S8', 'T5', 'S5', 'S9'],
  ['T1', 'S1', 'S2', 'T3', 'S6', 'S7', 'S8', 'T8',       'S9']
]

When the conversation encounters a choice, look for the nearest shared future common segments that all end in either another choice, or all end in a terminal segment.
If a branch terminates without sharing any such common segments with other branches, then it is removed from the running for checks at the next choice.
If an option leads to a terminating next talk while other branches are longer, the player probably turned something down. The other branch(es) are the important ones.
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

# -- Private Functions ---------------------------------------------------------

# Get the common elements that lead up to a convergence point.
def _find_common_elements(stacks: list[list[str]], convergence: str) -> list[str]:
    substacks = [
        # Get up to and including the convergence point, then reverse it.
        stack[:(stack.index(convergence) + 1)][::-1]
        for stack in stacks if convergence in stack
    ]

    # Iterate back from the convergence point to find the elements that all
    # substacks share.
    min_substack_length = min(len(stack) for stack in substacks)
    common_series       = []
    for i in range(min_substack_length):
        if all(substack[i] == substacks[0][i] for substack in substacks):
            common_series.append(substacks[0][i])
        else:
            break
    
    return common_series[::-1]

def _find_first_convergence(stacks: list[list[str]]) -> str:
    if len(stacks) == 0: return None
    
    choice_segment_stacks = []
    
    for stack in stacks:
        choice_segment_stacks.append([item for item in stack if item.startswith('ChoiceSegment') or item.startswith('TerminalSegment')])

    max_stack_length = max(len(stack) for stack in choice_segment_stacks)
    sub_elements = []

    # print(choice_segment_stacks)
    # print(f'Max stack length: {range(max_stack_length)}')

    for i in range(max_stack_length):
        sub_stacks = [stack[:(i + 1)] for stack in choice_segment_stacks]

        # print("Sub stacks:")
        # print(json.dumps(sub_stacks, indent=2))

        for j in range(i + 1):
            for sub_stack in sub_stacks:
                if j < len(sub_stack) and sub_stack[j] not in sub_elements:
                    sub_elements.append(sub_stack[j])
        
        # print("Sub elements:")
        # print(sub_elements)
        
        for element in sub_elements:
            if all(element in sub_stack for sub_stack in sub_stacks):
                # print("Returning element:")
                # print(element)
                return element

    # TODO: Should we consider elements shared by a significant majority? If 
    # yes, we need to discard stacks that never reconverge. Honestly, might not
    # be worth the effort of writing that code versus just fixing the output
    # manually after the fact.

    # choice_segment_stacks_count = len(choice_segment_stacks)   
    # for element in sub_elements:
    #     stacks_with_element_count = sum(1 for stack in choice_segment_stacks if element in stack)
    #     if stacks_with_element_count > 1 and stacks_with_element_count > choice_segment_stacks_count * 0.75:
    #         return element

def _substitute(text):
    pattern = re.compile('|'.join(re.escape(key) for key in _substitutions.keys()))
    return pattern.sub(lambda match: _substitutions[match.group(0)], text)

# -- Private Classes -----------------------------------------------------------

# TODO: If nextTalk is in the parent stack, print that the conversation repeats
# for the given option. Otherwise, will we loop infinitely?
class _ConvOption:
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
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
    @property
    def choice_type(self) -> str:
        type_map = {
            4: 'flirt'
        }
        assert self._choice_type in [-1, 4], f'Unhandled choice type {self._choice_type}'
        
        return type_map.get(self._choice_type, None)

    @property
    def identifier(self) -> str:
        return f'Option|{self.id}'
    
    @property
    def line(self) -> list[str]:
        indent = self._indent_count * ':'
        type = '{{flirt}}' if self.choice_type == 'flirt' else ''
        return f'{indent}*{type}\'\'{_substitute(self.content)}\'\''
    
    @property
    def parent(self) -> ConvSegment:
        parent = self._parent_stack[-1]
        assert isinstance(parent, ConvSegment)
        return parent
    
    def find_response_talk(self) -> ConvTalk:
        if self._talk_id == -1: return None
        return ConvTalk(self._talk_id, self._parent_stack + [self])
    
    def parse(self) -> None:
        self.content       = _substitute(text.text(self._content_id))
        self.response_talk = self.find_response_talk()
    
    def read_response_talk_up_to(self, identifier: str, next_talk_ids_list: list[list]) -> list[str]:
        if self.response_talk:
            return self.response_talk.read_up_to(identifier, next_talk_ids_list)
        else:
            return []
    
    def read_response_talk(self) -> list[str]:
        if self.response_talk:
            return self.response_talk.read()
        else:
            return []
        
class _ConvTalkMimic:
    def __init__(self, next_talk_ids: list[int]):
        self.next_talk_ids = next_talk_ids
        self.segment_ids = []
    
    @property
    def identifier(self) -> str:
        return 'TalkMimic|'
    
    @property
    def is_branch(self) -> bool:
        return False
    
    def set_segment_ids(self, segment_ids: list[int]) -> None:
        self.segment_ids = segment_ids

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
        return _substitute(text(self._text_id))
    
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
    _bubble: Bubble
    _data: dict
    id: int

    def __init__(self, id: int):
        self.id    = id
        self._data = _conv_chats[id]
        self._bubble = Bubble(self.speaker_id, self.text_id)

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

# AssetConvSegmentConversationSegment
class ConvSegment:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int       = id
        self._data: dict   = _conv_segments[id]
        self._parent_stack = parent_stack

        self.parse()
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
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
        return _substitute(text.text(text_id))
    
    @property
    def identifier(self) -> str:
        if len(self.conv_option_content_ids):
            return f'ChoiceSegment|{self.id}'
        if self.is_terminal:
            return f'TerminalSegment|{self.id}'
        return f'Segment|{self.id}'
    
    @property
    def is_terminal(self) -> str:
        if self.conv_parent:
            assert isinstance(self.conv_parent, ConvTalk) or isinstance(self.conv_parent, _ConvTalkMimic)
            talk_ids = self.conv_parent.next_talk_ids
            if self.id == self.conv_parent.segment_ids[-1] and not any(x != -1 for x in talk_ids):
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
        if len(self._parent_stack) and isinstance(self._parent_stack[0], ConvBuilder):
            return self._parent_stack[0]
    
    @property
    def conv_parent(self) -> ConvTalk:
        # print([item.identifier for item in self._parent_stack])
        for item in reversed(self._parent_stack):
            if isinstance(item, ConvTalk) or isinstance(item, _ConvTalkMimic):
                return item
    
    @property
    def option_parent(self) -> _ConvOption:
        # There will be a talk between the segment and the option.
        if self.conv_parent and self.conv_parent.is_branch and self.id == self.conv_parent.segment_ids[0]:
            return self.conv_parent.parent
    
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
    
    def get_conv_options(self) -> list[_ConvOption]:
        if not len(self.conv_option_content_ids):
            return []
        
        if self.conv_parent:
            assert isinstance(self.conv_parent, ConvTalk) or isinstance(self.conv_parent, _ConvTalkMimic)
            assert self.id == self.conv_parent.segment_ids[-1]
            
            talk_ids = self.conv_parent.next_talk_ids
        else:
            talk_ids = [-1] * len(self.conv_option_content_ids)
        
        choices = zip(self.conv_option_content_ids, talk_ids, self.choice_types)
        
        assert len(talk_ids) == len(self.conv_option_content_ids)
        # TODO: Combine options with a single result?
        return [_ConvOption(content_id, talk_id, choice_type, index, self._parent_stack + [self]) for index, (content_id, talk_id, choice_type) in enumerate(choices)]
    
    def get_next_talk(self) -> ConvTalk:
        if self.conv_parent and not len(self.conv_option_content_ids) and self.id == self.conv_parent.segment_ids[-1]:
            assert len(self.conv_parent.next_talk_ids) == 1
            next_talk_id = self.conv_parent.next_talk_ids[0]
            if next_talk_id != -1:
                return ConvTalk(next_talk_id, self._parent_stack)
        
        return None
    
    def parse(self) -> None:
        self.conv_options = self.get_conv_options()
        self.next_talk    = self.get_next_talk()

        if self.is_terminal:
            assert not self.conv_options
            assert not self.next_talk
            self.return_stack()
    
    def read_up_to(self, identifier: str, next_talk_ids_list: list[list]) -> list[str]:
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
                lines += option.read_response_talk_up_to(identifier, next_talk_ids_list)
        
        if self.next_talk:
            lines += self.next_talk.read_up_to(identifier, next_talk_ids_list)

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
        if len(self._parent_stack) and isinstance(self._parent_stack[0], ConvBuilder):
            builder = self._parent_stack[0]
            builder.add_stack(self._parent_stack + [self])
    
    def print(self) -> None:
        print('\n'.join(self.read()))

# -- ConvTalk ------------------------------------------------------------------
# AssetConvTalkConversationTalk

class ConvTalk:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int                                                   = id
        self._data: dict                                               = _conv_talks[self.id]
        self._parent_stack: list[ConvTalk | ConvSegment | _ConvOption] = parent_stack
        self._stack                                                    = self._parent_stack + [self]

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
    
    def get_segments(self) -> list[ConvSegment]:
        segments = []
        
        for id in self.segment_ids:
            segment = ConvSegment(id, self._stack)
            segments.append(segment)
            self._stack.append(segment)
        
        return segments
    
    def parse(self) -> None:
        self.segments = self.get_segments()
    
    def read_up_to(self, identifier: str, next_talk_ids_list: list[list]) -> list[str]:
        lines = []
        for segment in self.segments:
            if segment.identifier == identifier:
                next_talk_ids_list.append(self.next_talk_ids)
                break
            lines += segment.read_up_to(identifier, next_talk_ids_list)
        return lines
    
    def read(self) -> list[str]:
        lines = []
        for segment in self.segments:
            lines += segment.read()
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.read()))

class ConvBuilder:
    def __init__(self, entry_talk_id: int, modifiers: dict[str, list[str]] = {}):
        self._entry_talk_id: int                                       = entry_talk_id
        self._modifiers: dict[str, list[str]]                          = modifiers

        self._stack: list[ConvBuilder]                                 = [self]
        self._stacks: list[list[ConvSegment | _ConvOption | ConvTalk]] = []
        self._identifier_stacks: list[str]                             = []

        self._common_series = []
        self._common_series_counts = {}

        self.build()
        self.find_common_series()
    
    @property
    def common_series(self) -> list[ConvSegment]:
        return [ConvSegment(id, [], self._stack) for id in self.segment_ids]
    
    @property
    def identifier(self) -> str:
        return 'Builder|'
    
    @property
    def option_modifiers(self) -> dict[str, set[tuple]]:
        return self._modifiers.get('option', {})
    
    @property
    def segment_modifiers(self) -> dict[str, set[tuple]]:
        return self._modifiers.get('segment', {})
    
    def add_stack(self, stack) -> None:
        self._stacks.append(stack)
        self._identifier_stacks.append([item.identifier for item in stack])
    
    def build(self) -> None:
        self._entry_talk = ConvTalk(self._entry_talk_id, self._stack)
    
    def find_common_series(self) -> None:
        stacks = self._identifier_stacks
        common_series = []

        while True:
            first_convergence = _find_first_convergence(stacks)
            if not first_convergence: break

            # print(f'First convergence: {first_convergence}')

            common_series.append(_find_common_elements(stacks, first_convergence))
            
            new_stacks = []
            for stack in stacks:
                if first_convergence in stack:
                    stack_remainder = stack[stack.index(first_convergence) + 1:]
                    if len(stack_remainder) > 0:
                        new_stacks.append(stack_remainder)
                else:
                    # TODO: What if it converges later? Needs a note to skip forwards.
                    new_stacks.append(stack)
        
            stacks = new_stacks # list(set(new_stacks))
        
        self._common_series = common_series

    def read(self) -> list[str]:
        lines = []
        talk = None

        assert self._common_series[0][0] == self.identifier

        for i, series in enumerate(self._common_series):
            for j, identifier in enumerate(series):
                type, id = identifier.split('|', 1)
                
                match type:
                    case 'Builder':
                        assert i == 0 and j == 0
                        continue
                    case 'ChoiceSegment':
                        assert j == len(series) - 1
                        
                        if isinstance(talk, _ConvTalkMimic):
                            talk.set_segment_ids([int(id)])
                        
                        segment = ConvSegment(int(id), [self, talk])
                        next_talk_ids_list = []
                        next_common = self._common_series[i + 1][0] if i + 1 < len(self._common_series) else None
                        # Is it beneficial to consider all common segments rather than only the next?
                        # lines += ['', f'!!! Yielding control to the choice segment {identifier}. !!!', '']
                        lines += segment.read_up_to(next_common, next_talk_ids_list)
                        
                        assert len(list(map(list, {tuple(i) for i in next_talk_ids_list}))) < 2
                        
                        if len(next_talk_ids_list):
                            talk = _ConvTalkMimic(next_talk_ids_list[0])
                        else:
                            talk = _ConvTalkMimic([])
                    case 'Segment':
                        segment = ConvSegment(int(id), [self])
                        lines += segment.read()
                    case 'Talk':
                        talk = ConvTalk(int(id))
                    case 'TerminalSegment':
                        segment = ConvSegment(int(id), [self])
                        lines += segment.read()
                        lines += ['The conversation ends.']
                    case _:
                        raise ValueError(f'Unhandled identifier {identifier}')
        
        return lines

    def print(self) -> None:
        print('\n'.join(self.read()))

    def print_debug(self) -> None:
        print(json.dumps(self._identifier_stacks, indent=2))
        print(json.dumps(self._common_series, indent=2))
