from flask import jsonify, redirect, session, request, render_template, url_for
from datetime import datetime
import base64
import requests
import urllib.parse
from app import app, client_id, client_secret, redirect_uri, auth_url, token_url, api_base_url
from api import *
from models.userModel import *
from models.playlistModel import *
from models.songModel import *
from models.stateModel import *
from models.stageModel import StagedChange
from typing import *
from database import init_db, save_user, get_user, save_staged_change, get_staged_change, clear_staged_change, save_pending_changes, get_pending_changes, clear_pending_changes
import uuid

# Initialize the database when the app starts
init_db()

# ----------------------- Routes -------------------------
'''
    / - index page
    /home - home page
    /login - login page
    /callback - callback page
    /check_user - checks for existing user, if not create new user
    /playlists - view of all playlists
    /create_playlist - creates a new playlist
    /commit_changes - commit changes to playlist
    /playlist/<playlist_name> - view a single playlist
    /playlist_history/<playlist_id> - view the history of a playlist
'''
# ----------------------- / aka the root -------------------------
@app.route("/")
def index():
    return render_template('index.html')

# ----------------------- /login -------------------------
@app.route("/login")
def login():
    scope = "playlist-modify-public playlist-modify-private playlist-read-private user-read-private user-read-email"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True,
    }
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(full_auth_url)

# ----------------------- /callback -------------------------
@app.route("/callback")
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        code = request.args['code']
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            'Authorization': f"Basic {auth_header}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        response = requests.post(token_url, headers=headers, data=data)
        token_info = response.json()

        if 'access_token' in token_info:
            session['access_token'] = token_info['access_token']
            session['refresh_token'] = token_info['refresh_token']
            session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
            return redirect('/check_user')
        else:
            print("Error fetching access token:", token_info)
            return jsonify({"error": "Failed to retrieve access token."})


# ----------------------- /check_user -------------------------
@app.route("/check_user")
def check_user():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')

    # Try to get existing user from database
    if 'user_id' in session:
        user = get_user(session['user_id'])
        if user and not user.needs_refresh(max_age_minutes=0):
            print("Using existing user data from database")
            return redirect('/home')

    # Only make new user if necessary
    print("Creating new user from Spotify API")
    user = make_new_user(session['access_token'])
    session['user_id'] = user.id
    save_user(user)
    
    return redirect('/home')

# get current user
def get_current_user():
    if 'user_id' in session:
        return get_user(session['user_id'])
    return None

# ----------------------- /home -------------------------
@app.route("/home")
def home():
    return render_template('home.html')


# ----------------------- /playlists -------------------------
@app.route("/playlists")
def playlists():
    if 'access_token' not in session or 'user_id' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')

    # Try to get user from database first
    user = get_user(session['user_id'])
    
    # Only refresh if data is older than 10 minutes or doesn't exist
    if user is None:
        print("Data needs refresh, fetching from Spotify API")
        user = make_new_user(session['access_token'])
        save_user(user)
    else:
        print(f"Using cached data from database with {len(user.user_playlists)} playlists")
    
    # Update total_tracks for each playlist
    for playlist in user.user_playlists:
        # Get the corresponding playlist object
        playlist_obj = user.playlist_objects.get(playlist['id'])
        if playlist_obj and playlist_obj.states:
            # Update the total_tracks in the playlist dictionary
            playlist['total_tracks'] = len(playlist_obj.states[-1].tracks)
        else:
            # Fallback if no states exist
            playlist['total_tracks'] = 0

    return render_template('playlists.html', playlists=user.user_playlists)


