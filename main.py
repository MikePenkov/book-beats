from flask import Flask, request, redirect
import threading
import webbrowser
from dotenv import load_dotenv
import os
from multiprocessing import Process

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'

# todo fix the spotify scopes when I know them!
AUTHORIZE_URL = (f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}'
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
      #  shutdown_server()  # Shut down the server after receiving the code
        return f"<h1>Authorization Code:</h1><code>{received_code}</code>"
    else:
        return "<h1>Error: No code found in the callback URL</h1>", 400

# def shutdown_server():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()

if __name__ == '__main__':
    global server
    threading.Thread(target=run_app).start()  # Run Flask app in a separate thread
    server = Process(target=run_app)
    server.start()
    webbrowser.open('http://localhost:5000/')

    while received_code is None:
        pass  # Wait until the authorization code is received

    server.terminate()
    server.join()
    print(f"Received authorization code: {received_code}")
    user_input = input("Please enter something to continue: ")
    print(f"You entered: {user_input}")
