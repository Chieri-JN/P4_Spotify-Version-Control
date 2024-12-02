from typing import List, Dict, Union
from ModelsClasses import User, Playlist, Song, State
import os
import json

def view_playlist_versions(user: User, playlist_id: str) -> Union[List[Song], str]:
    pass


def restore_playlist_version(user: User, playlist_id: str, version_id: int) -> Union[Song, str]:
    pass

def clone_from_previous_version(user: User, playlist_id: str, version_id: int) -> Union[Playlist, str]:
    pass

def save_session(user: User, playlist_id: str, state: State) -> None:
    pass


