from datetime import datetime
import base64
from flask import Flask, jsonify, redirect, session, request
import requests
import os
import urllib.parse

app = Flask(__name__)
key = "8430320293932802-2-3299492--239398484"
sk = os.getenv("SECRET_KEY")
app.secret_key = key

client_id = "97d45ae505fa435f8ff093e5c24f5ecc"
client_secret = "0e7541b28bf9424abef6984749bc5b1e"
redirect_uri = "http://localhost:5002/callback"

auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
api_base_url = "https://api.spotify.com/v1/"

@app.route("/")
def index():
    return "Welcome bum <a href='/login'>Login</a>"

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

    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(full_auth_url)   

# if __name__ == "__main__":
#     app.run(debug=True)

@app.route("/callback")
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        code = request.args['code']

        # Prepare the headers with Basic Authentication
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            'Authorization': f"Basic {auth_header}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Prepare the body
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }

        # Make the POST request
        response = requests.post(token_url, headers=headers, data=data)
        token_info = response.json()

        # Handle possible errors
        if 'access_token' in token_info:
            session['access_token'] = token_info['access_token']
            session['refresh_token'] = token_info['refresh_token']
            session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
            # session['expires_at'] = datetime.now().timestamp() + 10
            return redirect('/playlists')
        else:
            # Log the error and inform the user
            print("Error fetching access token:", token_info)
            return jsonify({"error": "Failed to retrieve access token."})

@app.route("/playlists")
def get_playlists():
    if 'access_token' not in session: # token should be in session otherwise ... not good
        return redirect('/login')
    
    #  has token expired?
    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
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
    


    if datetime.now().timestamp() > session['expires_at']:
        print("token expired, REFRESHING....")
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
    # session['expires_at'] = datetime.now().timestamp() + 10

    return redirect('/playlists')

if __name__ == "__main__":
    app.run(debug=True, port=5002, host='127.0.0.1')