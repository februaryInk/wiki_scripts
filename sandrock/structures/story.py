'''
Classes that interpret missions from their XML.

-> DELIVER MISSION: rtlm, rtl, stlm, stl - time limits?
-> CHECK VAR: compare 3 is "equal to"? ref is value to check?
ON SENDGIFT END: When given special item.
SET SPECIAL GIFT RULE STATE: AssetSpecialGiftRuleSpecialGiftRule
CHECK MISSION CURRENT STATE: state - 1 = not started, 2 = in progress, 3 = complete? 4? flag = 0 or 1

# Successful mission completion:
# stmt="CHECK MISSION CURRENT STATE" missionId="1600122" state="3" flag="1"

Compare:
    2: >=
    3: ==
    6: != ?
'''

from __future__ import annotations

from sandrock                              import *
from sandrock.lib.asset                    import Asset
from sandrock.structures.conversation      import *
from sandrock.structures.story_xml.stmt    import *
from sandrock.structures.story_xml.trigger import *

import urllib.parse

# -- Private -------------------------------------------------------------------

# Events don't really have official in-game names, but they have internal names
# that are recorded in Chinese in the XML. Seems like the best way to refer to
# them on the wiki is to translate these internal names.
_event_names = {
    1300026: 'Shonash Canyon Bridge Opening Ceremony',
    1500337: 'A Lifetime of Growing', # Chinese idiom "It takes a hundred years to cultivate a person"
    1600391: 'Heartbreak Drama', # Heartbroken Solo Drama
    # 1600392: 'Promise Me', # A Lonely Performance follow-up.
    1700300: 'Community Service', # Logan Promoting
    1800306: 'Follow-up Meeting',
    1700315: 'A Secret Under the Tree', # A Secret Beneath a Tree
    1800354: 'Grandma Vivi\'s Guidance', # Seeking Grandma Vivi's Guidance
    1800373: 'An Unexpected Outcome',
    1800376: "Luna's Invitation",
    1800398: 'Civil Corps Award Ceremony', # Militia Player Award
    1800484: 'End Marriage Loop',
    1900379: 'Grace\'s Return'
}

_manual_mission_names = {
    1300041: text(80001007), # In Trusses We Trust, donated gifts
    1500403: text(80031199) # The Girl with the Umbrella, Ginger's Diary Easter egg
}

_npc_mission_controllers = {
    'Amirah': 1200264,
    'Arvio': 1200107,
    'Grace': 1200133,
    'Heidi': 1200124,
    'Jane': 1200333,
    'Qi': 1200112,
    'Unsuur': 1200280,
}

_general_mission_controllers = {
    1200127: 'Nia and Mom\'s Letters',
    1200128: 'Mission Failure Follow-up',
    1200364: 'Side Mission Controller (Chapter 3)',
}

def _recursive_unquote(element: ElementTree.Element) -> None:
    for k, v in element.attrib.items():
        if v and isinstance(v, str) and '%' in v:
            element.attrib[k] = urllib.parse.unquote(v)
    for child in element:
        _recursive_unquote(child)

# ------------------------------------------------------------------------------

