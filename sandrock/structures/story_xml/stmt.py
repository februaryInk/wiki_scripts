'''
Classes for handling the many types of STMTs in the story scripts. A STMT can be
listening for an event, checking for a condition, or performing an action. In
these classes, we check what the STMT is doing and try to print it in a more 
human-readable form.

-> DELIVER MISSION: rtlm, rtl, stlm, stl - time limits?
-> CHECK VAR: compare 3 is "equal to"? ref is value to check?
ON SENDGIFT END: When given special item.
SET SPECIAL GIFT RULE STATE: AssetSpecialGiftRuleSpecialGiftRule
CHECK MISSION CURRENT STATE: state - 1 = not started, 2 = in progress, 3 = complete? 4? flag = 0 or 1

Seems like: Increase var by 1 6 days in a row.
<TRIGGER name="%E5%A6%AE%E9%9B%85%E5%A4%A9%E6%95%B0" repeat="6" procedure="2" step="1">
<STMT stmt="SET VAR" scope="2" name="NIASEED" set="1" value="1" identity="" />

# Successful mission completion:
# stmt="CHECK MISSION CURRENT STATE" missionId="1600122" state="3" flag="1"
'''

from __future__ import annotations

from sandrock                         import *
from sandrock.lib.asset               import Asset
from sandrock.structures.conversation import *

import urllib.parse

if TYPE_CHECKING:
    from sandrock.structures.story import Mission

# -- Private -------------------------------------------------------------------

_compare_map = {
    2: '>=',
    3: '==',
    4: '<= (maybe?)',
    5: '> (maybe?)',
    6: '<'
}

_weather_map = {
    1: 'Rainy',
}

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

    def __init__(self, stmt: ElementTree.Element, group_index: int | None, mission: Mission):
        self.group_index = group_index
        self._mission = mission
        self._stmt: ElementTree.Element = stmt
        self.extract_properties()
    
    @property
    def is_always(self) -> bool:
        return False
    
    @property
    def is_blueprint_unlock(self) -> bool:
        return False
    
    @property
    def is_conversation_choice_made(self) -> bool:
        return False
    
    @property
    def is_conversation_end(self) -> bool:
        return False
    
    @property
    def is_conversation_start(self) -> bool:
        return False
    
    @property
    def is_conversation_segment_end(self) -> bool:
        return False
    
    @property
    def is_every_day(self) -> bool:
        return False
    
    @property
    def is_npc_change_favor(self) -> bool:
        return False
    
    @property
    def is_npc_send_gift(self) -> bool:
        return False
    
    @property
    def is_quiet(self) -> bool:
        return False
    
    @property
    def is_receive_item(self) -> bool:
        return False
    
    def is_run_mission(self, mission_id: int = None) -> bool:
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

    def read_default(self) -> list[str]:
        attribs = ' | '.join([f'{k}: {v}' for k, v in self._stmt.attrib.items() if k not in ['identity', 'stmt']])
        return [f'{self.stmt} || {attribs}']
    
    # Override.
    def read(self) -> list[str]:
        return self.read_default()
    
    # Do not override.
    def read_debug(self) -> list[str]:
        default = self.read_default()
        actual  = self.read()

        if actual == default:
            return default
        else:
            return default + [''] + actual

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
        self.count: int       = int(self._stmt.get('count') or self._stmt.get('itemCount'))
        self._item_grade: int = int(self._stmt.get('itemGrade'))
        self.item_id: int     = int(self._stmt.get('item') or self._stmt.get('itemId'))
        self._show_tips: int  = int(self._stmt.get('showTips') or self._stmt.get('itemShowTip'))
    
    @property
    def is_receive_item(self) -> bool:
        # If the game isn't letting the player know they got an item, we don't
        # need to report it as an item source, right?
        # Answer: Actually, there are times when this is important, such as when 
        # a mission is giving the player a recipe book silently in order to 
        # unlock an item for crafting. There are failsafe items too, like the
        # Filter Core 19810073 in mission 1200128.
        if self._add_remove == 0: # and self._show_tips == 1:
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

