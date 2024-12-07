from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta

from .playlistModel import *
from .songModel import *
from .stateModel import *
from api import *

# user model
class User:
    def __init__(self, user_name:str, user_id: str, user_playlists, playlist_objects):
        self.name = user_name
        self.id = user_id
        self.user_playlists = user_playlists
        self.playlist_objects = defaultdict(Playlist)
        
        if isinstance(playlist_objects, dict):
            # If playlist_objects is already a dictionary
            for pid, p in playlist_objects.items():
                if p:
                    self.playlist_objects[pid] = p
        else:
            # If playlist_objects is a list
            for p in playlist_objects:
                if p and hasattr(p, 'id'):
                    self.playlist_objects[p.id] = p
                    
        self.last_updated = datetime.now().isoformat()

    # convert user to dictionary
    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'user_playlists': self.user_playlists,
            'playlist_objects': {pid: playlist.to_dict() for pid, playlist in self.playlist_objects.items()},
            'last_updated': self.last_updated
        }

    # convert dictionary to user object
    @staticmethod
    def from_dict(data):
        # Create a dictionary of playlist objects
        playlist_objects = {
            pid: Playlist.from_dict(p) 
            for pid, p in data.get('playlist_objects', {}).items()
        }
        
        user = User(
            data.get('name', ''),
            data.get('id', ''),
            data.get('user_playlists', []),
            playlist_objects  
        )
        user.last_updated = data.get('last_updated', datetime.now().isoformat())
        return user

    def needs_refresh(self, max_age_minutes=30):
        last_updated = datetime.fromisoformat(self.last_updated)
        age = datetime.now() - last_updated
        return age > timedelta(minutes=max_age_minutes)

    def add_playlist(self, playlist: Playlist):
        self.playlist_objects[playlist.id] = playlist
        
    def remove_playlist(self, playlist_id: str):
        if playlist_id in self.playlist_objects:
            del self.playlist_objects[playlist_id]
            
    def display_info(self):
        print(f"User ID: {self.id}")
        print("Playlists:")
        print('PLAYLISTS_DICT = ', self.playlist_objects)
        print('USER PLAYLISTS: ', self.user_playlists)
        for pid, playlist in self.playlist_objects.items():
            print(f"Playlist ID: {pid}")
            playlist.display_info()
        
    

def make_new_user(token):
    try:
        # Get user playlists from Spotify API
        playlists = get_user_playlists(token)
        print(f"Retrieved {len(playlists)} playlists from Spotify")
        
        # Create playlist objects for each playlist
        playlist_objects = []
        for plist in playlists:
            if plist:
                try:
                    playlist = make_new_playlist(token, plist['id'])
                    if playlist:
                        playlist_objects.append(playlist)
                except Exception as e:
                    print(f"Error creating playlist object for {plist['id']}: {str(e)}")
        
        print(f"Created {len(playlist_objects)} playlist objects")
        
        # Get user info
        name, ID = get_user_info(token)
        print(f"Creating user {name} with ID {ID}")
        
        # Create and return user object
        user = User(name, ID, playlists, playlist_objects)
        return user
        
    except Exception as e:
        print(f"Error in make_new_user: {str(e)}")
        raise e



# function to compare the current save user state with the one pulled from spotify
def compare_playlists(current_user, new_user):
    changes = {
        'new_playlists': [],
        'deleted_playlists': [],
        'modified_playlists': []
    }
    
    # Get current and new playlist IDs
    current_playlists = {p['id']: p for p in current_user.user_playlists}
    new_playlists = {p['id']: p for p in new_user.user_playlists}
    
    # Find new and deleted playlists
    new_playlist_ids = set(new_playlists.keys()) - set(current_playlists.keys())
    deleted_playlist_ids = set(current_playlists.keys()) - set(new_playlists.keys())
    
    # Convert to Playlist objects before adding to changes
    changes['new_playlists'] = [new_user.playlist_objects[pid] for pid in new_playlist_ids if pid in new_user.playlist_objects]
    changes['deleted_playlists'] = [current_user.playlist_objects[pid] for pid in deleted_playlist_ids if pid in current_user.playlist_objects]
    
    # Check for modifications in existing playlists
    common_playlist_ids = set(current_playlists.keys()) & set(new_playlists.keys())
    
    for pid in common_playlist_ids:
        if pid in current_user.playlist_objects and pid in new_user.playlist_objects:
            current_pl = current_user.playlist_objects[pid]
            new_pl = new_user.playlist_objects[pid]
            
            # Create sets of track identifiers (using both id and title for uniqueness)
            current_tracks = {(t.id, t.title) for t in current_pl.tracks}
            new_tracks = {(t.id, t.title) for t in new_pl.tracks}
            
            # Find actual differences
            added = new_tracks - current_tracks
            removed = current_tracks - new_tracks
            
            # Only add to modified if there are actual differences
            if added or removed:
                print(f"\nAnalyzing playlist: {new_pl.name}")
                print(f"Current tracks: {len(current_tracks)}")
                print(f"New tracks: {len(new_tracks)}")
                print(f"Added: {len(added)}")
                print(f"Removed: {len(removed)}")
                
                # Only append if there are real changes
                if len(added) > 0 or len(removed) > 0:
                    changes['modified_playlists'].append({
                        'playlist': new_pl,
                        'added_tracks': [t for t in new_pl.tracks if (t.id, t.title) in added],
                        'removed_tracks': [t for t in current_pl.tracks if (t.id, t.title) in removed]
                    })
    
    print(f"\nSummary:")
    print(f"Found {len(changes['new_playlists'])} new playlists")
    print(f"Found {len(changes['deleted_playlists'])} deleted playlists")
    print(f"Found {len(changes['modified_playlists'])} modified playlists")
    
    return changes

