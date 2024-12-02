import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from song_model import Song
from db import create_tables
from typing import List
from song_dao import doa_save_songs, doa_get_all_songs

# repalce with your own Spotify client ID and secret
# client_id = os.environ.get('CLIENT_ID')
# client_secret = os.environ.get('CLIENT_SECRET')
# client_id ="blank" # replace with your own Spotify client ID
# client_secret="blank" # replace with your own Spotify client secret
client_id ="d1f1f65af5f84370957268cd87f32ba3"
client_secret="557cede63f6b4820a66b8698f84ca9b0"

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, 
    client_secret=client_secret
)

sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def search_songs(query: str) -> List[Song]:
    results = sp.search(query, limit=10)
    songs = []
    for track in results['tracks']['items']:
        song = Song(
            title=track['name'],
            artist=track['artists'][0]['name'],
            album=track['album']['name'],
            spotify_id=track["id"]
        )
        songs.append(song)
    return songs

if __name__ == '__main__': 
    create_tables()
    
    while True:
        selection = input('''
        Enter: 
        s - to search
        g - to print all songs
        q - to quit
                          ''')
        selection = selection.lower()
        
        if selection =='q':
            break
        elif selection == 'g':
            print("All songs in the database:")
            all_songs = doa_get_all_songs()
            for song in all_songs:
                print(f"Title: {song.title}, Aritst: {song.artist}, Album: {song.album}")
                
        elif selection == 's':
            seearch_query = input("enter your search: ")
            songs = search_songs(seearch_query)
            
            if len(songs):
                print(f"Returned {len(songs)} songs")
                for i, song in enumerate(songs, start=1):
                    print(f"{i}. Title: {song.title}, Artist: {song.artist}, Album: {song.album}")
                
                save_choice = input("Do you want to save these songs? (y/n):")
                if save_choice.lower() == 'y':
                    doa_save_songs(songs)
                else:
                    print("Not saving songs.")
            else:
                print("No songs found from search")       
        else:
            print("Invalid selection. Please try again.")