# Checks that an event script has played out, since event scripts do not have 
# states in the same way that missions do.
class _StmtCheckEndScript(Stmt):
    _stmt_matches = [
        'CHECK END SCRIPT'
    ]

    def extract_properties(self) -> None:
        self.flag: int       = int(self._stmt.get('flag'))
        self.mission_id: int = int(self._stmt.get('missionId'))
        self.result: int     = int(self._stmt.get('result'))
    
    @property
    def mission_name(self) -> str:
        return self._mission.story.get_mission_name(self.mission_id)

    def read(self) -> list[str]:
        return [f'Check if mission {self.mission_name or self.mission_id} is result {self.result} flag {self.flag}']

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
    
    @property
    def mission_name(self) -> str:
        return self._mission.story.get_mission_name(self.mission_id)
    
    def read(self) -> list[str]:
        if self.is_successfully_completed:
            return [f'{self.mission_name} is successfully completed']
        elif self.is_failed:
            return [f'{self.mission_name} has failed']
        else:
            return [f'{self.mission_name} is in state {self._state} with flag {self._flag}']

class _StmtCheckNpcLeaveTown(Stmt):
    _stmt_matches = [
        'CHECK NPC LEAVE TOWN'
    ]

    def extract_properties(self) -> None:
        self.flag: int       = int(self._stmt.get('flag'))
        self.npc_id: int = int(self._stmt.get('npc'))
    
    @property
    def checking_for(self) -> str:
        if self.flag == 1:
            return 'has left town'
        elif self.flag == 0:
            return 'is in town'
        else:
            return f'unknown flag {self.flag}'

    def read(self) -> list[str]:
        return [f'Check if {text.npc(self.npc_id)} {self.checking_for}']

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
        return [f'Check relationship with {text.npc(self.npc)} is {self.level}']