# function to apply changes to the given user
def apply_changes(user, changes):
    print("\n=== Applying Changes ===")
    
    # Add new playlists
    for playlist in changes['new_playlists']:
        print(f"Adding new playlist: {playlist.name}")
        user.add_playlist(playlist)
        user.user_playlists.append({
            'id': playlist.id,
            'name': playlist.name,
            'images': [{'url': playlist.image}] if playlist.image else [],
            'total_tracks': len(playlist.tracks)
        })
    
    # Remove deleted playlists
    for playlist in changes['deleted_playlists']:
        print(f"Removing playlist: {playlist.id}")
        user.remove_playlist(playlist.id)
        user.user_playlists = [p for p in user.user_playlists if p['id'] != playlist.id]
    
    # Update modified playlists
    for change in changes['modified_playlists']:
        playlist = change['playlist']
        if playlist.id in user.playlist_objects:
            current_playlist = user.playlist_objects[playlist.id]
            
            # Convert all tracks to Song objects if they aren't already
            added_tracks = [Song.from_dict(t) if isinstance(t, dict) else t for t in change['added_tracks']]
            removed_tracks = [Song.from_dict(t) if isinstance(t, dict) else t for t in change['removed_tracks']]
            
            # Start with current tracks
            updated_tracks = current_playlist.tracks.copy()
            
            # Remove tracks that should be removed
            for track in removed_tracks:
                if track in updated_tracks:
                    updated_tracks.remove(track)
                    print(f"Removed track: {track.title}")
            
            # Add new tracks
            for track in added_tracks:
                updated_tracks.append(track)
                print(f"Added track: {track.title}")
            
            # Create new state with the updated tracks
            new_state = make_new_state(
                None,
                playlist_id=playlist.id,
                description=f"Updated playlist with {len(added_tracks)} new and {len(removed_tracks)} removed tracks",
                id=len(current_playlist.states),
                image_url=current_playlist.image,
                playlist_name=current_playlist.name,
                tracks=updated_tracks
            )
            print(f"Created new state #{len(current_playlist.states)} with {len(updated_tracks)} tracks")
            
            # Update playlist
            current_playlist.states.append(new_state)
            current_playlist.total_tracks = len(updated_tracks)
            current_playlist.tracks = updated_tracks
            print(f"Updated playlist {playlist.name} with new state and {len(updated_tracks)} tracks")
            
            # Verify state was added
            print(f"Playlist now has {len(current_playlist.states)} states")
            
            # Update corresponding entry in user_playlists
            for p in user.user_playlists:
                if p['id'] == playlist.id:
                    p['total_tracks'] = len(current_playlist.tracks)
                    break
    
    # Ensure user_playlists only contains playlists that exist in playlist_objects
    valid_playlist_ids = set(user.playlist_objects.keys())
    user.user_playlists = [p for p in user.user_playlists if p['id'] in valid_playlist_ids]
    
    # for debugging
    print("\n=== Final User State ===")
    print(f"Total playlists in user_playlists: {len(user.user_playlists)}")
    print(f"Total playlists in playlist_objects: {len(user.playlist_objects)}")
    print("Playlist IDs in user_playlists:", [p['id'] for p in user.user_playlists])
    print("Playlist IDs in playlist_objects:", list(user.playlist_objects.keys()))
    
    print("=== Changes Applied ===\n")
    return user
