import datetime
from flask import Flask, jsonify, redirect, session
import requests
import os
import urllib.parse

app = Flask(__name__)
key = "8430320293932802-2-3299492--239398484"
sk = os.getenv("SECRET_KEY")
app.secret_key = key


client_id ="3151fdf8d67d41e88616a2910c6a4c64"
client_secret="7358788d3e82427589eb8db56894e40a"
redirect_uri = "http://localhost:5000/callback/"

auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
api_base_url = "https://api.spotify.com/v1"


@app.route("/")
def index():
    return "Welcome bum <a href='{/login}'>Login</a>"

@app.route("/login")
def login():
    scope = "user-read-private user-read-email"

    params = {
        'client_id' : client_id,
        'response_type' : 'code',
        'scope' : scope,
        'redirect_uri' : redirect_uri,
        'show_dialog' : True, # to force the user to login again if they are already logged in
    }

    auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)   

# if __name__ == "__main__":
#     app.run(debug=True)


# account for success and erros 
@app.route("/callback")
def callback():
    if 'error' in requests.args:
        return jsonify({"error": requests.args['error']})

    if 'code' in requests.args:
        req_body = {
            'code' : requests.args['code'],
            'grant_type' : 'authorization_code',
            'redirect_uri' : redirect_uri,
            'client_id' : client_id,
            'client_secret' : client_secret,
        }

        response = requests.post(token_url, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token'] # used make requests to the Spotify API   
        session['refresh_token'] = token_info['refresh_token'] # used to refresh access token when it expires
        session['expires_at'] = datetime.now().timestamp() +  token_info['expires_in'] # tells use when token expires, lasts fro 1 hour

        
        return redirect('/playlists')


@app.route("/playlists")
def get_playlists():
    if 'access_token' not in session: # token should be in session otherwise ... not good
        return redirect('/login')
    
    #  has token expired?
    if datetime.now().timestamp > session['expires_at']:
        return redirect('/refresh_token')
    

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{api_base_url}me/playlists", headers=headers)
    playlists = response.json()

    return playlists

@app.route("/refresh_token")
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp > session['expires_at']:
        # info needed to refresh the token from spotify
        req_body = {
            'grant_type' : 'refresh_token',
            'refresh_token' : session['refresh_token'],
            'client_id' : client_id,
            'client_secret' : client_secret,
        }

    response = requests.post(token_url, data=req_body)
    new_token_info = response.json()

    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/playlists')

if __name__ == "__main__":
    app.run(debug=True)