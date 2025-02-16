'''

'''

from __future__ import annotations

from sandrock                           import *
from sandrock.lib.asset                 import Asset
from sandrock.structures.story_xml.stmt import *

if TYPE_CHECKING:
    from sandrock.structures.story import Mission

# ------------------------------------------------------------------------------

class Trigger:
    def __init__(self, trigger: ElementTree.Element, mission: Mission):
        self._mission: Mission             = mission
        self._trigger: ElementTree.Element = trigger
        self._procedure: float             = float(self._trigger.get('procedure'))
        self._step: float                  = float(self._trigger.get('step'))
        self._structure = {
            'EVENTS': self.eval_stmts(trigger.findall('EVENTS')),
            'CONDITIONS': self.eval_stmts(trigger.findall('CONDITIONS')),
            'ACTIONS': self.eval_stmts(trigger.findall('ACTIONS'))
            # 'RELY' ?
        }

    def get_unlocked_item_ids(self) -> list[int]:
        unlock_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_blueprint_unlock]
        item_ids = sum([stmt.item_ids for stmt in unlock_stmts], [])

        return item_ids
    
    def get_received_gifts(self) -> dict[tuple, list[int]]:
        mission_id = self._mission.id
        mission_type = 'event' if self._mission.is_event else 'mission'
        gift_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_npc_send_gift]
        gift_ids = [stmt.gift_id for stmt in gift_stmts]

        return (mission_id, gift_ids)
    
    # Sometimes a mission controller handles sending mail after a mission script 
    # is completed.
    def get_mail_id_by_mission_id(self) -> tuple[int, list[int]]:
        mission_id = self._mission.id
        mail_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_mail_delivery]

        if len(mail_stmts) == 0: return (mission_id, [])

        if self._mission.is_controller:
            causal_mission_ids = []
            if len([event for event in self._structure['EVENTS'] if event.is_every_day]) > 0:
                for stmt in self._structure['CONDITIONS']:
                    if stmt.is_check_mission_state and stmt.is_completed:
                        causal_mission_ids.append(stmt.mission_id)
                    
                    if stmt.is_check_var:
                        var_setter_id = self._mission.get_vars_to_mission_id().get(stmt.name)
                        if var_setter_id is not None:
                            causal_mission_ids.append(var_setter_id)
            
            if len(causal_mission_ids) == 1:
                mission_id = causal_mission_ids[0]
            if len(causal_mission_ids) > 1:
                print(f'Warning: Multiple causal missions found for mail delivery in controller {mission_id}: {causal_mission_ids}')
        
        return (mission_id, [stmt.mail_id for stmt in mail_stmts])
    
    def get_received_items(self) -> dict[tuple, list[int]]:
        mission_id = self._mission.id
        mission_type = 'event' if self._mission.is_event else 'mission'
        item_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_receive_item]

        if len(item_stmts) == 0: return ((mission_type, 'script', f'mission:{mission_id}'), [])

        causal_event = (mission_type, 'script', f'mission:{mission_id}')
        if self._mission.is_controller:
            causal_events = []
            for stmt in self._structure['CONDITIONS']:
                if stmt.is_check_mission_state and stmt.is_completed:
                    causal_events.append((mission_type, 'script', f'mission:{stmt.mission_id}'))
                if stmt.is_check_relationship_level:
                    causal_events.append(('npc', 'relationship', f'npc:{stmt.npc}', stmt.level))
            
            if len(self._structure['CONDITIONS']) == 1 and self._structure['CONDITIONS'][0].is_always:
                for stmt in self._structure['EVENTS']:
                    if stmt.is_conversation_end:
                        causal_events.append(('npc', 'conversation', f'npc:{stmt.npc}'))
            
            if len(causal_events) == 1:
                causal_event = causal_events[0]
            elif len(causal_events) > 1:
                missions = [event for event in causal_events if event[0] == 'mission']
                conversations = [event for event in causal_events if event[0] == 'conversation']
                relationships = [event for event in causal_events if event[0] == 'relationship']
                if len(missions) == 1:
                    causal_event = missions[0]
                elif len(conversations) == 1:
                    causal_event = conversations[0]
                elif len(relationships) == 1:
                    causal_event = relationships[0]
                else:
                    print(f'Warning: Multiple causal events found for item reception in controller {mission_id}: {causal_events}')
        
        return (causal_event, [stmt.item_id for stmt in item_stmts])
    
    def get_item_id_by_mission_id(self) -> tuple[int, list[int]]:
        mission_id = self._mission.id
        item_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_receive_item]

        if len(item_stmts) == 0: return (mission_id, [])

        if self._mission.is_controller:
            for stmt in self._structure['CONDITIONS']:
                if stmt.is_check_mission_state and stmt.is_successfully_completed:
                    assert mission_id == self._mission.id, f'Item source is ambiguous: Mission {self._mission.id}, Procedure {self._procedure}, Step {self._step}'
                    mission_id = stmt.mission_id
        
        return (mission_id, [stmt.item_id for stmt in item_stmts])
    
    def get_initialized_vars_by_mission_id(self) -> tuple[int, list[str]]:
        mission_id = self._mission.id
        var_stmts = [stmt for stmt in self._structure['ACTIONS'] if stmt.is_initialize_var]

        if len(var_stmts) == 0: return (mission_id, [])

        if self._mission.is_controller:
            for stmt in self._structure['CONDITIONS']:
                if stmt.is_check_mission_state and stmt.is_successfully_completed:
                    assert mission_id == self._mission.id, f'Var source is ambiguous: Mission {self._mission.id}, Procedure {self._procedure}, Step {self._step}'
                    mission_id = stmt.mission_id
        
        return (mission_id, [stmt.name for stmt in var_stmts])

    
    def eval_stmts(self, element: list[ElementTree.Element]):
        assert len(element) == 1
        element = element[0]
        stmts = []

        # TODO: assert len(element.findall('GROUP')) <= 1
        
        for stmt in element.iter('STMT'):
            stmt_class = Stmt.find_stmt_class(stmt)
            stmts.append(stmt_class(stmt))
        
        return stmts
    
    def read(self) -> list[str]:
        lines = [f'TRIGGER Step {self._step}']
        for key, stmts in self._structure.items():
            lines += [key]
            for stmt in stmts:
                lines += stmt.read()
        return lines
    
    def read_debug(self) -> list[str]:
        lines = [f'TRIGGER Step {self._step}']
        for key, stmts in self._structure.items():
            lines += [key]
            for stmt in stmts:
                stmt_lines = stmt.read_debug()
                lines += ['  -> ' + line for line in stmt_lines]
        return lines