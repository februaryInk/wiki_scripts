'''
Classes for handling the many types of STMTs in the story scripts.

-> DELIVER MISSION: rtlm, rtl, stlm, stl - time limits?
-> CHECK VAR: compare 3 is "equal to"? ref is value to check?
ON SENDGIFT END: When given special item.
SET SPECIAL GIFT RULE STATE: AssetSpecialGiftRuleSpecialGiftRule
CHECK MISSION CURRENT STATE: state - 1 = not started, 2 = in progress, 3 = complete? 4? flag = 0 or 1

Seems like: Increase var by 1 6 days in a row.
<TRIGGER name="%E5%A6%AE%E9%9B%85%E5%A4%A9%E6%95%B0" repeat="6" procedure="2" step="1">
<STMT stmt="SET VAR" scope="2" name="NIASEED" set="1" value="1" identity="" />

Compare:
    2: >=
    3: ==
    6: != ?
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.lib.asset               import Asset
from sandrock.structures.conversation import *

import urllib.parse

# -- STMT Class ----------------------------------------------------------------

class Stmt:
    _stmt_matches: list[str] = []

    @classmethod
    def find_stmt_class(cls, stmt: ElementTree.Element) -> Type[Stmt]:
        for stmt_class in Stmt.__subclasses__():
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
    def is_always(self) -> bool:
        return False
    
    @property
    def is_blueprint_unlock(self) -> bool:
        return False
    
    @property
    def is_conversation_end(self) -> bool:
        return False
    
    @property
    def is_every_day(self) -> bool:
        return False
    
    @property
    def is_npc_send_gift(self) -> bool:
        return False
    
    @property
    def is_receive_item(self) -> bool:
        return False
    
    @property
    def is_initialize_var(self) -> bool:
        return False
    
    @property
    def is_mail_delivery(self) -> bool:
        return False
    
    @property
    def is_check_mission_state(self) -> bool:
        return False
    
    @property
    def is_check_relationship_level(self) -> bool:
        return False
    
    @property
    def is_check_var(self) -> bool:
        return False
    
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

# -- STMT Types ----------------------------------------------------------------

class _StmtAlways(Stmt):
    _stmt_matches = [
        'ALWAYS'
    ]

    @property
    def is_always(self) -> bool:
        return True

    def read(self) -> list[str]:
        return ['Always:']

class _StmtBagModify(Stmt):
    _stmt_matches = [
        'BAG ADD ITEM REPLACE',
        'BAG MODIFY'
    ]

    def extract_properties(self) -> None:
        self._add_remove: int = int(self._stmt.get('addRemove', '0'))
        self._count: int      = int(self._stmt.get('count') or self._stmt.get('itemCount'))
        self._item_grade: int = int(self._stmt.get('itemGrade'))
        self.item_id: int    = int(self._stmt.get('item') or self._stmt.get('itemId'))
        self._show_tips: int  = int(self._stmt.get('showTips') or self._stmt.get('itemShowTip'))
    
    @property
    def is_receive_item(self) -> bool:
        # If the game isn't letting the player know they got an item, we don't
        # need to report it as an item source, right? Seems like it replaces
        # items sometimes, like what is happening with 19810073 in mission 
        # 1200128? Why?
        if self._add_remove == 0 and self._show_tips == 1:
            return True

class _StmtBlueprintUnlock(Stmt):
    _stmt_matches = [
        'BLUEPRINT UNLOCK',
        'BLUEPRINT UNLOCK GROUP'
    ]

    def extract_properties(self) -> None:
        self._item_id: int = int(self._stmt.get('id') or '0')
        self._item_tag: int = int(self._stmt.get('itemTag') or '0')
        self._show_tips: int = int(self._stmt.get('showTips') or '0')
    
    @property
    def is_blueprint_unlock(self) -> bool:
        return True
    
    @property
    def item_ids(self) -> list[int]:
        if self._item_id:
            return [self._item_id]
        else:
            return [item['id'] for item in DesignerConfig.ItemPrototype if self._item_tag in item['itemTag']]
    
    def read(self) -> list[str]:
        return [f'Unlock blueprint {text.item(self._blueprint_id)} with {text.item(self._book_id)}']

class _StmtCheckMissionState(Stmt):
    _stmt_matches = [
        'CHECK MISSION CURRENT STATE'
    ]

    def extract_properties(self) -> None:
        self.mission_id: int = int(self._stmt.get('missionId'))
        self._flag: int      = int(self._stmt.get('flag'))
        self._state: int     = int(self._stmt.get('state'))
    
    @property
    def is_check_mission_state(self) -> bool:
        return True
    
    @property
    def is_completed(self) -> bool:
        return self.is_successfully_completed or self.is_failed
    
    @property
    def is_failed(self) -> bool:
        # Maybe this is right?
        return self._state == 4 and self._flag == 1
    
    @property
    def is_successfully_completed(self) -> bool:
        return self._state == 3 and self._flag == 1

class _StmtCheckNpcRelationship(Stmt):
    _stmt_matches = [
        'CHECK PLAYER NPC RELATION SHIP'
    ]

    def extract_properties(self) -> None:
        self._compare: int = int(self._stmt.get('compare'))
        self.npc: int      = int(self._stmt.get('npc'))
        self._level: str   = self._stmt.get('level')
    
    @property
    def is_check_relationship_level(self) -> bool:
        return True
    
    @property
    def level(self) -> str:
        readable_level = re.sub(r'(?<=[a-z])([A-Z])', r' \1', self._level)
        if self._compare == 2:
            if self._level == 'MateUnhappy':
                return 'Married'
            else:
                return readable_level
        else:
            return f'{self._compare} {readable_level}'

    
    def read(self) -> list[str]:
        return [f'Check relationship with {text.npc(self.npc)}']

class _StmtCheckVar(Stmt):
    _stmt_matches = [
        'CHECK VAR'
    ]

    def extract_properties(self) -> None:
        self._compare: int = int(self._stmt.get('compare'))
        self.name: str     = self._stmt.get('name')
        self._ref: str     = self._stmt.get('ref')
    
    @property
    def is_check_var(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        return [f'Check if {self.name} is {self._compare} {self._ref}']

class _StmtMissionProgress(Stmt):
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

class _StmtOnEveryDayStart(Stmt):
    _stmt_matches = [
        'ON EVERY DAY START'
    ]

    @property
    def is_every_day(self) -> bool:
        return True

    def read(self):
        return 'At the beginning of the day:'

class _StmtQuiet(Stmt):
    _stmt_matches = [
        'CAMERA NATURAL SET',
        'CAMERA PATH START',
        'CAMERA PATH STOP',
        'NPC REMOVE IDLE'
    ]

    def read_debug(self) -> list[str]:
        return []
    
class _StmtActorShowBubble(Stmt):
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

class _StmtNpcSendGift(Stmt):
    _stmt_matches = [
        'ACTION NPC SEND GIFT'
    ]

    def extract_properties(self) -> None:
        self._duration_hour: int = int(self._stmt.get('druationHour'))
        self.gift_id: int        = int(self._stmt.get('giftId'))
        self.npc: int            = int(self._stmt.get('npc'))
        self._scene_pos: str     = self._stmt.get('scenePos')
    
    @property
    def is_npc_send_gift(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        return [f'{text.npc(self._npc_id)} leaves a gift: {self._gift_id}']

# Choice with the given index is made in response to conversation segment with
# given ID.
class _StmtOnConversationChoiceMade(Stmt):
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
class _StmtOnConversationEnd(Stmt):
    _stmt_matches = [
        'ON CONVERSATION END'
    ]

    def extract_properties(self) -> None:
        self._cId: int       = int(self._stmt.get('cId'))
        self.mission_id: int = int(self._stmt.get('missionId'))
        self.npc: int        = int(self._stmt.get('npc'))
        self._order: int     = int(self._stmt.get('order'))
    
    @property
    def is_conversation_end(self) -> bool:
        return True

    def read(self):
        return ['After the conversation ends:']

class _StmtOnConversationEndSegment(Stmt):
    _stmt_matches = [
        'ON CONVERSATION END SEGMENT'
    ]

    def extract_properties(self) -> None:
        self._cId: int        = int(self._stmt.get('cId'))
        self._id: int         = int(self._stmt.get('id'))
        self._mission_id: int = int(self._stmt.get('missionId'))
        self.npc: int         = int(self._stmt.get('npc'))
        self._order: int      = int(self._stmt.get('order'))
    
    @property
    def is_conversation_end(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        return [f'After ConvSegment {self._id} ends:']

class _StmtOnInteractWithNpc(Stmt):
    _stmt_matches = [
        'ON INTERACT WITH NPC'
    ]

    def extract_properties(self) -> None:
        self._npc   = int(self._stmt.get('npc'))
        self._order = int(self._stmt.get('order'))
    
    def read(self) -> list[str]:
        return [f'On speaking to {text.npc(self._npc)}']

class _StmtOnPlayerWakeUp(Stmt):
    _stmt_matches = [
        'ON PLAYER WAKE UP'
    ]

    @property
    def is_every_day(self) -> bool:
        return True

    def read(self) -> list[str]:
        return ['When the player wakes up:']

class _StmtSendMail(Stmt):
    _stmt_matches = [
        'MAIL SEND TO BOX'
    ]

    def extract_properties(self) -> None:
        self.mail_id = int(self._stmt.get('mailId'))
    
    @property
    def is_mail_delivery(self) -> bool:
        return True

class _StmtSetVar(Stmt):
    _stmt_matches = [
        'SET VAR'
    ]

    def extract_properties(self) -> None:
        self.name: str   = self._stmt.get('name')
        self._scope: int = int(self._stmt.get('scope'))
        self._set: int   = int(self._stmt.get('set'))
        self.value: int = int(self._stmt.get('value'))
    
    @property
    def action(self) -> str:
        # My best guess.
        action_map = {
            0: 'Set',
            1: 'Increment',
            2: 'Decrement',
            5: 'Modulus'
        }
        return action_map[self._set]
    
    @property
    def is_initialize_var(self) -> bool:
        return self.action == 'Set'
    
    def read(self) -> list[str]:
        return [f'Set {self._name} to {self._value}']

class _StmtShowConversation(Stmt):
    _stmt_matches = [
        'SHOW CONVERSATION',
        'SHOW CONVERSATION CACHED'
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
        self._conversation: list[ConvSegment | ConvTalk] = []

    def read(self) -> list[str]:
        self._conversation = [self.build_conversation(id_str) for id_str in self._dialogue_ids]
        lines = []
        for conv in self._conversation:
            lines += conv.read()
        return lines
    
    def read_debug(self):
        self._conversation = [self.build_conversation(id_str) for id_str in self._dialogue_ids]
        return [f'{self.stmt} {", ".join([str(conv.id) for conv in self._conversation])}']

class _StmtUpdateMissionInfo(Stmt):
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
