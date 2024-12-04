from typing import List, Dict, Any
from datetime import datetime

class StagedChange:
    def __init__(self, 
                 id: str,
                 type: str,
                 playlist_id: str,
                 state_id: str,
                 tracks: List[Dict],
                 name: str,
                 description: str,
                 timestamp: str = None):
        self.id = id
        self.type = type
        self.playlist_id = playlist_id
        self.state_id = state_id
        self.tracks = tracks
        self.name = name
        self.description = description
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'playlist_id': self.playlist_id,
            'state_id': self.state_id,
            'tracks': self.tracks,
            'name': self.name,
            'description': self.description,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StagedChange':
        return cls(**data)
