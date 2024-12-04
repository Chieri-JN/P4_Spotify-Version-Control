from flask import Flask
import os

app = Flask(__name__)
key = "8430320293932802-2-3299492"
app.secret_key = key

# important things
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:5003/callback"
auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
api_base_url = "https://api.spotify.com/v1/"

# Import routes after app initialization
from routing import *

if __name__ == "__main__":
    app.run(debug=True, port=5003, host='127.0.0.1')