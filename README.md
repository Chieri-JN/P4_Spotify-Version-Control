# P4_Spotify Version Control

## Notes about Requirements
It is recommended to use python 3.10+, *note you may encounter issues with 3.12, 3.11.9 was used for this project*
A spotify account is required to use the app.

## Project Description: 
At a high level the project idea is a spotify playlist version history tracker. It is in a sense a simplified “github” for one's spotify playlists. The goal is to keep track of states of a user's playlists in such a way that allows them to view previous states, restore a playlist to a previous state and clone a previous state of a playlist.

Key interactions: 
- Viewing past playlists versions
- Restoring a playlist to a previous state
- Cloning a previous playlist state into a new playlist

## How to run: 
    1. download the repo
    2. pip install -r requirements.txt
    3. go [spotify developer](https://developer.spotify.com/dashboard/) and create new app, 
    4. set redirect uri to [http://localhost:5003/callback](http://localhost:5003/callback)  
    5. get client id and client secret, from edit settings page
    6. put client id and client secret in  .env file
    7. use either **python app.py** or **python3 app.py** to run the app

## Environment Variables
If not already created, create a `.env` file in the root directory with the following:
```
SPOTIFY_CLIENT_ID = <your_client_id_here>
SPOTIFY_CLIENT_SECRET = <your_client_secret_here>
```

## Features
- Track changes to your Spotify playlists over time
- View past versions of your playlists
- Restore playlists to previous versions
- Clone past versions into new playlists
- Compare different versions of the same playlist


## Helpful Links
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Spotipy](https://spotipy.readthedocs.io/) - Python library for the Spotify Web API

