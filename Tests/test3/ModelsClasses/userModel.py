from typing import List, Dictionary
from playlistModel import Playlist
from songModel import *
from stateModel import *

class User:
    def __init__(self, user_id : str, user_playlists : List[Playlist]):
        self.id = user_id
        # used dict instead of list because order is not necessary and quick lookup is nice
        self.user_playlists = user_playlists 
        self.playlists :Dictionary[Playlist]     
        for p in user_playlists:
            self.playlists[p.id] = p # playlist ids with associated playlist objects   
        
    def add_playlist(self, playlist: Playlist):
        self.playlists[playlist.id] = playlist
        
    def remove_playlist(self, playlist_id: str):
        if playlist_id in self.playlists:
            del self.playlists[playlist_id]
            
    def display_info(self):
        print(f"User ID: {self.id}")
        print("Playlists:")