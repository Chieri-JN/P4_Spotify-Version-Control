import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get

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

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    
    headers = get_auth_header(token)
    query = f"q=artist:{artist_name}&type=artist&limit=1" # Limiting to one result for simplicity
    
    query_url = url + "?" + query
    # print(query_url)
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if not len(json_result):
        print("No artist found with the name: ", artist_name)
        return
    
    return json_result[0]
    
def get_song_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US" 
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

    

token = get_token()
res = search_for_artist(token, "The Rare Occasions")
artist_id = res["id"]
songs = get_song_by_artist(token, artist_id)
# print(songs)

for idx, song in enumerate(songs):
    print(f"{idx+1}. {song['name']}")