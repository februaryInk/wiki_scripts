'''
Classes that interpret missions from their XML.

-> DELIVER MISSION: rtlm, rtl, stlm, stl - time limits?
-> CHECK VAR: compare 3 is "equal to"? ref is value to check?
ON SENDGIFT END: When given special item.
SET SPECIAL GIFT RULE STATE: AssetSpecialGiftRuleSpecialGiftRule
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.lib.asset               import Asset
from sandrock.structures.conversation import *

import urllib.parse

# -- Private -------------------------------------------------------------------

def _recursive_unquote(element: ElementTree.Element) -> None:
    for k, v in element.attrib.items():
        if v and isinstance(v, str) and '%' in v:
            element.attrib[k] = urllib.parse.unquote(v)
    for child in element:
        _recursive_unquote(child)

# -- STMT Classes --------------------------------------------------------------

class _Stmt:
    _stmt_matches: list[str] = []

    @classmethod
    def find_stmt_class(cls, stmt: ElementTree.Element) -> Type[_Stmt]:
        for stmt_class in _Stmt.__subclasses__():
            if stmt_class.is_type_match(stmt):
                return stmt_class
        
        return cls

    @classmethod
    def is_type_match(cls, stmt: ElementTree.Element) -> bool:
        val = stmt.get('stmt')
        return val in cls._stmt_matches

    def __init__(self, stmt: ElementTree.Element):
        self._stmt: ElementTree.Element = stmt
        self.extract_properties()
    
    @property
    def stmt(self) -> str:
        return self._stmt.get('stmt')
    
    def extract_properties(self) -> None:
        pass
    
    def read(self) -> list[str]:
        return self.read_debug()
    
    def read_debug(self) -> list[str]:
        attribs = ' | '.join([f'{k}: {v}' for k, v in self._stmt.attrib.items() if k not in ['identity', 'stmt']])
        return [f'{self.stmt} || {attribs}']

class _StmtMissionProgress(_Stmt):
    _stmt_matches = [
        'MISSION BEGIN',
        'DELIVER MISSION',
        'START MISSION',
        'ON ACCEPT MISSION',
        'RUN MISSION',
        'ACTION MISSION TRACE',
        'SUBMIT MISSION',
        'END MISSION',
        'MISSION END BEFORE' # Mission timeout?
    ]

    def extract_properties(self) -> None:
        self._mission_id: int = self._stmt.get('missionId')

    def read_debug(self) -> list[str]:
        return [f'{self.stmt} {self._mission_id}']

class _StmtQuiet(_Stmt):
    _stmt_matches = [
        'CAMERA NATURAL SET',
        'CAMERA PATH START',
        'CAMERA PATH STOP',
        'NPC REMOVE IDLE'
    ]

    def read_debug(self) -> list[str]:
        return []
    
class _StmtActorShowBubble(_Stmt):
    _stmt_matches = [
        'SHOW ACTOR BUBBLE'
    ]

    def extract_properties(self) -> None:
        self._text_id = self._stmt.get('transId')
        self._npc_id = self._stmt.get('npc')
        self._bubble = Bubble(self._npc_id, self._text_id)
    
    def read(self) -> list[str]:
        return ['In a speech bubble:'] + self._bubble.read()
    
    def read_debug(self) -> list[str]:
        return self._bubble.read_debug()

# Choice with the given index is made in response to conversation segment with
# given ID.
class _StmtOnConversationChoiceMade(_Stmt):
    _stmt_matches = [
        'ON CONVERSATION CHOICE MADE'
    ]

    def extract_properties(self) -> None:
        # cId?
        self._conv_choice_index = self._stmt.get('selectIndex')
        self._conv_segment_id = self._stmt.get('id')
    
    def read_debug(self) -> list[str]:
        return [f'{self.stmt} for ConvSegment {self._conv_segment_id}: {self._conv_choice_index}']

# Conversation in previous step finishes, regardless of outcome.
class _StmtOnConversationEnd(_Stmt):
    _stmt_matches = [
        'ON CONVERSATION END'
    ]

class _StmtShowConversation(_Stmt):
    _stmt_matches = [
        'SHOW CONVERSATION'
    ]
    
    def build_conversation(self, id_str: str) -> ConvSegment | ConvTalk:
        print(self._dialogue_ids)
        if '_' in id_str:
            id = int(id_str.split('_', 1)[0])
            return ConvTalk(id)
        else:
            return ConvSegment(int(id_str))
    
    def extract_properties(self) -> None:
        self._dialogue_ids: list[str] = self._stmt.get('dialog').split(',')
        self._conversation: list[ConvSegment | ConvTalk] = [self.build_conversation(id) for id in self._dialogue_ids]

    def read(self) -> list[str]:
        lines = []
        for conv in self._conversation:
            lines += conv.read()
        return lines
    
    def read_debug(self):
        return [f'{self.stmt} {", ".join([str(conv.id) for conv in self._conversation])}']

class _StmtUpdateMissionInfo(_Stmt):
    _stmt_matches = [
        'UPDATE MISSION INFO'
    ]

    def extract_properties(self) -> None:
        self._desc       = int(self._stmt.get('desc'))
        self._mission_id = int(self._stmt.get('missionId'))
        self._npc        = int(self._stmt.get('npc'))
        self._req_target = self._stmt.get('reqTarget')
        self._target_id  = int(self._stmt.get('targetId'))
        self._title      = int(self._stmt.get('title'))
        self._type       = int(self._stmt.get('type'))
    
    @property
    def description(self) -> str:
        return text(self._desc)

    @property
    def npc(self) -> str:
        if self._npc != 0:
            return text.npc(self._npc)
        
    @property
    def required(self) -> tuple[str, int]:
        if self._type == 1: # Items
            req_targets = [tar.split('_') for tar in self._req_target.split(',')]
            return [(text.item(int(item_id), config.wiki_language), int(count)) for (item_id, count) in req_targets]
        elif self._type == 4: # Go to scene
            scene_sys_name, scene_name_id = self._req_target.split(',')
            return [(scene_sys_name, int(scene_name_id))]
    
    @property
    def title(self) -> str:
        return text(self._title)
    
    def read(self) -> list[str]:
        lines = ['{{mission_details', f'|desc = {self.description}', f'|details = {self.title}']
        if self._type == 1:
            for item_name, count in self.required:
                lines += [f'*{{{{i2|{item_name}|0/{count}}}}}']
        if self.npc:
            lines += [f'*{{{{i2|{self.npc}|0/1}}}}']
        lines += ['}}']
        return lines

# ------------------------------------------------------------------------------

# properties: description_id|npc_id|opening_conversation_id?|??
class _Mission:
    def __init__(self, story: Story, asset: Asset):
        self._asset: Asset             = asset
        self.story: Story              = story 
        self.root: ElementTree.Element = asset.read_xml()

        _recursive_unquote(self.root)
    
    @property
    def children(self):
        return self.story.get_children_for(self.id)
    
    @property
    def continuations(self):
        if self.name:
            return [child for child in self.children if not child.name]
        return []
    
    @property
    def id(self) -> int:
        return int(self.root.get('id'))
    
    @property
    def is_main(self) -> bool:
        return self.root.get('isMain').lower == 'true'
    
    @property
    def name(self) -> str:
        return text(int(self.root.get('nameId')))
    
    @property
    def parents(self):
        pass
    
    def get_children_ids(self) -> list[int]:
        children_ids = []
        for stmt in self.root.iter('STMT'):
            if stmt.get('stmt') == 'RUN MISSION':
                children_ids.append(int(stmt.get('missionId')))
        return children_ids
    
    def parse(self) -> dict:
        json = {}
        for trigger in self.root.findall('TRIGGER'):
            procedure = int(trigger.get('procedure'))
            step      = float(trigger.get('step'))

            if procedure not in json: json[procedure] = {}
            if step in json[procedure]:
                print(f'Repeat of Procedure {procedure}, Step {step}')
                json[procedure][step].append(_Trigger(trigger))
            else:
                json[procedure][step] = [_Trigger(trigger)]
        
        json = {k: dict(sorted(steps.items())) for k, steps in json.items()}
        json = dict(sorted(json.items()))
        return json

    def read(self) -> None:
        lines = [f'Reading Mission {self.id}: {self.name}']
        lines += ['']
        for procedure, steps in self.parse().items():
            lines += [f'Reading Procedure {procedure}']
            lines += ['---------------------------------------------------------']
            for step, triggers in steps.items():
                for trigger in triggers:
                    lines += trigger.read()
                    lines += ['']
            lines += ['']
        return lines
    
    def read_debug(self) -> list[str]:
        lines = [f'Reading Mission {self.id}: {self.name}']
        lines += ['']
        for procedure, steps in self.parse().items():
            lines += [f'Reading Procedure {procedure}']
            lines += ['---------------------------------------------------------']
            for step, triggers in steps.items():
                for trigger in triggers:
                    lines += trigger.read_debug()
                    lines += ['']
            lines += ['']
        return lines
    
    def print(self) -> None:
        lines = self.read()
        print('\n'.join(lines))

    def print_debug(self) -> None:
        lines = self.read_debug()
        print('\n'.join(lines))

class _Trigger:
    def __init__(self, trigger: ElementTree.Element):
        self._trigger   = trigger
        self._procedure = self._trigger.get('procedure')
        self._step      = self._trigger.get('step')

        self._structure = {
            'EVENTS': self.eval_stmts(trigger.findall('EVENTS')),
            'CONDITIONS': self.eval_stmts(trigger.findall('CONDITIONS')),
            'ACTIONS': self.eval_stmts(trigger.findall('ACTIONS'))
        }
    
    def eval_stmts(self, element: list[ElementTree.Element]):
        assert len(element) == 1
        element = element[0]
        stmts = []

        assert len(element.findall('GROUP')) <= 1
        
        for stmt in element.iter('STMT'):
            stmt_class = _Stmt.find_stmt_class(stmt)
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

class Story:
    def __init__(self):
        self.bundle            = Bundle('story_script')
        self.missions          = {}
        self.mission_parentage = {}

        for asset in self.bundle.assets:
            if asset.type == 'TextAsset':
                mission                            = _Mission(self, asset)
                self.missions[mission.id]          = mission
                self.mission_parentage[mission.id] = mission.get_children_ids()
    
    def get_children_for(self, id: int) -> list[_Mission]:
        assert id in self.missions
        assert id in self.mission_parentage
        child_missions = [self.get_mission(child_id) for child_id in self.mission_parentage[id]]
        return child_missions

    def get_mission(self, id: int) -> _Mission:
        return self.missions[id]
    
    def get_mission_names(self) -> dict[int, str]:
        name_dict = {mission.id: mission.name for mission in self._missions}
        return dict(sorted(name_dict.items()))
