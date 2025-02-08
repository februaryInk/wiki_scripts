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

- Start from the last talk.
- Branches with similar endings can only merge at a common ancestor. Lift the common elements to the ancestor for printing.
- Branches with similar endings can only merge at a common ancestor. Lift the common elements to the ancestor for printing.
- Common elements can only occur at the end of a ConvTalk, or as the entire ConvTalk.
- How do you determine the "True" ending of a conversation, as opposed to a branch that terminates the conversation early?

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

def find_max_shared_ending(compositions):
    reversed_compositions = [comp[::-1] for comp in compositions]

    prefix_count = defaultdict(int)
    
    for comp in reversed_compositions:
        prefix = []
        for num in comp:
            prefix.append(num)
            prefix_count[tuple(prefix)] += 1

    # Find the longest prefix with the maximum count.
    max_prefix = []
    max_count = 0
    for prefix, count in prefix_count.items():
        if count > max_count or (count == max_count and len(prefix) > len(max_prefix)):
            max_prefix = prefix
            max_count = count

    # Reverse the prefix back to its original order.
    return list(max_prefix[::-1])

def _substitute(text):
    pattern = re.compile('|'.join(re.escape(key) for key in _substitutions.keys()))
    return pattern.sub(lambda match: _substitutions[match.group(0)], text)

# Add: If nextTalk is in the parent stack, print that the conversation repeats
# for the given option.
class _ConvOption:
    def __init__(self, content_id, talk_id, index, parent_stack: list[Any] = []):
        self.index: int    = index
        self._content_id   = content_id
        self._talk_id      = talk_id
        self._parent_stack = parent_stack
        self.id: str       = f'{self.parent.id}_{index}'

        self.parse()
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))

    @property
    def identifier(self) -> str:
        return f'Option|{self.id}'
    
    @property
    def line(self) -> list[str]:
        indent = self._indent_count * ':'
        return f'{indent}*\'\'{_substitute(self.content)}\'\''
    
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
    
    def read_response_talk(self) -> list[str]:
        if self.response_talk:
            return self.response_talk.read()
        else:
            return []

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

class ConvSegment:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int = id
        self._data: dict = _conv_segments[id]
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
        if self.conv_parent and self.conv_parent.is_branch and self.id == self.conv_parent.segment_ids[0]:
            args.append(f'answer={self.conv_parent.parent.content}\n')
        args.append(self.content)
        return '{{' + '|'.join(args) + '}}'
    
    @property
    def content(self) -> str:
        text_id = int(self._data['content'].split('|', 1)[0])
        return _substitute(text.text(text_id))
    
    @property
    def identifier(self) -> str:
        if len(self.conv_option_content_ids):
            return f'ChoiceSegment|{self.id}'
        return f'Segment|{self.id}'
    
    @property
    def is_terminal(self) -> str:
        if self.conv_parent:
            assert isinstance(self.conv_parent, ConvTalk)
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
    def conv_parent(self) -> ConvTalk:
        for item in reversed(self._parent_stack):
            if isinstance(item, ConvTalk):
                return item
    
    @property
    def conv_option_content_ids(self) -> list[int]:
        split_content = self._data['content'].split('|', 1)
        if len(split_content) > 1:
            return [int(id) for id in split_content[1].split(',')]
        else:
            return []
    
    def get_conv_options(self) -> list[_ConvOption]:
        if not len(self.conv_option_content_ids):
            return []
        
        if self.conv_parent:
            assert isinstance(self.conv_parent, ConvTalk)
            # assert self.id == self.conv_parent.segment_ids[-1]
            
            talk_ids = self.conv_parent.next_talk_ids
        else:
            talk_ids = [-1] * len(self.conv_option_content_ids)
        
        # assert len(talk_ids) == len(self.conv_option_content_ids)
        # TODO: Combine options with a single result.
        return [_ConvOption(content_id, talk_id, index, self._parent_stack + [self]) for index, (content_id, talk_id) in enumerate(zip(self.conv_option_content_ids, talk_ids))]
    
    def parse(self) -> None:
        self.conv_options = self.get_conv_options()
        if self.is_terminal:
            self.return_stack()
    
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
            builder.add_stack([conv.identifier for conv in self._parent_stack + [self]])
    
    def print(self) -> None:
        print('\n'.join(self.read()))

