'''
Find all the ways that the ability to craft an item can be unlocked.
'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.text            import text
from sandrock.structures.story    import Story
from .common                      import *

# ------------------------------------------------------------------------------

def update_unlockers(results: Results) -> None:
    update_cooking_experimentation(results)
    update_machines(results)
    update_missions(results)
    update_recipe_books(results)
    update_recipe_inquiry(results)
    update_item_use(results)

def update_cooking_experimentation(results: Results) -> None:
    for dish in DesignerConfig.Cooking:
        source = ('cooking_experimentation',)
        formula = DesignerConfig.CookingFormula[dish['formulaId']]

        if formula['isActive'] == 1 and formula['disableTrying'] == 0:
            results[dish['outItemId']].add(source)

# Unlocked by item use. Somehow has a handful of items that aren't caught by the 
# recipe book step.
def update_item_use(results: Results) -> None:
    for use in DesignerConfig.ItemUse:
        source = ('recipe_book', use["id"])

        for unlocked in use['unLockIDs']:
            if unlocked not in results:
                print(f'{text.item(unlocked)} unlocked by {text.item(use["id"])}')
            results[unlocked].add(source)
        
        for unlocked in use['unlockCookingIDs']:
            results[unlocked].add(source)

def update_machines(results: Results) -> None:
    for machine in DesignerConfig.Machine:
        source = ('machine_acquired', f'item:{machine["id"]}')
        for product in machine['unlockBlueprintIds']:
            results[product].add(source)

def update_missions(results: Results) -> None:
    story = Story()
    for mission_id, mission in story:
        source = ('mission', 'script', f'mission:{mission_id}')
        for item in mission.get_unlocked_item_ids():
            results[item].add(source)

def update_recipe_books(results: Results) -> None:
    for recipe in DesignerConfig.Blueprint:
        if recipe['bookId'] in DesignerConfig.ItemPrototype:
            source = ('recipe_book', recipe["bookId"])
            results[recipe['id']].add(source)

def update_recipe_inquiry(results: Results) -> None:
    for inquiry in DesignerConfig.InquiryDataBase:
        if len(inquiry['npcId']) > 0:
            source = ('share_recipe', (f'npc:{npc}' for npc in inquiry['npcId']))
            results[inquiry['para']].add(source)
