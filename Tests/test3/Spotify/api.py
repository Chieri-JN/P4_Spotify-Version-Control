import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get, delete

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Debugging: Print client_id and client_secret
# print("Client ID:", client_id)
# print("Client Secret:", client_secret)

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

def get_user_playlists(token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    playlists = json_result["items"]
    
    return playlists

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    tracks = json_result["items"]
    
    return tracks

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