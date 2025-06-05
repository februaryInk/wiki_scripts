'''
Scratch script for testing ad hoc output.
'''

from __future__ import annotations

from sandrock          import *
from sandrock.lib.text import load_text
from sandrock.preproc  import get_config_paths
from sandrock.structures.conversation import *

# ------------------------------------------------------------------------------

def run() -> None:
    print_bubbles_for_tag('BeforeRobTrain')
    print_bubbles_for_tag('RobTrain')
    
def print_bubbles_for_tag(tag: str) -> None:
    bubbles = DesignerConfig.EventBubbles
    tag_bubbles = [
        bubble for bubble in bubbles
        if tag.lower() == bubble['tag'].lower()
    ]

    print(tag_bubbles)

    if not tag_bubbles:
        print(f'No bubbles found for tag {tag}')
        return
    
    print(f'Bubbles for tag {tag}, found {len(tag_bubbles)}:\n')
    for bubble in tag_bubbles:
        event_bubble = EventBubble(bubble['id'], bubble['tag'])
        event_bubble.print()

if __name__ == '__main__':
    run()