class _StmtCheckVar(Stmt):
    _stmt_matches = [
        'CHECK VAR'
    ]

    def extract_properties(self) -> None:
        self._compare: int = int(self._stmt.get('compare'))
        self.name: str     = self._stmt.get('name')
        self._ref: str     = self._stmt.get('ref')
    
    @property
    def compare(self) -> str:
        return _compare_map[self._compare]
    
    @property
    def is_check_var(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        return [f'Check if {self.name} is {self.compare} {self._ref}']

class _StmtGlobalBlackBoardSet(Stmt):
    _stmt_matches = [
        'GLOBAL BLACK BOARD SET'
    ]

    def extract_properties(self) -> None:
        self.key: str  = self._stmt.get('key')
        self.info: str = self._stmt.get('info')
    
    @property
    def event_talks(self) -> list[EventTalk]:
        return EventTalk.global_str_talks(self.key)
    
    def read(self) -> list[str]:
        lines = [f'Set global blackboard key {self.key} with info {self.info}.']

        if self.event_talks:
            lines += ['Townsfolk respond to the event:', '']
            for talk in self.event_talks:
                lines += talk.read()
                lines += ['']
        
        return lines


class _StmtMissionProgress(Stmt):
    _stmt_matches = [
        'MISSION BEGIN',
        'DELIVER MISSION',
        'START MISSION',
        'ON ACCEPT MISSION',
        'ACTION MISSION TRACE',
        'SUBMIT MISSION',
        'END MISSION',
        'MISSION END BEFORE' # Mission timeout?
    ]

    def extract_properties(self) -> None:
        self._mission_id: int = self._stmt.get('missionId')

    def read(self) -> list[str]:
        return [f'{self.stmt} {self._mission_id}']

class _StmtNpcAddIdle(Stmt):
    _stmt_matches = [
        'NPC ADD IDLE',
        'NPC ADD IDLE 2',
    ]

    def extract_properties(self) -> None:
        self._flag_name: str      = self._stmt.get('flagName')
        self._look_at_npc_id: int = int(self._stmt.get('lookAtActor', '-1'))
        self._npc_id: int         = int(self._stmt.get('npc'))
        self._order: int          = int(self._stmt.get('order', '-1'))
        self._scene_name: str     = self._stmt.get('sceneName')
    
    @property
    def look_at_npc(self) -> str:
        if self._look_at_npc_id > 0:
            return text.npc(self._look_at_npc_id)
    
    def read(self) -> list[str]:
        line = f'{text.npc(self._npc_id)} idles in {self._scene_name}'
        if self.look_at_npc:
            line += f' and looks at {self.look_at_npc}'
        
        return [line]

class _StmtNpcChangeFavor(Stmt):
    _stmt_matches = [
        'NPC CHANGE FAVOR'
    ]

    def extract_properties(self) -> None:
        self.favor: int   = int(self._stmt.get('changeFavor'))
        self.npc_id: int = int(self._stmt.get('npc'))
    
    @property
    def is_npc_change_favor(self) -> bool:
        return True
    
    @property
    def npc(self) -> str:
        return text.npc(self.npc_id)
    
    def read(self) -> list[str]:
        return [f'{self.npc} gains {self.favor} favor']

class _StmtOnEveryDayStart(Stmt):
    _stmt_matches = [
        'ON EVERY DAY START'
    ]

    @property
    def is_every_day(self) -> bool:
        return True

    def read(self):
        return ['At the beginning of the day:']

class _StmtQuiet(Stmt):
    _stmt_matches = [
        'CAMERA NATURAL SET',
        'CAMERA PATH START',
        'CAMERA PATH STOP',
        'NPC CREATE SET POS ROT FLAG'
    ]

    @property
    def is_quiet(self) -> bool:
        return True

    def read(self) -> list[str]:
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

class _StmtNpcSendGift(Stmt):
    _stmt_matches = [
        'ACTION NPC SEND GIFT'
    ]

    def extract_properties(self) -> None:
        self._duration_hour: int = int(self._stmt.get('druationHour'))
        self.gift_id: int        = int(self._stmt.get('giftId'))
        self.npc_id: int         = int(self._stmt.get('npc'))
        self._scene_pos: str     = self._stmt.get('scenePos')
    
    @property
    def is_npc_send_gift(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        return [f'{text.npc(self.npc_id)} leaves a gift: {self.gift_id}']

# Choice with the given index is made in response to conversation segment with
# given ID, during conversation with given cId.
class _StmtOnConversationChoiceMade(Stmt):
    _stmt_matches = [
        'ON CONVERSATION CHOICE MADE'
    ]

    def extract_properties(self) -> None:
        self._c_id: int             = int(self._stmt.get('cId'))
        self.conv_choice_index: int = int(self._stmt.get('selectIndex'))
        self.conv_segment_id: int   = int(self._stmt.get('id'))
    
    @property
    def conv_segment(self) -> ConvSegment:
        return ConvSegment(self.conv_segment_id)
    
    @property
    def is_conversation_choice_made(self) -> bool:
        return True
    
    @property
    def option_id(self) -> str:
        return f'{self.conv_segment_id}_{self.conv_choice_index}'
    
    def read(self) -> list[str]:
        lines = [f'The player chooses option index {self.conv_choice_index} for conversation choice (id {self.conv_segment_id}):']
        lines += self.conv_segment.read()

        return lines

# Conversation with cId finishes, regardless of outcome.
class _StmtOnConversationEnd(Stmt):
    _stmt_matches = [
        'ON CONVERSATION END'
    ]

    def extract_properties(self) -> None:
        self.c_id: int       = int(self._stmt.get('cId'))
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
        self.c_id: int        = int(self._stmt.get('cId'))
        self.segment_id: int  = int(self._stmt.get('id'))
        self._mission_id: int = int(self._stmt.get('missionId'))
        self.npc: int         = int(self._stmt.get('npc'))
        self._order: int      = int(self._stmt.get('order'))
    
    @property
    def conv_segment(self) -> ConvSegment:
        return ConvSegment(self.segment_id)
    
    @property
    def is_conversation_end(self) -> bool:
        return True
    
    @property
    def is_conversation_segment_end(self) -> bool:
        return True
    
    def read(self) -> list[str]:
        lines = [f'There is a conversation segment (id {self.segment_id}) that ends:']
        lines += self.conv_segment.read()
        return lines

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

class _StmtOnSceneChange(Stmt):
    _stmt_matches = [
        'ON SCENE CHANGE END',
        'ON SCENE CHANGE POST',
        'ON SCENE CHANGE START',
    ]

    def extract_properties(self) -> None:
        self._from_scene = self._stmt.get('fromScene')
        self._to_scene   = self._stmt.get('toScene')
    
    def read(self) -> list[str]:
        return [f'When the player moves from {self._from_scene} to the {self._to_scene}:']

class _StmtRunMission(Stmt):
    _stmt_matches = [
        'RUN MISSION'
    ]

    def extract_properties(self) -> None:
        self.mission_id = int(self._stmt.get('missionId'))

    @property
    def mission_name(self) -> str:
        name = self._mission.story.get_mission_name(self.mission_id)
        if not name: name = f'#{self.mission_id}'
        return name
    
    def is_run_mission(self, mission_id: int = None) -> bool:
        if mission_id:
            return self.mission_id == mission_id
        else:
            return True
    
    def read(self) -> list[str]:
        return [f'Run mission {self.mission_name}']

class _StmtSendMail(Stmt):
    _stmt_matches = [
        'MAIL SEND TO BOX'
    ]

    def extract_properties(self) -> None:
        self.mail_id = int(self._stmt.get('mailId'))
    
    @property
    def is_mail_delivery(self) -> bool:
        return True

    def read(self) -> list[str]:
        return ['The player receives a letter:', f'{{{{mail|{self.mail_id}}}}}']

class _StmtSetSpecialGiftRuleState(Stmt):
    _stmt_matches = [
        'SET SPECIAL GIFT RULE STATE'
    ]

    def extract_properties(self) -> None:
        self._rule_id: int = int(self._stmt.get('ruleID'))
        self._state: int   = int(self._stmt.get('state'))
    
    @property
    def item(self) -> str:
        return text.item(self.special_gift_rule['itemId'])
    
    @property
    def npc(self) -> str:
        return text.npc(self.special_gift_rule['npcID'])
    
    @cached_property
    def special_gift_rule(self) -> dict:
        return DesignerConfig.SpecialGiftRule[self._rule_id]
    
    def read_bad_reply(self) -> list[str]:
        bad_reply_texts = self.special_gift_rule['badReplyText'].split(',')
        lines = []

        if bad_reply_texts == ['NULL']: return lines

        for segment_id in bad_reply_texts:
            conv_segment = ConvSegment(int(segment_id))
            lines += conv_segment.read()
        
        return lines
    
    def read_items_with_tag(self, tag) -> list[str]:
        item_data = sorted(DesignerConfig.ItemPrototype, key=lambda item: item['id'])
        items = [item for item in item_data if tag in item['itemTag']]
        return [f'{text.item(item["id"])}' for item in items]
    
    def read_normal_reply(self) -> list[str]:
        normal_reply_texts = self.special_gift_rule['normalReplyText'].split(',')
        lines = []

        if normal_reply_texts == ['NULL']: return lines

        for segment_id in normal_reply_texts:
            conv_segment = ConvSegment(int(segment_id))
            lines += conv_segment.read()
        
        return lines
    
    def read_special_results(self) -> list[str]:
        special_results = self.special_gift_rule['specialResults']
        lines = []

        for i, result in enumerate(special_results):
            lines += [f'Special result {i + 1}, type {result["resultType"]}:']
            reply_texts = result['replyText'].split(',')
            for segment_id in reply_texts:
                conv_segment = ConvSegment(int(segment_id))
                lines += conv_segment.read()
            lines += ['Applied to the following items:']
            for tag in result['itemTags']:
                lines += [f'With tag {tag}:']
                lines += self.read_items_with_tag(tag)
        
        return lines
    
    def read(self) -> list[str]:
        if self._state == 1:
            lines = [f'Special gift rule {self._rule_id} is set for giving {self.npc} {self.item}:']
        else:
            lines = [f'The special gift rule {self._rule_id} for giving {self.item} to {self.npc} is disabled. The rule was:']

        bad_reply = self.read_bad_reply()
        if bad_reply:
            lines += ['The gift is rejected with:']
            lines += bad_reply
            lines += ['']
        
        normal_reply = self.read_normal_reply()
        if normal_reply:
            lines += ['The gift is accepted with:']
            lines += normal_reply
            lines += ['']

        special_results = self.read_special_results()
        if special_results:
            lines += ['Special results:']
            lines += special_results
        
        return lines
        

class _StmtSetVar(Stmt):
    _stmt_matches = [
        'SET VAR'
    ]

    def extract_properties(self) -> None:
        self.name: str   = self._stmt.get('name')
        self._scope: int = int(self._stmt.get('scope'))
        self._set: int   = int(self._stmt.get('set'))
        self.value: int  = int(self._stmt.get('value'))
    
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
        return [f'{self.action} {self.name} to {self.value}']

class _StmtShowConversation(Stmt):
    _stmt_matches = [
        'SHOW CONVERSATION',
        'SHOW CONVERSATION CACHED'
    ]

    @property
    def is_conversation_start(self) -> bool:
        return True
    
    def build_conversation(self, id_str: str) -> ConvSegment | ConvBuilder:
        if '_' in id_str:
            id = int(id_str.split('_', 1)[0])
            return ConvBuilder(id, self._mission.get_conversation_modifiers())
        else:
            return ConvSegment(int(id_str))
    
    def extract_properties(self) -> None:
        self.c_id: int                = int(self._stmt.get('cId'))
        self._dialogue_ids: list[str] = self._stmt.get('dialog').split(',')
        self._conversation: list[ConvSegment | ConvBuilder] = []

    def read(self) -> list[str]:
        self._conversation = [self.build_conversation(id_str) for id_str in self._dialogue_ids]
        lines              = []

        for conv in self._conversation:
            lines += conv.read()

        return lines

class _StmtStartInteractive(Stmt):
    _stmt_matches = [
        'START INTERACTIVE'
    ]

    _option_map = {
        0: 'hugs',
        1: 'kisses',
    }

    def extract_properties(self) -> None:
        self._inst_id: int  = int(self._stmt.get('instId'))
        self._npc_id: int   = int(self._stmt.get('protoId'))
        self.option_id: int = int(self._stmt.get('optionId'))
        self.type: int      = int(self._stmt.get('type'))
    
    @property
    def interaction(self) -> str:
        default = f'interacts (type {self.type}, option {self.option_id}) with'
        if type == 1:
            return self._option_map.get(self.option_id, default)
        
        return default
    
    @property
    def npc(self) -> str:
        return text.npc(self._npc_id)
    
    def read(self) -> list[str]:
        return [f'The player {self.interaction} {self.npc}']

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
        if self._npc > 0:
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
        lines = [
            f'==={self.title}===',
            '',
            '{{mission_details', 
            f'|desc = {self.description}', 
            f'|details = {self.title}'
        ]
        if self._type == 1:
            for item_name, count in self.required:
                lines += [f'*{{{{i2|{item_name}|0/{count}}}}}']
        if self.npc:
            lines += [f'*{{{{i2|{self.npc}|0/1}}}}']
        lines += ['}}']
        return lines

# ------------------------------------------------------------------------------
