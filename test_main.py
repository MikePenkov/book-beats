import json
import unittest
from unittest.mock import Mock, patch

import main


class BookBeatsTest(unittest.TestCase):
    def setUp(self):
        main.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        main.RUNS.clear()
        self.client = main.app.test_client()

    def test_model_payload_handles_fenced_json(self):
        atmosphere, songs = main.model_payload('```json\n{"atmosphere":{"name":"Rain","summary":"Muted"},"songs":[{"title":"A","artist":"B","why":"Fits"}]}\n```', 5)
        self.assertEqual(atmosphere["name"], "Rain")
        self.assertEqual(songs[0]["artist"], "B")

    @patch("main.requests.post")
    def test_model_request_enforces_json_output_and_language(self, post):
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": '{"atmosphere":{"name":"雨夜","summary":"安静"},"songs":[{"title":"A","artist":"B","why":"适合"}]}'}}]}
        post.return_value = response
        run = {"book_title": "书", "song_count": 1, "content_language": "zh", "model_api_key": "key", "base_url": "https://api.example.com/v1", "model_name": "model"}
        main.ask_for_songs(run, [])
        kwargs = post.call_args.kwargs
        self.assertEqual(post.call_args.args[0], "https://api.example.com/v1/chat/completions")
        self.assertEqual(kwargs["json"]["response_format"], {"type": "json_object"})
        self.assertIn("Simplified Chinese", kwargs["json"]["messages"][1]["content"])
        self.assertEqual(kwargs["timeout"], 120)

    def test_generation_timeout_has_retryable_error(self):
        main.RUNS["run"] = {"book_title": "Book", "song_count": 1, "content_language": "zh", "model_api_key": "key", "base_url": "https://api.example.com/v1", "model_name": "model", "access_token": "token"}
        with self.client.session_transaction() as browser_session:
            browser_session["run_id"] = "run"
        with patch("main.research_book", return_value=[]), patch("main.requests.post", side_effect=main.requests.Timeout("slow")):
            response = self.client.post("/generate")
        self.assertEqual(response.status_code, 504)
        self.assertIn("模型响应超时", response.get_json()["error"])

    def test_authorize_requires_complete_form(self):
        self.assertEqual(self.client.post("/authorize", data={"book_title": "Book"}).status_code, 400)

    def test_authorize_redirects_to_spotify(self):
        response = self.client.post("/authorize", data={"book_title": "Book", "song_count": "6", "spotify_client_id": "client", "spotify_client_secret": "secret", "model_api_key": "key", "model_name": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.spotify.com/authorize", response.location)
        self.assertIn("scope=playlist-modify-public+playlist-modify-private", response.location)
        self.assertEqual(main.RUNS[next(iter(main.RUNS))]["content_language"], "zh")

    def test_auto_song_count_is_accepted(self):
        response = self.client.post("/authorize", data={"book_title": "Book", "song_count": "5", "auto_song_count": "1", "spotify_client_id": "client", "spotify_client_secret": "secret", "model_api_key": "key", "model_name": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(main.RUNS[next(iter(main.RUNS))]["song_count"])

    def test_auto_payload_accepts_more_than_twenty_songs(self):
        songs = [{"title": f"Song {index}", "artist": "Artist", "why": "Fits"} for index in range(21)]
        _, parsed = main.model_payload(json.dumps({"atmosphere": {"name": "Mood"}, "songs": songs}), None)
        self.assertEqual(len(parsed), 21)

    def test_language_switches_to_english(self):
        response = self.client.get("/language/en?next=/", follow_redirects=True)
        self.assertIn(b"A sonic bookmark", response.data)

    def test_model_provider_presets_are_rendered(self):
        response = self.client.get("/")
        self.assertIn(b'value="openai"', response.data)
        self.assertIn(b'value="deepseek"', response.data)
        self.assertIn(b'data-auto-count', response.data)

    def test_preview_survives_a_refresh(self):
        main.RUNS["run"] = {"book_title": "Book", "atmosphere": {"name": "Mood", "summary": "Quiet"}, "research": [], "tracks": []}
        with self.client.session_transaction() as browser_session:
            browser_session["run_id"] = "run"
        self.assertEqual(self.client.get("/preview").status_code, 200)
        self.assertEqual(self.client.get("/preview").status_code, 200)

    def test_callback_redirects_to_loading_screen(self):
        main.RUNS["run"] = {"state": "state"}
        with self.client.session_transaction() as browser_session:
            browser_session["run_id"] = "run"
        response = self.client.get("/callback?code=code&state=state")
        self.assertEqual(response.location, "/generating")
        self.assertEqual(main.RUNS["run"]["authorization_code"], "code")

    def test_loading_screen_requires_authorization_code(self):
        self.assertEqual(self.client.get("/generating").location, "/")

    @patch("main.requests.post")
    def test_playlist_uses_current_spotify_items_endpoint(self, post):
        playlist_response, add_response = Mock(), Mock()
        playlist_response.json.return_value = {"id": "playlist", "external_urls": {"spotify": "https://open.spotify.com/playlist/playlist"}}
        post.side_effect = [playlist_response, add_response]
        main.RUNS["run"] = {"book_title": "Book", "access_token": "token", "atmosphere": {"name": "Mood", "summary": "A quiet reading soundtrack."}, "tracks": [{"found": True, "id": "track"}]}
        with self.client.session_transaction() as browser_session:
            browser_session["run_id"] = "run"

        response = self.client.post("/playlist", data={"track_id": "track"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.call_args_list[0].kwargs["json"]["description"], "Mood — A quiet reading soundtrack.")
        self.assertEqual(post.call_args_list[1].args[0], "https://api.spotify.com/v1/playlists/playlist/items")

    @patch("main.requests.post")
    def test_playlist_rejects_duplicate_submission(self, post):
        main.RUNS["run"] = {"tracks": [{"found": True, "id": "track"}], "playlist_creating": True}
        with self.client.session_transaction() as browser_session:
            browser_session["run_id"] = "run"

        response = self.client.post("/playlist", data={"track_id": "track"})

        self.assertEqual(response.status_code, 409)
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
