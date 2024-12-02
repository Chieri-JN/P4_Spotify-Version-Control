from typing import *
from songModel import *

class State:
    def __init__(self, playlist_name : str, playlist_id : str, playlist_tracks : List[Song], playlist_description : str, state_data : str, state_id : int):
        self.name = playlist_name
        self.id = state_id  # unique identifier for this state
        self.playlist_id = playlist_id
        self.tracks = playlist_tracks
        self.description = playlist_description 
        self.data = state_data # data represemts the date and time when state was created
    
    
    def display_info(self):
        print(f"State ID: {self.id}")
        print(f"Playlist Name: {self.name}")
        print(f"Playlist Description: {self.description}")
        print(f"State Data: {self.data}")
        print("Songs:")