class ConvTalk:
    def __init__(self, id, parent_stack: list[Any] = []):
        self.id: int                        = id
        self._data: dict                    = _conv_talks[self.id]
        self._parent_stack: list[ConvTalk | ConvSegment | _ConvOption] = parent_stack
        self._stack = self._parent_stack + [self]

        self.stacks = []
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
        print(self.segment_ids)
        for id in self.segment_ids:
            segment = ConvSegment(id, self._stack)
            segments.append(segment)
            self._stack.append(segment)
        return segments
    
    def parse(self) -> None:
        self.segments = self.get_segments()
    
    def read(self) -> list[str]:
        lines = []
        print(len(self.segments))
        for segment in self.segments:
            lines += segment.read()
        return lines
    
    def print(self) -> None:
        print('\n'.join(self.read()))

class ConvBuilder:
    def __init__(self, entry_talk_id: int):
        self._entry_talk_id: int = entry_talk_id
        self._stack: list[ConvBuilder] = [self]
        self._stacks: list[str] = []

        self.build()

        # Can't do this; different parent stacks make components unique by more
        # than id.
        self._components = {
            'options': {},
            'segments': {},
            'talks': {}
        }

        print(json.dumps(self._stacks, indent=2))

        self.find_common_series()
        self.count_common_series()
    
    @property
    def identifier(self) -> str:
        return 'ConvBuilder'
    
    def add_stack(self, stack) -> None:
        self._stacks.append(stack)
    
    def build(self) -> None:
        self._entry_talk = ConvTalk(self._entry_talk_id, self._stack)
    
    @property
    def common_series(self) -> list[ConvSegment]:
        return [ConvSegment(id, [], self._stack) for id in self.segment_ids]
    
    def count_common_series(self) -> None:
        stacks = self._stacks
        counts = {}
        for series in self._common_series:
            count = sum(1 for stack in stacks if is_subarray(series, stack))
            counts[series] = count
        self._common_series_counts = counts
    
    def find_common_series(self) -> None:
        stacks = self._stacks
        common_series = []
        while True:
            first_convergence = find_first_convergence(stacks)
            print(first_convergence)
            if not first_convergence:
                break
            common_series.append(find_common_series(stacks, first_convergence))
            
            new_stacks = []
            for stack in stacks:
                if first_convergence in stack:
                    new_stacks.append(stack[stack.index(first_convergence):])
                else:
                    # TODO: What if it converges later? Needs a note to skip forwards.
                    new_stacks.append(stack)
            stacks = new_stacks # list(set(new_stacks))
        
        self._common_series = common_series

    def read(self) -> list[str]:
        pass

    def print(self) -> None:
        # print(json.dumps(self._stacks, indent=2))
        print(json.dumps(self._common_series, indent=2))

def find_common_series(stacks: list[list[str]], convergence: str) -> list[str]:
    print(stacks)
    print(convergence)
    substacks = [
        stack[:(stack.index(convergence) + 1)][::-1]
        for stack in stacks if convergence in stack
    ]

    print(substacks)
    min_substack_length = min(len(stack) for stack in substacks)

    common_series = []
    for i in range(min_substack_length):
        if all(substack[i] == substacks[0][i] for substack in substacks):
            common_series.append(substacks[0][i])
        else:
            break
    return common_series.reverse()

def find_first_convergence(stacks: list[list[str]]) -> str:
    choice_segment_stacks = []
    for stack in stacks:
        choice_segment_stacks.append([item for item in stack if item.startswith('ChoiceSegment')])
    print(choice_segment_stacks)
    max_stack_length = max(len(stack) for stack in choice_segment_stacks)

    print("Max stack length:")
    print(range(max_stack_length))

    sub_elements = []
    for i in range(max_stack_length):
        sub_stacks = [stack[:(i + 1)] for stack in choice_segment_stacks]

        print("Sub stacks:")
        print(sub_stacks)

        for j in range(i + 1):
            for sub_stack in sub_stacks:
                if j < len(sub_stack) and sub_stack[j] not in sub_elements:
                    sub_elements.append(sub_stack[j])
        
        print("Sub elements:")
        print(sub_elements)
        
        for element in sub_elements:
            if all(element in sub_stack for sub_stack in sub_stacks):
                print("Returning element:")
                print(element)
                return element

    choice_segment_stacks_count = len(choice_segment_stacks)   
    for element in sub_elements:
        stacks_with_element_count = sum(1 for stack in choice_segment_stacks if element in stack)
        if stacks_with_element_count > choice_segment_stacks_count / 2.0:
            return element
        
def is_subarray(subarray, array):
    n, m = len(array), len(subarray)
    for i in range(n - m + 1):
        if array[i:i + m] == subarray:
            return True
    return False