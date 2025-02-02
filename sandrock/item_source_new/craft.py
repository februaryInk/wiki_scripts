'''
Find all the items the player can craft through various means.
'''

from sandrock.common              import *
from sandrock.lib.designer_config import DesignerConfig
from sandrock.lib.text            import text
from .common                      import *

# ------------------------------------------------------------------------------

def update_crafting(results: Results) -> None:
    update_assembly(results)
    update_crafting_stations(results)
    update_recycle(results)
    update_cooking(results)
    update_restoring(results)
    update_ore_refining(results)

def update_assembly(results: Results) -> None:
    for recipe in DesignerConfig.Creation:
        assert recipe['fromMachineLevel'] < 4, f'Assembly recipe {text.item(recipe["itemId"])} has invalid level {recipe["fromMachineLevel"]}'

        # Confirm that all parts are available.
        ready = True
        for part_id in recipe['partIds']:
            part = DesignerConfig.CreationPart[part_id]
            mat = part['material']['x']
            if mat not in results:
                ready = False
        if ready:
            source = ('crafting', 'assemble', recipe['fromMachineLevel'])
            results[recipe['itemId']].add(source)

def update_crafting_stations(results: Results) -> None:
    for recipe in DesignerConfig.Synthetics:
        item_id = recipe['itemId']
        ready = False
        for unlocker in _get_recipe_unlockers()[item_id]:
            if unlocker in results:
                ready = True
        for mat in recipe['rawMaterials']:
            if mat['x'] not in results:
                ready = False
        if ready:
            machine = _find_machine(recipe['fromMachineType'], recipe['fromMachineLevel'])
            if machine is None:
                # TODO: Check on Bone Necklace, which is crafted at a level 99 machine.
                print(f'No machine found for {text.item(item_id)}, type {recipe["fromMachineType"]}, level {recipe["fromMachineLevel"]}')
            source = ('crafting', f'item:{machine}')
            results[item_id].add(source)

def update_recycle(results: Results) -> None:
    for recipe in DesignerConfig.Recycle:
        assert recipe['machineLevel'] < 4, f'Recycling recipe {text.item(recipe["id"])} has invalid level {recipe["machineLevel"]}'
        # Material being recycled.
        if recipe['id'] not in results: continue

        source = ('recycle', f'item:{recipe["id"]}')
        for group in recipe['backGeneratorIds']:
            update_generator(results, source, group)

def update_cooking(results: Results) -> None:
    for cook in DesignerConfig.Cooking:
        recipe = DesignerConfig.CookingFormula[cook['formulaId']]
        if not recipe['isActive']: continue

        ready = True
        for mat in recipe['materials']:
            if mat not in results:
                ready = False
        if ready:
            source = ('crafting', 'cooking', recipe['cookingType'])
            results[cook['outItemId']].add(source)

def update_restoring(results: Results) -> None:
    for recipe in DesignerConfig.Restore:
        ready = True
        for mat in recipe['partsItemIds']:
            if mat not in results:
                ready = False
        if ready:
            source = ('relic',)
            results[recipe['id']].add(source)

def update_ore_refining(results: Results) -> None:
    for recipe in DesignerConfig.Screening:
        # Material being refined.
        if recipe['id'] not in results: continue
        source = ['ore_refining', f'item:{recipe["id"]}']
        for gen in recipe['generatorIds']:
            update_generator(results, source, gen)

@cache
def _get_recipe_unlockers() -> dict[int, list[int]]:
    unlockers = defaultdict(list)
    for item in DesignerConfig.ItemPrototype:
        if 85 in item['itemTag']:
            # Basic worktable recipes unlocked by 'BLUEPRINT UNLOCK GROUP' script.
            unlockers[item['id']] = [13000001] # Worktable.
        if 86 in item['itemTag']:
            # Basic assembly station recipes unlocked by 'BLUEPRINT UNLOCK GROUP' script.
            unlockers[item['id']] = [13000004]
    # Unlocked by machine aquisition.
    for machine in DesignerConfig.Machine:
        for product in machine['unlockBlueprintIds']:
            unlockers[product].append(machine['id'])
    # Unlocked by recipe book.
    for recipe in DesignerConfig.Blueprint:
        if recipe['bookId'] in DesignerConfig.ItemPrototype:
            # print(f'{text.item(recipe["id"])} unlocked by {text.item(recipe["bookId"])}')
            unlockers[recipe['id']].append(recipe['bookId'])
    # Unlocked by Research Center.
    for recipe in DesignerConfig.ResearchItem:
        unlockers[recipe['blueprintId']] = [19200001] # Data discs.
    # Unlocked by item use. Somehow has a handful of items that aren't caught by
    # the recipe book step.
    for use in DesignerConfig.ItemUse:
        for unlocked in use['unLockIDs']:
            # if unlocked not in unlockers:
            #     print(f'{text.item(unlocked)} unlocked by {text.item(use["id"])}')
            unlockers[unlocked].append(use['id'])

    return unlockers

@cache
def _find_machine(type_: int, level: int) -> str:
    if level == 0:
        level = 1
    for machine in DesignerConfig.Machine:
        if machine['tag'] == type_ and machine['level'] == level:
            return machine['id']
    return f'{type_}:{level}'
