'''
Resource nodes the player can gather items from? Hp, level, item drops...
Might only be salvage points?
'''

from sandrock.common import *
from sandrock.lib.asset import Bundle

# ------------------------------------------------------------------------------

def find_catchable_resource_points() -> dict[str, str]:
    bundle    = Bundle('resourcepoint')
    resources = {}

    for behav in bundle.behaviours:
        if behav.script == 'CatchableResourcePoint':
            resources[behav.game_object.name] = str(behav.path)

    return resources
