from typing import List, Dict, Any
from datetime import datetime

# staged change model
class StagedChange:
    def __init__(self,  id: str, type: str, playlist_id: str, state_id: str, tracks: List[Dict], name: str, description: str, image_url: str = None, timestamp: str = None):
        self.id = id
        self.type = type
        self.playlist_id = playlist_id
        self.state_id = state_id
        self.tracks = tracks
        self.name = name
        self.description = description
        self.timestamp = timestamp or datetime.now().isoformat()
        self.image_url = image_url

    # convert staged change to dictionary
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'playlist_id': self.playlist_id,
            'state_id': self.state_id,
            'tracks': self.tracks,
            'name': self.name,
            'description': self.description,
            'timestamp': self.timestamp,
            'image_url' : self.image_url
        }

    # convert dictionary to staged change object
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StagedChange':
        # if not given image
        if 'image_url' not in data:
            data['image_url'] = None
        return cls(**data)
