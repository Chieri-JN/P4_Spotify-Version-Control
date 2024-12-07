# P4_Spotify Version Control

# Requirements
python 3.10+, note may encounter issues with 3.12, 3.11.9 was used for this project
flask version 2.3.3
a spotify account
potentially a spotify developer account


# Project Description: 
At a high level the project idea is a spotify playlist version history tracker. It is in a sense a simplified “github” for one's spotify playlists. The goal is to keep track of states of a user's playlists in such a way that allows them to view previous states, restore a playlist to a previous state and clone a previous state of a playlist.
Key interactions: 
- Viewing past playlists versions
- Restoring a playlist to a previous state
- Cloning a previous playlist state into a new playlist

# Project Structure: 
```tree
├── static/
│ └── css/
│ └── style.css
├── templates/
│ └── cancel_push.html
│ └── home.html
│ └── index.html
│ └── playlists_history.html
│ └── playlist.html
│ └── playlists.html
│ └── pull_changes.html
│ └── push_changes.html
├── main.py
├── models/
│ ├── playlistModel.py
│ ├── songModel.py
│ ├── stateModel.py
│ ├── userModel.py
│ └── stageModel.py
├── README.md
└── requirements.txt
```

# How to run: 
    1. download the repo
    2. pip install -r requirements.txt
    3. go [spotify developer](https://developer.spotify.com/dashboard/) and create new app, 
    4. set redirect uri to [http://localhost:5003/callback](http://localhost:5003/callback)  
    5. get client id and client secret, from edit settings page
    4. put client id and client secret in  new .env file
    5. use either **python app.py** or **python3 app.py** to run the app

