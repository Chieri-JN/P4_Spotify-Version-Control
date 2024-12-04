from typing import * 

class Song:
    def __init__(self, title: str, artist: str, album: str, id: str, spotify_id: str = None):
        self.title = title
        self.artist = artist
        self.album = album
        self.id = id
        
        
        
    def display_info(self) -> None:
        print(f"Title: {self.title}")
        print(f"Artist: {self.artist}")
        print(f"Album: {self.album}")
        print(f"ID: {self.id}")
        
        
        
    def to_dict(self):
        return {
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'id': self.id,
        }

    @staticmethod
    def from_dict(data):
        # Handle missing fields gracefully with default values
        return Song(
            title=data.get('title', 'Unknown Title'),
            artist=data.get('artist', 'Unknown Artist'),
            album=data.get('album', 'Unknown Album'),
            id=data.get('id', ''),
        )

def make_new_song(token, title: str, artist: str, album: str, id: str) -> Song:
    return Song(title, artist, album, id)