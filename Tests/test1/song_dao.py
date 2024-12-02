from typing import List
from sqlmodel import Session, select
from song_model import Song
from db import engine

def doa_get_all_songs() -> List[Song]:
    with Session(engine) as session:
        statement = select(Song)
        songs = session.exec(statement).all()
        return songs
    
def doa_save_songs(songs: List[Song]):
    with Session(engine) as session: 
        for song in songs:
            # Check if song already exists in the database before saving it. If not, add it. 
            existing_song = session.exec(
                select(Song).where(Song.spotify_id == song.spotify_id) 
            ).first()
            if not existing_song:
                session.add(song)
        # Save the changes to the database.
        session.commit()
        
        