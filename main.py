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

load_dotenv()

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
    print("\n")
    print(json.dumps(json_object, indent=4, sort_keys=True))
    print("\n")

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

    print("\n\n\n")
    print(completion.choices[0].message)
    content = completion.choices[0].message.content
    print("\n\n\n")
    print("make it pretty")
    pretty_print_json(json.loads(content))
    items = json.loads(content)["items"]

    print("\n\n\n OpenAi Songs:\n")
    for i in items:
        print(i["song"] + " by " + i["artist"])

    return items
    



@app.route('/')
def index():

#    return AUTHORIZE_URL 
  #return f"<a href='{AUTHORIZE_URL}'>Authorize</a>" 
  return redirect(AUTHORIZE_URL, code=302)

@app.route('/callback')
def callback():
    print("callback endpoint hit!\n")
    
    received_code = request.args.get('code')
    if received_code:
        global shared_list_glob
        shared_list_glob.append(received_code)
        return f"<h1>Authorization Code:</h1><code>{received_code}</code>"
    else:
        return "<h1>Error: No code found in the callback URL</h1>", 400

if __name__ == '__main__':
    # Step 1: Get the authorization code
    # threading.Thread(target=run_app).start()  # Run Flask app in a separate thread


    received_code = None
    with Manager() as manager:
        shared_list = manager.list()
        server = Process(target=run_app, args=(shared_list,))

        print("Starting flask server\n")
        server.start()
        print("Flask server started\n")

        # this is a specific thing for WSL to open the browser automatically
        webbrowser.get("wslview %s").open("http://localhost:5000/")
        # You should probably just use
        # webbrowser.open("http://localhost:5000/")

    # while received_code is None:
    #     time.sleep(1)
    #     pass  # Wait until the authorization code is received

        while len(shared_list) == 0:
            print("waiting for code")
            time.sleep(1)
        
        server.terminate()
        server.join()

        received_code = shared_list[0]
        print("I GOT IT", received_code)

        

    print("Shutting down flask server\n")
    server.terminate()
    server.join()
    print("Flask server terminated\n")
    print("\n\n\n")
    print(f"Received authorization code: {received_code}")
    print("\n\n\n")

    # Step 2: Get the access token
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

    print("\n\n\n")

    print(all_text['access_token'])
    access_token = all_text['access_token']

    # Step 3: Get the user id before requesting to create playlist
    url = 'https://api.spotify.com/v1/me'

    response = requests.get(url, headers=get_standard_headers(access_token))

    # To check the response
    print("User ID response:\n")
    pretty_print_json(response.json())
    user_id = response.json()['id']
    print(user_id)

    # STEP 4: send a post request to create a playlist
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

    print("time to OpenAI\n")

    # Step 5: Get song suggestions from OpenAI
    openai_songs = get_song_suggestions(vibe="Harry Potter and the Deathly Hallows. Dark and eerie atmosphere")


    # Step 6: Search for a tracks based on song names and artists
    print("\nStep 6: Search for a tracks based on song names and artists\n")
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
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    data = {
        "uris": [f'spotify:track:{i}' for i in track_ids]
    }

    response = requests.post(url, headers=get_standard_headers(access_token), json=data)
    pretty_print_json(response.json())


    print("\n\n\n")
    print ("ALL DONE! Check your spotify account for the playlist you just made!")


    print("\n\n\n")
    print("YAY YOU GUYZ ARE THE BESTEST!!!!")
    sys.exit(0)
    # i_got = jsonify(response.json())
    # print(i_got)