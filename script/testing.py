'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths

from pathvalidate import sanitize_filename

# ------------------------------------------------------------------------------

indents = [
    'none',
    'true',
    'double',
    'triple',
    '4',
    '5'
]

conv_segments = DesignerConfig.ConvSegement
conv_talks = DesignerConfig.ConvTalk

class _ConvOption:
    def __init__(self, content_id, talk_id, parent_stack: list[Any] = []):
        self._content_id   = content_id
        self._talk_id      = talk_id
        self._parent_stack = parent_stack
    
    @property
    def content(self) -> str:
        return text.text(self._content_id)
    
    @property
    def response_talk(self) -> _ConvTalk:
        if self._talk_id == -1: return None
        return _ConvTalk(self._talk_id, self._parent_stack + [self])
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
    @property
    def line(self) -> list[str]:
        indent = self._indent_count * ':'
        return f'{indent}*\'\'{self.content}\'\''
    
    def print_response_talk(self) -> list[str]:
        if self.response_talk:
            return self.response_talk.print()
        else:
            return []

class _ConvSegment:
    def __init__(self, id, parent_stack: list[Any] = []):
        self._id = id
        self._data = conv_segments[id]
        self._parent_stack = parent_stack
    
    @property
    def _indent_count(self):
        return sum(1 for item in self._parent_stack if isinstance(item, _ConvOption))
    
    @property
    def content(self) -> str:
        text_id = int(self._data['content'].split('|', 1)[0])
        return text.text(text_id)
    
    @property
    def speaker_name(self) -> str:
        speaker_id = int(self._data['speakerId'])
        return text.npc(speaker_id)
    
    @property
    def parent(self) -> _ConvTalk:
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
        
        assert isinstance(self.parent, _ConvTalk)
        assert self._id == self.parent.segment_ids[-1]
        talk_ids = self.parent.next_talk_ids
        assert len(talk_ids) == len(self.conv_option_content_ids)
        return [_ConvOption(content_id, talk_id, self._parent_stack + [self]) for content_id, talk_id in zip(self.conv_option_content_ids, talk_ids)]
    
    @property
    def _line(self) -> str:
        args = ['dialogue', self.speaker_name]
        if self._indent_count:
            args.append(f'indent={indents[self._indent_count]}')
        args.append(self.content)
        return '{{' + '|'.join(args) + '}}'
    
    def print(self) -> list[str]:
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
                lines += option.print_response_talk()
        
        return lines

class _ConvTalk:
    def __init__(self, id, parent_stack: list[Any] = []):
        self._data = conv_talks[id]
        self._parent_stack = parent_stack
    
    @property
    def next_talk_ids(self) -> list[int]:
        return self._data['nextTalkId']

    @property
    def segment_ids(self) -> list[int]:
        return self._data['segmentIdList']
    
    @property
    def segments(self) -> list[_ConvSegment]:
        return [_ConvSegment(id, self._parent_stack + [self]) for id in self.segment_ids]
    
    def print(self) -> list[str]:
        lines = []
        for segment in self.segments:
            lines += segment.print()
        return lines
    
    def read(self) -> None:
        print('\n'.join(self.print()))

def run() -> None:
    conv = _ConvTalk(25, [])
    conv.read()

def print_scenes() -> None:
    for scene in DesignerConfig.Scene:
        print(f'{scene['scene']}: {text.scene(scene['scene'])}')

def test_dump_parsing() -> None:
    path = config.assets_root / 'scene/additive/apartment/GameObject/m1 @501.txt'
    print(json.dumps(read_asset_dump(path), indent=2))

if __name__ == '__main__':
    run()
