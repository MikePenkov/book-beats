# Book Beats

Book Beats creates a Spotify reading playlist from a book title. It searches public context and review snippets, asks an OpenAI-compatible model to shape a reading mood, and lets you preview the matched tracks before creating a private Spotify playlist.

The Web UI supports 中文 / English and runs entirely on your machine.

## Run locally

On Windows, double-click [`start_book_beats.bat`](start_book_beats.bat). The first run creates the virtual environment and installs dependencies; later runs start the app directly and open the browser.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\main.py
```

Open <http://127.0.0.1:5000>.

## Spotify setup

1. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. In its settings, add this Redirect URI exactly:

   ```
   http://127.0.0.1:5000/callback
   ```

3. Copy the app's Client ID and Client Secret into Book Beats.

## Model setup

The UI includes presets for OpenAI (`https://api.openai.com/v1`, `gpt-4o-mini`) and DeepSeek (`https://api.deepseek.com`, `deepseek-v4-flash`), plus a custom option for any provider compatible with OpenAI Chat Completions. You can always edit the API URL and model name. Smart track count has no artificial upper limit; Spotify writes are batched in groups of 100.

The form settings are kept in this browser, including across app restarts, so you do not need to re-enter them. Use this only on your own device and select **Clear saved settings on this device** when finished. OAuth tokens, research results, and previews live only in the running local process. Spotify playlists are private by default.

## Checks

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```
