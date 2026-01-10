'''
'''

from __future__ import annotations

from sandrock                       import *
from sandrock.structures.extras import newspaper_contents as source_newspaper_contents
from collections import OrderedDict

# ------------------------------------------------------------------------------

def run() -> None:
    def _type_of(value):
        if hasattr(value, 'type'):
            return getattr(value, 'type')
        if isinstance(value, dict):
            return value.get('type')
        return None

    newspaper_contents = OrderedDict(
        sorted(
            source_newspaper_contents.items(),
            key=lambda kv: (_type_of(kv[1]), kv[0])
        )
    )
    for _id, newspaper_content in newspaper_contents.items():
        newspaper_content.print()
        print()
        print('----------------------------------------------------------')
        print()
            

if __name__ == '__main__':
    run()
