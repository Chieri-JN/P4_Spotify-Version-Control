from typing import *
from .songModel import *
from datetime import datetime
class State:
    def __init__(self, playlist_name : str, playlist_id : str, playlist_tracks : List[Song], playlist_description : str, state_data : str, state_id : int, image_url : str):
        self.name = playlist_name
        self.id = state_id  # just the index on state list
        self.playlist_id = playlist_id
        self.tracks = playlist_tracks
        self.description = playlist_description 
        self.data = state_data # data represemts the date and time when state was created
        self.timestamp = datetime.fromisoformat(self.data).strftime("%B %d, %Y at %I:%M %p")
        self.image_url = image_url
    
    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'playlist_id': self.playlist_id,
            'tracks': [track.to_dict() for track in self.tracks],
            'description': self.description,
            'data': self.data,
            'image_url': self.image_url
        }

    @staticmethod
    def from_dict(data):
        tracks = [Song.from_dict(track) for track in data['tracks']]
        image_url = data.get('image_url', None)
        return State(
            data['name'],
            data['playlist_id'],
            tracks,
            data['description'],
            data['data'],
            data['id'],
            image_url
        )
    
    def display_info(self):
        print(f"State ID: {self.id}")
        print(f"name: {self.name}")
        print(f"Playlist Description: {self.description}")
        print(f"State Data: {self.data}")
        print("Songs:")
        
        
        
def make_new_state(token, playlist_id, description, id, image_url, playlist_name, tracks):
    return State(playlist_name, playlist_id, tracks, description, datetime.now().isoformat(), id, image_url)