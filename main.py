from flask import Flask, request
import threading
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

CLIENT_ID = 'YOUR_CLIENT_ID'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTHORIZE_URL = f"https://your-okta-domain.okta.com/oauth2/default/v1/authorize?client_id={CLIENT_ID}&response_type=code&scope=openid&redirect_uri={REDIRECT_URI}&state=1234"

received_code = None

def run_app():
    app.run(port=5000, use_reloader=False)

@app.route('/')
def index():
    return redirect(AUTHORIZE_URL, code=302)

@app.route('/callback')
def callback():
    global received_code
    received_code = request.args.get('code')
    if received_code:
        shutdown_server()  # Shut down the server after receiving the code
        return f"<h1>Authorization Code:</h1><code>{received_code}</code>"
    else:
        return "<h1>Error: No code found in the callback URL</h1>", 400

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    threading.Thread(target=run_app).start()  # Run Flask app in a separate thread
    webbrowser.open('http://localhost:5000/')

    while received_code is None:
        pass  # Wait until the authorization code is received

    print(f"Received authorization code: {received_code}")
    user_input = input("Please enter something to continue: ")
    print(f"You entered: {user_input}")
