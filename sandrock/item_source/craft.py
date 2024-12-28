from sandrock.common import *
from sandrock.lib.designer_config import DesignerConfig
from .common import *

def update_crafting(results: Results) -> None:
    update_assembly(results)
    update_crafting_stations(results)
    update_recycle(results)
    update_cooking(results)
    update_restoring(results)
    update_ore_refining(results)

def update_assembly(results: Results) -> None:
    for recipe in DesignerConfig.Creation:
        if recipe['fromMachineLevel'] > 10:
            continue
        ready = True
        #ready = False
        #for unlocker in _get_recipe_unlockers()[recipe['itemId']]:
        #    if unlocker in results:
        #        ready = True
        for part_id in recipe['partIds']:
            part = DesignerConfig.CreationPart[part_id]
            mat = part['material']['x']
            if mat not in results:
                ready = False
        if ready:
            source = ('crafting', '_assemble_', recipe['fromMachineLevel'])
            results[recipe['itemId']].add(source)

def update_crafting_stations(results: Results) -> None:
    for recipe in DesignerConfig.Synthetics:
        if recipe['fromMachineLevel'] > 10:
            continue
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
            source = ('crafting', f'item:{machine}')
            results[item_id].add(source)

def update_recycle(results: Results) -> None:
    for recipe in DesignerConfig.Recycle:
        if recipe['machineLevel'] > 10:
            continue
        if recipe['id'] not in results:
            continue
        source = ('recycle', f'item:{recipe["id"]}')
        for group in recipe['backGeneratorIds']:
            update_generator(results, source, group)

def update_cooking(results: Results) -> None:
    for cook in DesignerConfig.Cooking:
        for recipe_id in cook['formulaIds']:
            recipe = DesignerConfig.CookingFormula[recipe_id]
            if not recipe['isActive']:
                continue
            ready = True
            for mat in recipe['materials']:
                if mat not in results:
                    ready = False
            if ready:
                source = ('crafting', '_cooking_', recipe['cookingType'])
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
        if recipe['id'] not in results:
            continue
        source = ['ore_refining', f'item:{recipe["id"]}']
        for gen in recipe['generatorIds']:
            update_generator(results, source, gen)

@cache
def _get_recipe_unlockers() -> dict[int, list[int]]:
    unlockers = defaultdict(list)
    for item in DesignerConfig.ItemPrototype:
        if 85 in item['itemTag']:
            # basic worktable recipes unlocked by 'BLUEPRINT UNLOCK GROUP' script
            unlockers[item['id']] = [13000001]
    for machine in DesignerConfig.Machine:
        for product in machine['unlockBlueprintIds']:
            unlockers[product].append(machine['id'])
    for recipe in DesignerConfig.Blueprint:
        unlockers[recipe['id']].append(recipe['bookId'])
    for recipe in DesignerConfig.ResearchItem:
        unlockers[recipe['blueprintId']] = [19200001]
    for use in DesignerConfig.ItemUse:
        for unlocked in use['unLockIDs']:
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