class Mission:
    def __init__(self, story: Story, asset: Asset):
        self._asset: Asset             = asset
        self.story: Story              = story 
        self.root: ElementTree.Element = asset.read_xml()
        self._content : dict           = None
        self._conversation_modifiers: dict = None
        self._vars_to_mission_id       = None

        _recursive_unquote(self.root)
    
    @property
    def central_npc(self):
        self.properties
    
    @property
    def children(self):
        return self.story.get_children_for(self.id)
    
    @property
    def continuations(self):
        if self.name:
            return [child for child in self.children if not child.name]
        return []
    
    @property
    def description(self) -> str:
        if len(self.properties) == 4:
            description_id = int(self.properties[0])
            if description_id != -1:
                return text(description_id)
        return ''
    
    @property
    def id(self) -> int:
        return int(self.root.get('id'))
    
    @property
    def involved_npc_ids(self) -> list[int]:
        npc_ids = set([int(elem.get('npc')) for elem in self.root.iter() if 'npc' in elem.attrib])
        return [id for id in npc_ids if id > 8000 and id < 9000]
    
    @property
    def involved_npcs(self) -> list[str]:
        return [text.npc(id) for id in self.involved_npc_ids]
    
    @property
    def is_controller(self) -> bool:
        return (
            self.id in _npc_mission_controllers.values()
            or self.id in _general_mission_controllers.keys()
            or (self.is_main and not self.name)
        )
    
    @property
    def is_event(self) -> bool:
        return self.name in _event_names.values()
    
    @property
    def is_main(self) -> bool:
        return self.root.get('isMain').lower() == 'true'
    
    @property
    def name(self) -> str:
        return self.get_name()
    
    @property
    def name_native(self) -> str:
        name_id = self.root.get('nameId')
        if name_id and name_id not in ['0', '-1']:
            name = text(int(self.root.get('nameId')))
            if name != '￥not use￥': return name
        if self.id in _event_names.keys():
            return _event_names[self.id]
        if self.id in _manual_mission_names.keys():
            return _manual_mission_names[self.id]
    
    # NPC you speak to in order to begin the mission?
    @property
    def npc(self) -> str:
        if len(self.properties) == 4:
            npc_id = int(self.properties[1])
            if npc_id not in [0, -1]:
                return text.npc(npc_id)
        return ''
    
    @property
    def parents(self):
        return self.story.get_parents_for(self.id)
    
    # properties: description_id|npc_id|opening_conversation_id?|-1 or 10&0: means what?
    @property
    def properties(self):
        return self.root.get('properties').split('|')
    
    @property
    def rewards_data(self) -> list[str]:
        if not hasattr(self, '_rewards_data'):
            self._rewards_data = next(
                (entry for entry in DesignerConfig.MissionRewards if entry.get('missionId') == self.id),
                {}
            )

        return self._rewards_data
    
    @property
    def rewards_exp(self) -> int:
        exp = self.rewards_data.get('exp', 0)
        return exp if exp else None
    
    @property
    def rewards_favor_list(self) -> list[dict[str, int]]:
        return self.rewards_data.get('favorList', [])
    
    @property
    def rewards_gols(self) -> int:
        gols = self.rewards_data.get('money', 0)
        return gols if gols else None
    
    @property
    def rewards_item_list(self) -> list[dict[str, int]]:
        return self.rewards_data.get('itemList', [])
    
    @property
    def rewards_reputation(self) -> int:
        reputation = self.rewards_data.get('reputation', 0)
        return reputation if reputation else None

    @property
    def triggers(self) -> list[Trigger]:
        triggers = []
        for procedure, steps in self.get_content().items():
            for step, step_triggers in steps.items():
                triggers += step_triggers
        return triggers
    
    @property
    def type(self) -> str:
        return 'Main' if self.is_main else 'Side'
    
    def get_children_ids(self) -> list[int]:
        children_ids = []
        for stmt in self.root.iter('STMT'):
            if stmt.get('stmt') == 'RUN MISSION':
                children_ids.append(int(stmt.get('missionId')))
        
        return children_ids
    
    def get_conversation_modifiers(self) -> list[str]:
        if not self._conversation_modifiers:
            conversation_modifiers = {
                'option': {},
                'segment': {}
            }
            for trigger in self.triggers:
                modifiers = trigger.get_conversation_modifiers()
                for event_type, modifier in modifiers.items():
                    event_type_modifiers = conversation_modifiers[event_type]
                    for id, modifiers in modifier.items():
                        if id not in event_type_modifiers:
                            event_type_modifiers[id] = set()
                        event_type_modifiers[id] |= modifiers
            self._conversation_modifiers = conversation_modifiers
        
        return self._conversation_modifiers
    
    def get_content(self) -> dict:
        if not self._content:
            content = {}
            order = defaultdict(int)

            for trigger in self.root.findall('TRIGGER'):
                procedure = float(trigger.get('procedure'))
                step      = float(trigger.get('step'))

                if procedure not in content: content[procedure] = {}
                if step in content[procedure]:
                    # print(f'Repeat of Procedure {procedure}, Step {step}')
                    content[procedure][step].append(Trigger(trigger, order[procedure], self))
                else:
                    content[procedure][step] = [Trigger(trigger, order[procedure], self)]
                order[procedure] += 1
            
            content = {k: dict(sorted(steps.items())) for k, steps in content.items()}
            content = dict(sorted(content.items()))
            self._content = content

        return self._content
    
    def get_initialized_vars_by_mission_id(self) -> dict[int, list[str]]:
        vars_by_mission_id = {}
        for trigger in self.triggers:
            mission_id, var_stmts = trigger.get_initialized_vars_by_mission_id()
            if mission_id not in vars_by_mission_id:
                vars_by_mission_id[mission_id] = []
            vars_by_mission_id[mission_id] += var_stmts
        
        return vars_by_mission_id
    
    def get_name(self, stack_level: int = 0) -> str:
        if self.name_native:
            return self.name_native
        
        # Might be too generous; we're probably getting follow-up events that
        # aren't part of the mission.
        if stack_level > 10:
            print(f'Warning: Possible looping parent-child relationship for {self.id}')
            return ''
        
        parent_name = self.parents[0].get_name(stack_level + 1) if len(self.parents) else ''
        return parent_name
    
    def get_mail_ids(self) -> list[int]:
        mail_ids_by_mission_id = {}
        for trigger in self.triggers:
            mission_id, mail_ids = trigger.get_mail_id_by_mission_id()
            if mission_id not in mail_ids_by_mission_id:
                mail_ids_by_mission_id[mission_id] = []
            mail_ids_by_mission_id[mission_id] += mail_ids
        
        return mail_ids_by_mission_id
    
    def get_received_gifts(self) -> dict[tuple, list[int]]:
        gift_ids_by_mission_id = {}
        for trigger in self.triggers:
            mission_id, gift_ids = trigger.get_received_gifts()
            if mission_id not in gift_ids_by_mission_id:
                gift_ids_by_mission_id[mission_id] = []
            gift_ids_by_mission_id[mission_id] += gift_ids
        
        return gift_ids_by_mission_id

    def get_received_item_ids(self) -> list[int]:
        item_ids_by_mission_id = {}
        for trigger in self.triggers:
            mission_id, item_ids = trigger.get_item_id_by_mission_id()
            if mission_id not in item_ids_by_mission_id:
                item_ids_by_mission_id[mission_id] = []
            item_ids_by_mission_id[mission_id] += item_ids
        
        return item_ids_by_mission_id
    
    def get_received_items(self) -> dict[tuple, list[int]]:
        items_by_causal_event = {}
        for trigger in self.triggers:
            causal_event, items = trigger.get_received_items()
            if len(items) == 0: continue
            if causal_event not in items_by_causal_event:
                items_by_causal_event[causal_event] = []
            items_by_causal_event[causal_event] += items
        
        return items_by_causal_event
    
    def get_unlocked_item_ids(self) -> list[int]:
        item_ids = []
        for trigger in self.triggers:
            item_ids += trigger.get_unlocked_item_ids()
        return item_ids
    
    def get_vars_to_mission_id(self) -> dict[str, int]:
        # All variables are set with `scope="2"`, which seems to mean that they 
        # are scoped to the script; therefore, I believe we can handle them 
        # mission by mission rather than having to consider them over the whole 
        # story. TODO: I should check this assumption later though.
        if not self._vars_to_mission_id:
            vars_to_mission_id = {}
            for mission_id, vars in self.get_initialized_vars_by_mission_id().items():
                if mission_id != self.id:
                    for var in vars:
                        vars_to_mission_id[var] = mission_id
            self._vars_to_mission_id = vars_to_mission_id
        
        return self._vars_to_mission_id
    
    @property
    def in_mission_talks(self) -> list[dict]:
        if not hasattr(self, '_in_mission_talks'):
            in_mission_talks = []

            for talk in DesignerConfig.InMissionTalk:
                if talk.get('missionId') == self.id:
                    in_mission_talks.append(talk)
            
            self._in_mission_talks = in_mission_talks
        
        return self._in_mission_talks
    
    def read_in_mission_talk(self) -> list[str]:
        lines = []

        for talk in self.in_mission_talks:
            builder = ConvBuilder(int(talk.get('dialog')), self.get_conversation_modifiers())
            lines += builder.read()
        
        return lines
    
    def read_infobox(self) -> list[str]:
        character = ''
        if self.npc: character = f'[[{self.npc}]]'

        lines = [
            '<onlyinclude>{{Infobox mission',
            f'|name = {self.name}',
            '|image =',
            f'|description = {self.description}',
            f'|type = {self.type}',
            '|time =',
            '|location =',
            f'|characters = {character}',
            '|condition =',
            '|details =',
            f'|exp = {self.rewards_exp}',
            f'|reputation = {self.rewards_reputation}',
            f'|gols = {self.rewards_gols}'
        ]

        for i, favor in enumerate(self.rewards_favor_list):
            lines.append(f'|npc{i + 1} = {text.npc(favor["id"])}')
            lines.append(f'|rp{i + 1} = {favor["count"]}')
        
        items = [f'{{{{i2|{text.item(item["id"])}}}|{item["count"]}}}' for item in self.rewards_item_list]
        if items:
            lines.append(f'|rewards = {"".join(items)}')
            

        lines.append('}}</onlyinclude>')

        return lines
    
    def read_rewards(self) -> list[str]:
        if not self.rewards_data: return []

        lines = [
            '==Rewards==',
            '{{mission reward'
        ]

        for i, favor in enumerate(self.rewards_favor_list):
            lines.append(f'|npc{i + 1} = {text.npc(favor["id"])}')
            lines.append(f'|rp{i + 1} = {favor["count"]}')
        
        lines.append(f'|exp = {self.rewards_exp}')
        lines.append(f'|reputation = {self.rewards_reputation}')
        lines.append(f'|gols = {self.rewards_gols}')

        items = [f'{{{{i2|{text.item(item["id"])}}}|{item["count"]}}}' for item in self.rewards_item_list]
        if items:
            lines.append(f'|rewards = {"".join(items)}')
        
        lines.append('}}')

        return lines
    
    def get_run_mission_context(self, mission_id: int) -> list[Trigger]:
        if mission_id not in self.get_children_ids(): 
            raise ValueError(f'Mission {mission_id} is not a child of {self.id}')

        previous_trigger = None
        ordered_triggers = sorted(self.triggers, key=lambda x: (x.procedure, x._step))
        for trigger in ordered_triggers:
            if trigger.is_run_mission(mission_id):
                return [previous_trigger, trigger]
            previous_trigger = trigger
    
    def read_run_conditions(self) -> list[str]:
        lines = ['==Overview==']

        if not self.parents: 
            lines.append(f'Parent not found; run conditions not available.')
            return lines

        for parent in self.parents:
            if parent.name:
                lines.append(f'Run conditions from {parent.name}:')
            else:
                lines.append(f'Run conditions from parent mission: {parent.id}')
            
            lines.append('')

            context = parent.get_run_mission_context(self.id)

            for trigger in context:
                lines += trigger.read()
                lines.append('')
        
        return lines
    
    def read(self) -> list[str]:
        lines = [f'Reading Mission {self.id}: {self.name}']
        lines += ['']
        lines += self.read_infobox()
        lines += ['']

        lines += self.read_run_conditions()

        lines.append('==Conduct==')
        lines.append('')
        
        ordered_triggers = sorted(self.triggers, key=lambda x: (x.procedure, x._step))
        # Move the triggers that follow up on ended conversations to be right 
        # after their respective conversations.
        reordered_triggers = []
        for trigger in ordered_triggers:
            if trigger in reordered_triggers: continue

            started_conversation_c_id = trigger.started_conversation_c_id
            
            if started_conversation_c_id:
                reordered_triggers.append(trigger)
                for followup_trigger in ordered_triggers:
                    if followup_trigger.ended_conversation_c_id == started_conversation_c_id:
                        if followup_trigger not in reordered_triggers:
                            reordered_triggers.append(followup_trigger)
            else:
                reordered_triggers.append(trigger)
        
        for trigger in reordered_triggers:
            if trigger.is_quiet: continue
            lines += trigger.read()
            lines += ['']
        
        if self.in_mission_talks:
            lines += ['NPC in-mission talks:', '']
            lines += self.read_in_mission_talk()
            lines += ['']

        lines += self.read_rewards()
        
        return lines
    
    def print(self) -> None:
        lines = self.read()
        print('\n'.join(lines))

