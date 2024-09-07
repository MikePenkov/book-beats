import base64
import os
import threading
import webbrowser
from openai import OpenAI
from multiprocessing import Process, Manager

import requests
from dotenv import load_dotenv
from flask import Flask, request, redirect
import json
from prompts import system_message, generate_prompt
import sys
import time
from banner import print_banner_text
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# todo fix the spotify scopes when I know them!
AUTHORIZE_URL = (f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}'
                 f'&scope=playlist-modify-public,playlist-modify-private,user-read-private,user-read-email'
                 f'&response_type=code'
                 f'&redirect_uri={REDIRECT_URI}')

def run_app(shared_list):
    global shared_list_glob 
    shared_list_glob = shared_list
    app.run(port=5000, use_reloader=False)


def get_standard_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

def pretty_print_json(json_object):
    logging.debug("\n")
    logging.debug(json.dumps(json_object, indent=4, sort_keys=True))
    logging.debug("\n")

def get_song_suggestions(vibe: str) -> [str]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": generate_prompt(vibe)
            }
        ]
    )

    logging.debug("\n\n\n")
    logging.debug(completion.choices[0].message)
    content = completion.choices[0].message.content
    logging.debug("\n\n\n")
    pretty_print_json(json.loads(content))
    items = json.loads(content)["items"]

    logging.debug("\n\n\n OpenAi Songs:\n")
    for i in items:
        logging.debug(i["song"] + " by " + i["artist"])

    return items
    



@app.route('/')
def index():
  return redirect(AUTHORIZE_URL, code=302)

@app.route('/callback')
def callback():
    logging.debug("callback endpoint hit!\n")
    
    received_code = request.args.get('code')
    if received_code:
        global shared_list_glob
        shared_list_glob.append(received_code)
        return f"<h1>Authorization Code:</h1><code>{received_code}</code>"
    else:
        return "<h1>Error: No code found in the callback URL</h1>", 400

if __name__ == '__main__':

    print_banner_text()
    # Step 0: vibe check
    logging.debug("Step 0: ask for a vibe check\n")
    vibe = input("What kind of atmoshpere are you looking for?\n")


    # Step 1: Get the authorization code
    logging.debug("Step 1: get the authorization code\n")
    received_code = None
    with Manager() as manager:
        shared_list = manager.list()
        server = Process(target=run_app, args=(shared_list,))

        logging.debug("Starting flask server\n")
        server.start()
        logging.debug("Flask server started\n")

        # this is a specific thing for WSL to open the browser automatically
        webbrowser.get("wslview %s").open("http://localhost:5000/")
        # You should probably just use
        # webbrowser.open("http://localhost:5000/")

        while len(shared_list) == 0:
            logging.debug("waiting for code")
            time.sleep(1)
        
        server.terminate()
        server.join()

        received_code = shared_list[0]
        logging.debug("I GOT IT", received_code)

        

    logging.debug("Shutting down flask server\n")
    server.terminate()
    server.join()
    logging.debug("Flask server terminated\n")
    logging.debug("\n\n\n")
    logging.debug(f"Received authorization code: {received_code}")
    logging.debug("\n\n\n")

    # Step 2: Get the access token
    logging.debug("Step 2: get the access token\n")
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
    pretty_print_json(response.json())
    all_text = response.json()

    logging.debug("\n\n\n")

    logging.debug(all_text['access_token'])
    access_token = all_text['access_token']

    # Step 3: Get the user id before requesting to create playlist
    logging.debug("Step 3: get the user id\n")
    url = 'https://api.spotify.com/v1/me'

    response = requests.get(url, headers=get_standard_headers(access_token))

    # To check the response
    logging.debug("User ID response:\n")
    pretty_print_json(response.json())
    user_id = response.json()['id']
    logging.debug(user_id)

    # STEP 4: send a post request to create a playlist
    logging.debug("Step 4: send a post request to create a playlist\n")
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    data = {
        "name": "Book-Beats Playlist",
        "description": "Awesome Trio strikes again",
        "public": True
    }

    response = requests.post(url, headers=get_standard_headers(access_token), json=data)

    # To check the response
    pretty_print_json(response.json())
    playlist_id = response.json()['id']

    logging.debug("time to OpenAI\n")

    # Step 5: Get song suggestions from OpenAI
    logging.debug("Step 5: Get song suggestions from OpenAI\n")
    openai_songs = get_song_suggestions(vibe)


    # Step 6: Search for a tracks based on song names and artists
    logging.debug("Step 6: Search for a tracks based on song names and artists\n")
    track_ids = []

    for i in openai_songs:
        name = i["song"]
        artist = i["artist"]
        url = f'https://api.spotify.com/v1/search?q=track:{name} artist:{artist}&type=track,artist&limit=1'
        response = requests.get(url, headers=get_standard_headers(access_token))
        if response.json()['tracks']['items'] == []:
            continue # Skip the track if nothing was returned by spotify
        track_id = response.json()['tracks']['items'][0]['id']
        track_ids.append(track_id)
    


    # Step 7: Add tracks to playlist
    logging.debug("Step 7: Add tracks to playlist\n")
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    data = {
        "uris": [f'spotify:track:{i}' for i in track_ids]
    }

    response = requests.post(url, headers=get_standard_headers(access_token), json=data)
    pretty_print_json(response.json())


    logging.debug("\n\n\n")
    logging.info("ALL DONE! Check your spotify account for the playlist you just made!")

