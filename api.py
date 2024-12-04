import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get, delete
import requests

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_user_info(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result['display_name'], json_result['id']


def get_user_playlists(token):
    # set limit = 8 because I have too many playlists
    url = "https://api.spotify.com/v1/me/playlists?limit=8"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    if result.status_code == 200:
        json_result = json.loads(result.content)
        playlists = json_result["items"]
        nextSet = json_result['next']
        
       # set limit = 8 because I have too many playlists
        while nextSet and len(playlists) < 8:
            print("getting next set of playlists")
            response = get(nextSet, headers=headers)
            result = response.json()
            playlists.extend(result['items'])
            nextSet = result['next']

        print(f"Total playlists fetched: {len(playlists)}")
        
        return playlists
    else:
        return []

def get_playlist_info(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}?market=US"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result

def get_playlist_tracks(token, playlist_id):
    # setting retrieved fields to get the tracks, id, name, href, and album name 
    fields = "tracks.items(track(id,name,artists.name,album.name)),next"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}?market=US&fields={fields}"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    # print('PRINTING JSON RESULT')
    # print(json_result)
    if 'tracks' in json_result:
        tracks = json_result['tracks']["items"]
        nextSet = json_result['tracks'].get('next', None)
        while nextSet:
            print("getting next set of tracks")
            response = get(nextSet, headers=headers)
            result = response.json()
            tracks.extend(result['tracks']['items'])
            nextSet = result['tracks']['next']
        return tracks
    else:
        return []   

def get_song_info(token, track_id):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result

def create_playlist(token, user_id, playlist_name, description, playlist_public):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    
    data = {
        "name": playlist_name,
        "description": description,
        "public": playlist_public,
    }
    
    result = post(url, headers=headers, json=data)
    json_result = json.loads(result.content)
    
    return json_result
    
    
def add_tracks_to_playlist(token, playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    data = {"uris": track_ids}
    
    result = post(url, headers=headers, json=data)
    json_result = json.loads(result.content)
    
    return json_result

def delete_tracks_from_playlist(token, playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    data = {"tracks": [{"uri": track_id} for track_id in track_ids]}
    
    result = delete(url, headers=headers, json=data)
    json_result = json.loads(result.content)
    
    return json_result

def clear_playlist(token, playlist_id):
    """Remove all tracks from a Spotify playlist"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # First, get all tracks in the playlist
    response = requests.get(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers=headers
    )
    response.raise_for_status()
    
    tracks = response.json()['items']
    if not tracks:
        return
    
    # Create list of track URIs to remove
    uris = [{'uri': track['track']['uri']} for track in tracks]
    
    # Remove all tracks
    response = requests.delete(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers=headers,
        json={'tracks': uris}
    )
    response.raise_for_status()

def add_tracks_to_playlist(token, playlist_id, track_uris):
    """Add tracks to a Spotify playlist"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Spotify API has a limit of 100 tracks per request
    for i in range(0, len(track_uris), 100):
        chunk = track_uris[i:i + 100]
        response = requests.post(
            f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
            headers=headers,
            json={'uris': chunk}
        )
        response.raise_for_status()
        print(f"Added {len(chunk)} tracks to playlist")