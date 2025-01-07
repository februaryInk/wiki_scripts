'''
Classes that interpret missions from their XML.
'''

from __future__ import annotations

from sandrock import *
from sandrock.structures.conversation import *

# -- Private -------------------------------------------------------------------



# ------------------------------------------------------------------------------

class Mission:
    def __init__(self, story: Story, asset: Asset):
        self.story = story 
        self.tree  = asset.read_xml()
    
    @property
    def children(self):
        pass
    
    @property
    def continuations(self):
        pass
    
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
                'conditions': {},
                'dialogue': {}
            }

    def read_dialogue(self) -> None:
        pass

class Story:
    def __init__(self):
        self.bundle            = Bundle('story_script')
        self.missions          = {}
        self.mission_parentage = {}

        for asset in self.bundle.assets:
            if asset.type == 'TextAsset':
                mission                            = Mission(self, asset)
                self.missions[mission.id]          = mission
                self.mission_parentage[mission.id] = mission.get_children_ids()
    
    def get_children_for(self, id: int) -> list[Mission]:
        assert id in self.missions
        assert id in self.mission_parentage
        child_missions = [self.missions[child_id] for child_id in self.mission_parentage[id]]
        return child_missions

    def get_mission(self, id: int) -> Mission:
        return self.missions[id]
