from typing import *
from songModel import *
from stateModel import *

class Playlist:
    def __init__(self, playlist_name : str, playlist_id : str, playlist_tracks : List[Song], playlist_states : List[State], playlist_description : str):
        self.name = playlist_name
        self.id = playlist_id
        self.tracks = playlist_tracks
        self.states = playlist_states
        # does this need to be set to True by default? Maybe
        self.updated : bool = True
        self.description = playlist_description
        
    def add_song(self, song: Song):
        self.tracks.append(song)
        
    def remove_song(self, song: Song):
        if song in set(self.tracks):
            self.tracks.remove(song)
    
    def add_state(self, state: State):
        self.states.append(state)
        
    def display_info(self):
        print(f"Playlist Name: {self.name}")
        print(f"Playlist Description: {self.description}")
        
        print("Songs:")
        print("States:")