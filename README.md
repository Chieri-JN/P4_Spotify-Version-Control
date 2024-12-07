# P4_Spotify Version Control

## Notes about Requirements
It is recommended to use python 3.10+ ,*note may encounter issues with 3.12, 3.11.9 was used for this project*
A spotify account is required to use the app.

## Project Description: 
At a high level the project idea is a spotify playlist version history tracker. It is in a sense a simplified “github” for one's spotify playlists. The goal is to keep track of states of a user's playlists in such a way that allows them to view previous states, restore a playlist to a previous state and clone a previous state of a playlist.
Key interactions: 
- Viewing past playlists versions
- Restoring a playlist to a previous state
- Cloning a previous playlist state into a new playlist

## Project Structure: 
```tree
├── static/
│ └── css/
│ └── style.css (css for the project)
├── templates/
│ └── cancel_push.html (template for cancel push page)
│ └── home.html (template for home page)
│ └── index.html (template for index page)
│ └── playlists_history.html (template for playlists history page)
│ └── playlist.html (template for playlist page)
│ └── playlists.html (template for playlists page)
│ └── pull_changes.html (template for pull changes page)
│ └── push_changes.html (template for push changes page)
├── models/
│ ├── playlistModel.py (model for playlists)
│ ├── songModel.py (model for songs)
│ ├── stateModel.py (model for states)
│ ├── userModel.py (model for users)
│ └── stageModel.py (model for stages ie what change is being made)
├── README.md
└── requirements.txt
├── app.py (main file to run the app)
├── api.py (where the spotify api calls are made)
├── routing.py (routing for the app)
├── database.py (database for the app)
├── .env (environment variables for the app)
└── Notes.md (notes)
```

## How to run: 
    1. download the repo
    2. pip install -r requirements.txt
    3. go [spotify developer](https://developer.spotify.com/dashboard/) and create new app, 
    4. set redirect uri to [http://localhost:5003/callback](http://localhost:5003/callback)  
    5. get client id and client secret, from edit settings page
    6. put client id and client secret in  .env file
    7. use either **python app.py** or **python3 app.py** to run the app

