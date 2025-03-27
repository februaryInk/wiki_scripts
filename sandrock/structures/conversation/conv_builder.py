'''
Constructs a conversation, starting from a given entry talk ID. The conversation
is built by following the next talk IDs and segment IDs from the entry talk.
'''

from __future__ import annotations

from sandrock                                      import *
from sandrock.structures.conversation.conv_elements import *

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
        choice_segment_stacks.append([
            item for item in stack 
            if item.startswith('ChoiceSegment') or item.startswith('TerminalSegment')
        ])

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

# -- Private Classes -----------------------------------------------------------
        
class ConvTalkMimic:
    def __init__(self, next_talk_ids: list[int]):
        self.next_talk_ids = next_talk_ids
        self.segment_ids = []
    
    @property
    def identifier(self) -> str:
        return 'TalkMimic|'
    
    @property
    def is_branch(self) -> bool:
        return False
    
    @property
    def is_builder(self) -> bool:
        return False
    
    @property
    def is_talk(self) -> bool:
        return True
    
    def set_segment_ids(self, segment_ids: list[int]) -> None:
        self.segment_ids = segment_ids

# ------------------------------------------------------------------------------

class ConvBuilder:
    def __init__(self, entry_talk_id: int, modifiers: dict[str, list[str]] = {}):
        self._entry_talk_id: int                                       = entry_talk_id
        self._modifiers: dict[str, list[str]]                          = modifiers

        self._stack: list[ConvBuilder]                                 = [self]
        self._stacks: list[list[ConvSegment | ConvOption | ConvTalk]] = []
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
    def is_builder(self) -> bool:
        return True
    
    @property
    def is_talk(self) -> bool:
        return False
    
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
                        
                        if isinstance(talk, ConvTalkMimic):
                            talk.set_segment_ids([int(id)])
                        
                        segment = ConvSegment(int(id), [self, talk])
                        parent_talks = []
                        next_common = self._common_series[i + 1][0] if i + 1 < len(self._common_series) else None
                        # Is it beneficial to consider all common segments rather than only the next?
                        # lines += ['', f'!!! Yielding control to the choice segment {identifier}. !!!', '']
                        lines += segment.read_up_to(next_common, parent_talks)
                        
                        assert len(list(map(list, {tuple(i) for i.next_talk_ids in parent_talks}))) <= 1
                        
                        if len(parent_talks):
                            talk = parent_talks.pop()
                        else:
                            talk = ConvTalkMimic([])
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
