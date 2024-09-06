from flask import Flask, request, redirect, jsonify
import threading
import webbrowser
from dotenv import load_dotenv
import os
from multiprocessing import Process
import base64
from urllib.parse import urlencode
import requests

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'

# todo fix the spotify scopes when I know them!
AUTHORIZE_URL = (f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}'
                 f'&scope=playlist-modify-public,playlist-modify-private'
                 f'&response_type=code'
                 f'&redirect_uri={REDIRECT_URI}')

received_code = None

def run_app():
    app.run(port=5000, use_reloader=False)

@app.route('/')
def index():

#    return AUTHORIZE_URL 
  #return f"<a href='{AUTHORIZE_URL}'>Authorize</a>" 
  return redirect(AUTHORIZE_URL, code=302)

@app.route('/callback')
def callback():
    global received_code
    received_code = request.args.get('code')
    if received_code:
        return f"<h1>Authorization Code:</h1><code>{received_code}</code>"
    else:
        return "<h1>Error: No code found in the callback URL</h1>", 400

if __name__ == '__main__':
    threading.Thread(target=run_app).start()  # Run Flask app in a separate thread
    server = Process(target=run_app)
    server.start()
    webbrowser.open('http://localhost:5000/')

    while received_code is None:
        pass  # Wait until the authorization code is received

    server.terminate()
    server.join()
    print("\n\n\n")
    print(f"Received authorization code: {received_code}")
    print("\n\n\n")

    my_base64_stuff = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    # Prepare the POST request to get the access token
    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'code': received_code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        },
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + my_base64_stuff
        }
    }

    # Make the POST request
    response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
    
    # Assuming you want to handle the JSON response in some way
    print(response.json())
    all_text = response.json()

    print("\n\n\n")

    print(all_text['access_token'])
    access_token = all_text['access_token']

    # TODO: Get the user id before requesting to create playlist

    # STEP X send a post request to create a playlist
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "name": "New Playlist",
        "description": "New playlist description",
        "public": False
    }

    response = requests.post(url, headers=headers, json=data)

    # To check the response
    print(response.status_code)
    print(response.json())

    print("\n\n\n")
    print("YAY YOU GUYZ ARE THE BESTEST!!!!")
    # i_got = jsonify(response.json())
    # print(i_got)