class Story:
    def __init__(self):
        self.bundle            = Bundle('story_script')
        self.missions          = {}
        self.mission_flags     = defaultdict(set)
        self.mission_parentage = {}
        self.mission_vars      = defaultdict(set)

        for asset in self.bundle.assets:
            if asset.type == 'TextAsset':
                mission                            = Mission(self, asset)
                self.missions[mission.id]          = mission
                self.mission_parentage[mission.id] = mission.get_children_ids()
    
    def __contains__(self, mission_id) -> bool:
        return mission_id in self.missions
    
    def __iter__(self) -> Iterator[Mission]:
        return iter(self.missions.items())
    
    def get_children_for(self, id: int) -> list[Mission]:
        assert id in self.missions
        assert id in self.mission_parentage
        child_missions = [self.get_mission(child_id) for child_id in self.mission_parentage[id]]
        return child_missions
    
    def get_parents_for(self, id: int) -> list[Mission]:
        assert id in self.missions
        parent_ids = [par_id for par_id, child_ids in self.mission_parentage.items() if id in child_ids]
        parent_missions = [self.get_mission(parent_id) for parent_id in parent_ids]
        assert len(parent_missions) or id in self.mission_parentage, f'Mission {id} has no parents and is not a parent itself.'

        return parent_missions

    def get_mission(self, id: int) -> Mission:
        return self.missions[id]
    
    def get_mission_name(self, id: int) -> str:
        return self.get_mission(id).name
    
    def get_mission_names(self) -> dict[int, str]:
        name_dict = {mission.id: mission.name for id, mission in self.missions.items()}
        return dict(sorted(name_dict.items()))
    
    def get_missions_for_npc(self, npc_name: str) -> list[Mission]:
        return [mission for id, mission in self if mission.npc == npc_name or npc_name in mission.involved_npcs]
    
    def print_mission_list_for_npc(self, npc_name: str) -> None:
        print(f'Finding missions for {npc_name}...')
        print('')
        for mission in self.get_missions_for_npc(npc_name):
            print(f'{mission.id}: {mission.name}')
            print(mission.description)
            print('')
