# book-beats
BookBeats enhances your reading experience by creating custom ambient music playlists. Provide your book's title, and our tool uses an LLM (like ChatGPT) to suggest tracks that match the book's mood. It then compiles a playlist from Spotify, giving you the perfect soundtrack for your read.

## Setup Dependencies
You need to have python and pip installed. To download the dependencies run this in the directory with the requirements.txt file

```
pip install -r requirements.txt
```

## Create a .env file
In the main project directory(the place where requirements.txt is) you need to create a file called **.env** that has these contents
```
CLIENT_ID=...
CLIENT_SECRET=...
OPENAI_API_KEY=...
```

## Setup API keys
You will need to create a Spotify Web API app in [Spotify Account Dashboard](https://developer.spotify.com/dashboard). From There you can get the values for **CLIENT_ID** and **CLIENT_SECRET**

You can get an **OPENAI_API_KEY** from [OpenAI Platform](https://platform.openai.com/api-keys)