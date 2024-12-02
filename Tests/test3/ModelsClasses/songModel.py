from typing import * 

class Song:
    def __init__(self, track_title: str, track_artist: str, track_album: str, track_spotify_id: str):
        self.title = track_title
        self.artist = track_artist
        self.album = track_album
        self.spotify_id = track_spotify_id
        
        
    def display_info(self) -> None:
        print(f"Title: {self.title}")
        print(f"Artist: {self.artist}")
        print(f"Album: {self.album}")