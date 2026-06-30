import os
import unittest
from unittest.mock import patch

from eeg_coderbot.config import AppConfig


class AppConfigTests(unittest.TestCase):
    def test_from_env_uses_defaults_for_missing_values(self):
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()

        self.assertEqual(config.cortex.websocket_url, "wss://localhost:6868")
        self.assertEqual(config.cortex.client_id, "")
        self.assertFalse(config.coderbot.dry_run)
        self.assertEqual(config.movement.speed, 100)

    def test_from_env_parses_overrides(self):
        env = {
            "EMOTIV_CORTEX_URL": "wss://example.test:6868",
            "EMOTIV_CLIENT_ID": "client-id",
            "EMOTIV_CLIENT_SECRET": "client-secret",
            "CODERBOT_BASE_URL": "http://bot.test",
            "DRY_RUN": "true",
            "CODERBOT_MOVE_SPEED": "42",
            "CODERBOT_MOVE_ELAPSE": "3",
            "EXPERIMENT_SECONDS": "5.5",
        }
        with patch.dict(os.environ, env, clear=True):
            config = AppConfig.from_env()

        self.assertEqual(config.cortex.websocket_url, "wss://example.test:6868")
        self.assertEqual(config.cortex.client_id, "client-id")
        self.assertEqual(config.cortex.client_secret, "client-secret")
        self.assertEqual(config.coderbot.base_url, "http://bot.test")
        self.assertTrue(config.coderbot.dry_run)
        self.assertEqual(config.movement.speed, 42)
        self.assertEqual(config.movement.elapse, 3)
        self.assertEqual(config.movement.experiment_seconds, 5.5)

    def test_invalid_integer_setting_raises(self):
        with patch.dict(os.environ, {"CODERBOT_MOVE_SPEED": "fast"}, clear=True):
            with self.assertRaises(ValueError):
                AppConfig.from_env()


if __name__ == "__main__":
    unittest.main()
