import unittest

from eeg_coderbot.coderbot import CoderBotClient
from eeg_coderbot.config import CoderBotConfig


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class FakeHttpClient:
    def __init__(self):
        self.posts = []
        self.gets = []

    def post(self, url, json):
        self.posts.append((url, json))
        return FakeResponse(status_code=201)

    def get(self, url):
        self.gets.append(url)
        return FakeResponse(payload={"code": "forward()"})


class CoderBotClientTests(unittest.TestCase):
    def test_move_dry_run_does_not_post(self):
        http = FakeHttpClient()
        client = CoderBotClient(CoderBotConfig(base_url="http://bot.test", dry_run=True), http_client=http)

        result = client.move(speed=10, elapse=2)

        self.assertTrue(result.dry_run)
        self.assertIsNone(result.status_code)
        self.assertEqual(http.posts, [])
        self.assertIn("DRY RUN", result.message)

    def test_move_posts_when_not_dry_run(self):
        http = FakeHttpClient()
        client = CoderBotClient(CoderBotConfig(base_url="http://bot.test", dry_run=False), http_client=http)

        result = client.move(speed=10, elapse=2)

        self.assertFalse(result.dry_run)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(http.posts, [("http://bot.test/control/move", {"speed": 10, "elapse": 2})])

    def test_move_requires_base_url_when_not_dry_run(self):
        client = CoderBotClient(CoderBotConfig(base_url="", dry_run=False), http_client=FakeHttpClient())

        with self.assertRaises(ValueError):
            client.move()


if __name__ == "__main__":
    unittest.main()
