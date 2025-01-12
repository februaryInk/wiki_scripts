'''
Classes that interpret missions from their XML.
'''

from __future__ import annotations

from sandrock import *
from sandrock.lib.asset import Asset
from sandrock.structures.conversation import *

# -- STMT Classes --------------------------------------------------------------

class _Stmt:
    stmt: ElementTree.Element

    def __init__(self, stmt: ElementTree.Element):
        self._stmt = stmt
        self.extract_properties()
    
    @property
    def is_notable(self) -> bool:
        return False
    
    @property
    def stmt(self) -> str:
        return self._stmt.get('stmt')
    
    def extract_properties(self) -> None:
        pass
    
    def read(self) -> list[str]:
        return [self.stmt]

class _StmtActorShowBubble(_Stmt):
    @property
    def is_notable(self) -> bool:
        return True
    
    def extract_properties(self) -> None:
        self._text_id = self._stmt.get('transId')
        self._npc_id = self._stmt.get('npc')

class _StmtOnConversationEnd(_Stmt):
    @property
    def is_notable(self):
        return True

class _StmtShowConversation(_Stmt):
    @property
    def is_notable(self):
        return True

# ------------------------------------------------------------------------------

class _Mission:
    _asset: Asset
    story: Story
    tree: ElementTree

    def __init__(self, story: Story, asset: Asset):
        self._asset = asset
        self.story  = story 
        self.tree   = asset.read_xml()
    
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
        return int(self.root.get('missionId'))
    
    @property
    def is_main(self) -> bool:
        return self.root.get('isMain').lower == 'true'
    
    @property
    def name(self) -> str:
        return text.get_text(int(self.root.get('nameId')))
    
    @property
    def parents(self):
        pass
    
    @property
    def root(self) -> ElementTree.Element:
        assert self.tree
        return self.tree.get_root()
    
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
            step      = int(trigger.get('step'))

            if procedure not in json: json[procedure] = {}
            assert step not in json[procedure]
            json[procedure][step] = {
                'events': [],
                'conditions': [],
                'actions': []
            }

            events = trigger.findall('EVENT')
            assert len(events) == 1
            for event in trigger.findall('EVENT'):
                for stmt in event.findall('STMT'):
                    val = stmt.get('stmt')
                    json[procedure][step]['events'] += self.parse_event(stmt)

    def read_dialogue(self) -> None:
        pass

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
