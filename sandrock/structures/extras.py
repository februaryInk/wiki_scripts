'''
Parses an assortment of unrelated data structures into reusable 
objects.

  - Newspaper articles
'''

from __future__ import annotations

from sandrock import *

# ------------------------------------------------------------------------------

# {
#   'id': 1089,
#   'type': 1,
#   'titleId': 80021753,
#   'supplement': 0,
#   'contentId': 80021754,
#   'layouts': [
#     0,
#     1,
#     2,
#     4
#   ],
#   'timeOfDuration': -1,
#   'texturePathCN': '',
#   'texturePathEN': '',
#   'pictureShowType': 0,
#   'pictureShowPosition': 0,
#   'missionIdAdd': -1,
#   'missionIdRemove': -1
# }

class NewspaperContent:
    types = {
        1: 'Article',
        6: 'Picture'
    }

    def __init__(self, id: int) -> None:
        self.id:   int = id
        self._data: dict = DesignerConfig.NewspaperContent[id]

    @cached_property
    def content(self) -> str:
        content_id = self._data['contentId']
        if content_id > 0: return text(content_id)
    
    @cached_property
    def image(self) -> str:
        image_filename = self._data['texturePathEN']
        if image_filename: return image_filename

    @cached_property
    def mission_add_id(self) -> int:
        mission_id = self._data['missionIdAdd']
        if mission_id > 0: return mission_id

    @cached_property
    def mission_remove_id(self) -> int:
        mission_id = self._data['missionIdRemove']
        if mission_id > 0: return mission_id

    @cached_property
    def title(self) -> str:
        title_id = self._data['titleId']
        if title_id > 0: return text(title_id)

    @cached_property
    def type(self) -> str:
        return NewspaperContent.types.get(self._data['type'], 'Unknown')

    def read(self) -> None:
        lines = [
            f'Newspaper adds {self.type} content {self.id}.',
        ]

        if self.mission_add_id:
            lines.append(f'Mission Add ID: {self.mission_add_id}')

        if self.mission_remove_id:
            lines.append(f'Mission Remove ID: {self.mission_remove_id}')
        
        if self.title:
            lines.append(f'Title: {self.title}')

        if self.content:
            lines.append(self.content)

        if self.image:
            lines.append(f'Image: {self.image}')

        return lines