# ----------------------- /playlist_history/<playlist_id> -------------------------
@app.route("/playlist_history/<playlist_id>")
def playlist_history(playlist_id):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')

    # Get user from database
    user = get_user(session['user_id'])
    
    if user is None:
        print("No user found, creating new user")
        user = make_new_user(session['access_token'])
        save_user(user)
    # elif user.needs_refresh(max_age_minutes=30):  # Use consistent 30-minute refresh
    #     print("Getting fresh playlist data")
    #     new_user = make_new_user(session['access_token'])
    #     # Compare and apply changes to preserve history
    #     changes = compare_playlists(user, new_user)
    #     user = apply_changes(user, changes)
    #     save_user(user)

    # Get the playlist object
    playlist = user.playlist_objects.get(playlist_id)
    
    if not playlist:
        print(f"Playlist {playlist_id} not found")
        return redirect('/playlists')

    # Get states and reverse list -> most recent one on top
    states = playlist.states[::-1]

    # Add formatted timestamp to each state for display
    # for state in states:
    #     timestamp = datetime.fromisoformat(state.data)
    #     state.timestamp = timestamp.strftime("%B %d, %Y at %I:%M %p")
    # print("THESE ARE THE STATES", states)
    # for state in states:
    #     state.display_info()
    # print("THIS A SANITY CHECK")\make_new_statez
    return render_template('playlist_history.html', 
                         states=states,
                         playlist_name=playlist.name,
                         playlist_id=playlist_id)  # Added playlist_id for template


# ----------------------- /pull_changes -------------------------
@app.route("/pull_changes")
def pull_changes():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')

    # Get current user from database
    current_user = get_user(session['user_id'])
    
    # Get fresh data from Spotify
    new_user = make_new_user(session['access_token'])
    
    # Compare and get changes
    changes = compare_playlists(current_user, new_user)
    
    # Store changes in database instead of session
    pending_changes = {
        'new_playlists': [p.to_dict() for p in changes['new_playlists']],
        'deleted_playlists': [p.to_dict() for p in changes['deleted_playlists']],
        'modified_playlists': [{
            'playlist': change['playlist'].to_dict(),
            'added_tracks': [t.to_dict() for t in change['added_tracks']],
            'removed_tracks': [t.to_dict() for t in change['removed_tracks']]
        } for change in changes['modified_playlists']]
    }
    save_pending_changes(session['user_id'], pending_changes)
    
    # Only store a flag in session
    session['has_pending_changes'] = True
    
    return render_template('pull_changes.html', changes=changes)

@app.route("/confirm_pull_changes")
def confirm_pull_changes():
    if 'access_token' not in session or 'has_pending_changes' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')

    # Get pending changes from database
    pending_changes = get_pending_changes(session['user_id'])
    if not pending_changes:
        return redirect('/playlists')
    
    # Get current user
    user = get_user(session['user_id'])
    
    # Reconstruct changes from database data
    changes = {
        'new_playlists': [
            Playlist.from_dict(p_dict) 
            for p_dict in pending_changes['new_playlists']
        ],
        'deleted_playlists': [
            Playlist.from_dict(p_dict)
            for p_dict in pending_changes['deleted_playlists']
        ],
        'modified_playlists': [{
            'playlist': Playlist.from_dict(change['playlist']),
            'added_tracks': [Song.from_dict(t) for t in change['added_tracks']],
            'removed_tracks': [Song.from_dict(t) for t in change['removed_tracks']]
        } for change in pending_changes['modified_playlists']]
    }
    
    # Apply changes
    updated_user = apply_changes(user, changes)
    
    # Save updated user to database
    save_user(updated_user)
    
    # Clear pending changes from both session and database
    session.pop('has_pending_changes', None)
    clear_pending_changes(session['user_id'])
    
    return redirect('/playlists')


# ----------------------- /restore_state -------------------------   
@app.route("/restore_state/<state_id>/<playlist_id>")
def restore_state(state_id, playlist_id):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    
    # Get user and playlist data
    user = get_user(session['user_id'])
    playlist = user.playlist_objects.get(playlist_id)
    
    if not playlist:
        print(f"Playlist {playlist_id} not found")
        return redirect('/playlists')
    
    # Find the state we want to restore
    state = next((s for s in playlist.states if s.id == int(state_id)), None)
    
    if not state:
        print(f"State {state_id} not found")
        return redirect(f'/playlist_history/{playlist_id}')
    
    # Create staged change
    staged_change = StagedChange(
        id=str(uuid.uuid4()),
        type='restore',
        playlist_id=playlist_id,
        state_id=state_id,
        tracks=[track.to_dict() for track in state.tracks],
        name=state.name,
        description=state.description
    )
    
    # Save to database
    save_staged_change(session['user_id'], staged_change)
    
    # Store only the type in session
    session['staged_type'] = 'restore'
    
    return redirect('/push_changes')


