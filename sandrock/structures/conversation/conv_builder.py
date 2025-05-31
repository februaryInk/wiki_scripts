'''
Constructs a conversation, starting from a given entry talk ID. The conversation
is built by following the next talk IDs and segment IDs from the entry talk.
'''

from __future__ import annotations

from sandrock                                       import *
from sandrock.structures.conversation.conv_elements import *

# -- Private Functions ---------------------------------------------------------

# Get the common elements that lead up to a convergence point.
def _find_common_elements(stacks: list[list[str]], convergence: str) -> list[str]:
    substacks = [
        # Get up to and including the convergence point, then reverse it.
        stack[:(stack.index(convergence) + 1)][::-1]
        for stack in stacks if convergence in stack
    ]

    # print(f'Substacks: {json.dumps(substacks, indent=2)}')
    # print(f'Convergence: {convergence}')

    # Iterate back from the convergence point to find the elements that all
    # substacks share.
    first_substack = substacks[0]
    min_substack_length = min(len(stack) for stack in substacks)
    common_series       = []

    for i in range(min_substack_length):
        if first_substack[i].startswith('Option'):
            break
        elif all(substack[i] == first_substack[i] for substack in substacks):
            common_series.append(first_substack[i])
        else:
            break
    
    return common_series[::-1]

def _find_first_convergence(stacks: list[list[str]]) -> str:
    if len(stacks) == 0: return None
    
    # Dialogue branches at choices only, so find all the choices and terminal
    # segments in the stacks (the meaningful elements for finding convergences).
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

    # Go through each stack of meaningful elements and find the first element 
    # that is shared by all stacks.
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
    
    # If there was no common element for ALL stacks, some stacks may be a situation
    # where the conversation terminates early due to a choice ("too much on my plate").
    # This time, discard stacks as we go.
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
        
        previous_length = len(choice_segment_stacks)
        # Remove stacks that don't have a next element.
        choice_segment_stacks = [
            stack for stack in choice_segment_stacks
            if len(stack) > i + 1
        ]
        if len(choice_segment_stacks) != previous_length:
            return _find_first_convergence(choice_segment_stacks)
        
    print('No common element found in any stack.')

# ------------------------------------------------------------------------------

class ConvBuilder:
    def __init__(self, entry_talk_id: int, modifiers: dict[str, list[str]] = {}):
        self._entry_talk_id: int                                      = entry_talk_id
        self._modifiers: dict[str, list[str]]                         = modifiers

        self._stack: list[ConvBuilder]                                = [self]
        self._stacks: list[list[ConvSegment | ConvOption | ConvTalk]] = []
        self._identifier_stacks: list[str]                            = []

        self._common_series = []
        self._common_series_counts = {}

        self.build()
        print(f'Stacks: {json.dumps(self._identifier_stacks, indent=2)}')
        self.find_common_series()
        print(f'Common series: {json.dumps(self._common_series, indent=2)}')
    
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
    
    # Some stacks repeat a choice segment twice for a looping dialogue option,
    # which messes up our attempts to collapse the stacks into a single
    # conversation thread. This function removes those duplicate choices.
    def clean_stacks(self) -> None:
        cleaned_stacks = []

        for stack in self._identifier_stacks:
            cleaned_stack = []

            for identifier in stack:
                if identifier.startswith('ChoiceSegment') or identifier.startswith('Option'):
                    if identifier in cleaned_stack:
                        continue
                
                cleaned_stack.append(identifier)
            
            cleaned_stacks.append(cleaned_stack)
        
        self._identifier_stacks = cleaned_stacks
    
    def find_common_series(self) -> None:
        stacks = self._identifier_stacks
        common_series = []

        while True:
            first_convergence = _find_first_convergence(stacks)
            if not first_convergence: break

            # print(f'First convergence: {first_convergence}')

            applicable_stacks = [
                stack for stack in stacks
                if first_convergence in stack
            ]
            common_series.append(_find_common_elements(applicable_stacks, first_convergence))
            
            new_stacks = []
            for stack in applicable_stacks:
                stack_remainder = stack[stack.index(first_convergence) + 1:]
                if len(stack_remainder) > 0:
                    new_stacks.append(stack_remainder)
        
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
                        
                        segment = ConvSegment(int(id), [self, talk])
                        parent_talks = []
                        next_common = self._common_series[i + 1][0] if i + 1 < len(self._common_series) else None
                        # Is it beneficial to consider all common segments rather than only the next?
                        # lines += ['', f'!!! Yielding control to the choice segment {identifier}. !!!', '']
                        lines += segment.read_up_to(next_common, parent_talks)
                        
                        assert len(list(map(list, {tuple(i.next_talk_ids) for i in parent_talks}))) <= 1
                        
                        if len(parent_talks):
                            talk = parent_talks.pop()
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
