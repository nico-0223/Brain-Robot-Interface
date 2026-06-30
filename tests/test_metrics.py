import unittest

from eeg_coderbot.metrics import should_move_from_met_values, values_to_dict


class MetricTests(unittest.TestCase):
    def test_values_to_dict_maps_columns_and_ignores_missing_values(self):
        self.assertEqual(values_to_dict(["a", "b", "c"], [1, 2]), {"a": 1, "b": 2})

    def test_should_move_when_engagement_and_excitement_are_positive(self):
        values = [0, 0.2, 0, 0.4]
        self.assertTrue(should_move_from_met_values(values))

    def test_should_not_move_when_engagement_is_missing(self):
        values = [0, None, 0, 0.4]
        self.assertFalse(should_move_from_met_values(values))

    def test_should_not_move_when_excitement_is_zero(self):
        values = [0, 0.2, 0, 0]
        self.assertFalse(should_move_from_met_values(values))

    def test_should_not_move_when_message_is_too_short(self):
        self.assertFalse(should_move_from_met_values([0, 0.2]))


if __name__ == "__main__":
    unittest.main()