# ----------------------- /clone_state -------------------------
@app.route("/clone_state/<state_id>")
def clone_state(state_id, playlist_id):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    # not implemented
    # clone playlist state to new playlist
    return redirect('/push_changes')


# ----------------------- /push_changes -------------------------
@app.route("/push_changes")
def push_changes():
    if 'access_token' not in session or 'staged_type' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    
    # Get staged changes from database
    staged_change = get_staged_change(session['user_id'])
    if not staged_change:
        print("No staged changes found in database")
        return redirect('/playlists')

    return render_template('push_changes.html', changes=staged_change.to_dict())


# ----------------------- /confirm_push_changes -------------------------
@app.route("/confirm_push_changes")
def confirm_push_changes():
    if 'access_token' not in session or 'staged_type' not in session:
        return redirect('/playlists')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    
    # Get staged changes from database
    staged_change = get_staged_change(session['user_id'])
    if not staged_change:
        return redirect('/playlists')
    
    if staged_change.type == 'restore':
        # Get user and playlist
        user = get_user(session['user_id'])
        playlist = user.playlist_objects.get(staged_change.playlist_id)
        
        if not playlist:
            print("Playlist not found in database")
            return redirect('/playlists')
        
        try:
            print(f"Starting playlist restore for {playlist.name}")
            
            # First, clear the playlist on Spotify
            clear_playlist(session['access_token'], playlist.id)
            print("Successfully cleared playlist")
            
            # Get track URIs from the state's tracks
            track_uris = [f"spotify:track:{track['id']}" for track in staged_change.tracks]
            print(f"Preparing to add {len(track_uris)} tracks")
            
            # Add tracks back to the Spotify playlist
            if track_uris:  # Only try to add tracks if we have any
                add_tracks_to_playlist(session['access_token'], playlist.id, track_uris)
                print("Successfully added tracks back to playlist")
            
            # Update local playlist
            playlist.tracks = [Song.from_dict(track) for track in staged_change.tracks]
            playlist.total_tracks = len(playlist.tracks)
            # Create new state
            new_state = make_new_state(
                None,
                playlist_id=playlist.id,
                description=staged_change.description,
                id=len(playlist.states),
                image_url=playlist.image,
                playlist_name=staged_change.name,
                tracks=playlist.tracks
            )
            print("Created new state")
            
            # Add new state
            playlist.states.append(new_state)
            
            # Update user in database
            save_user(user)
            print("Saved changes to database")
            
            # Clear staged changes from both session and database
            session.pop('staged_type', None)
            clear_staged_change(session['user_id'])
            
            return redirect(url_for('playlists'))
            
        except Exception as e:
            print(f"Error during playlist restore: {str(e)}")
            # If we hit an error, try to redirect to playlists
            return redirect(url_for('playlists'))
    
    # If we get here, something went wrong
    print("No valid changes found to apply")
    return redirect(url_for('playlists'))

# ----------------------- /cancel_push -------------------------
@app.route("/cancel_push")
def cancel_push():
    if 'staged_type' not in session:
        return redirect('/playlists')
    return render_template('cancel_push.html')

@app.route("/confirm_cancel_push")
def confirm_cancel_push():
    session.pop('staged_type', None)
    clear_staged_change(session['user_id'])
    return redirect('/playlists')


# ----------------------- /refresh_token -------------------------
@app.route("/refresh_token")
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret,
        }

    response = requests.post(token_url, data=req_body)
    new_token_info = response.json()

    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    previous_page = request.referrer or url_for('home')  # if no prev page, go to home
    return redirect(previous_page)


@app.route("/playlist/<playlist_id>")
def playlist(playlist_id):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    
    # Get user from database
    user = get_user(session['user_id'])
    
    # Get the playlist
    playlist = user.playlist_objects.get(playlist_id)
    if not playlist:
        return redirect('/playlists')
    
    # Make sure total_tracks is up to date
    playlist.total_tracks = len(playlist.tracks)
    
    return render_template('playlist.html', playlist=playlist)

@app.route("/create_playlist")
def create_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
        return redirect('/refresh_token')
    # not implemented
    return render_template('create_playlist.html')

