from typing import *
from .songModel import *
from .stateModel import *
from api import *
class Playlist:
    def __init__(self, playlist_name : str, playlist_id : str, playlist_tracks : List[Song], playlist_states : List[State], playlist_description : str, image):
        self.name = playlist_name
        self.id = playlist_id
        self.tracks = playlist_tracks
        self.states = playlist_states
        self.updated : bool = True
        self.description = playlist_description
        self.image = image  
        self.total_tracks = len(self.tracks)
    
    def to_dict(self):
        tl = []
        for track in self.tracks:
            if track:
                tl.append(track.to_dict())
        sl = []
        for state in self.states:
            if state:
                sl.append(state.to_dict())
        return {
            'id': self.id,
            'name': self.name,
            'tracks': tl,
            'states': sl,
            'description': self.description,
            'image': self.image,
            'total_tracks': self.total_tracks
        }

    @staticmethod
    def from_dict(data):
        return Playlist(
            data['name'],
            data['id'],
            [Song.from_dict(track) for track in data['tracks']],
            [State.from_dict(state) for state in data['states']],
            data['description'],
            data['image']
        )

    def add_song(self, song: Song):
        self.tracks.append(song)
        
    def remove_song(self, song: Song):
        if song in set(self.tracks):
            self.tracks.remove(song)
    
    def add_state(self, state: State):
        self.states.append(state)
        
    def display_info(self, command :int): # 
        # 0 show all info 
        # 1 show just playlist name
        # 2 show songs
        # 3 show states
        print(f"Playlist Name: {self.name}")
        # print(f"Playlist Description: {self.description}")
        
        for song in self.tracks:
            if command == 0 or command == 2:
                print(f"Song Name: ")
                song.display_info()
            else: break
        for state in self.states:
            if command == 0 or command == 3:
                print(f"States: ")
                state.display_info()
            else: break

   

def make_new_playlist(token, playlist_id):
    info = get_playlist_info(token, playlist_id)
    tracks = get_playlist_tracks(token, playlist_id)
    new_tracks= []
    for track in tracks:
        # print('Track data',track)
        if track and 'track' in track:
            t = track['track']
            new_tracks.append(make_new_song(token, t['name'], t['artists'][0]['name'], t['album']['name'], t['id']))

    new_state = make_new_state(token, playlist_id, info['description'], 0, info['images'][0]['url'], info['name'], new_tracks)

    playlist = Playlist(info['name'], info['id'], new_tracks, [new_state], info['description'], info['images'][0]['url'])
    return playlist
