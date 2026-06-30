import unittest

from eeg_coderbot.mental_states import (
    MentalCommandAlgorithm,
    PerformanceMetricThresholdAlgorithm,
    get_algorithm,
    list_algorithms,
)


class PerformanceMetricThresholdAlgorithmTests(unittest.TestCase):
    def test_engaged_excited_metric_triggers_fast_move(self):
        algorithm = PerformanceMetricThresholdAlgorithm()
        values = [None, 0.3, None, 0.4]

        action = algorithm.evaluate([], values)

        self.assertEqual(action.event.state, "engaged_excited")
        self.assertIsNotNone(action.movement)
        self.assertEqual(action.movement.speed, 100)
        self.assertEqual(action.movement.elapse, 1)

    def test_relaxed_metric_triggers_slow_move(self):
        algorithm = PerformanceMetricThresholdAlgorithm(strong_threshold=0.5)
        values = [None, 0.2, None, 0.1, None, None, 0.0, None, 0.8]

        action = algorithm.evaluate([], values)

        self.assertEqual(action.event.state, "relaxed")
        self.assertIsNotNone(action.movement)
        self.assertEqual(action.movement.speed, 35)

    def test_stressed_metric_does_not_move(self):
        algorithm = PerformanceMetricThresholdAlgorithm(strong_threshold=0.5)
        values = [None, 0.2, None, 0.1, None, None, 0.9]

        action = algorithm.evaluate([], values)

        self.assertEqual(action.event.state, "stressed")
        self.assertIsNone(action.movement)

    def test_missing_engagement_reports_no_signal(self):
        algorithm = PerformanceMetricThresholdAlgorithm()
        values = [None, None, None, 0.7]

        action = algorithm.evaluate([], values)

        self.assertEqual(action.event.state, "no_signal")
        self.assertIsNone(action.movement)


class MentalCommandAlgorithmTests(unittest.TestCase):
    def test_push_command_above_power_threshold_moves(self):
        algorithm = MentalCommandAlgorithm(power_threshold=0.1)

        action = algorithm.evaluate(["act", "pow"], ["push", 0.8])

        self.assertEqual(action.event.state, "push")
        self.assertEqual(action.event.confidence, 0.8)
        self.assertIsNotNone(action.movement)
        self.assertEqual(action.movement.speed, 100)
        self.assertEqual(action.event.raw, {"act": "push", "pow": 0.8})

    def test_command_below_power_threshold_is_neutral(self):
        algorithm = MentalCommandAlgorithm(power_threshold=0.5)

        action = algorithm.evaluate([], ["push", 0.1])

        self.assertEqual(action.event.state, "neutral")
        self.assertIsNone(action.movement)

    def test_unknown_command_is_reported_without_movement(self):
        algorithm = MentalCommandAlgorithm(power_threshold=0.1)

        action = algorithm.evaluate([], ["spin", 0.9])

        self.assertEqual(action.event.state, "spin")
        self.assertIsNone(action.movement)


class AlgorithmRegistryTests(unittest.TestCase):
    def test_registry_lists_and_creates_algorithms(self):
        self.assertIn("performance-threshold", list_algorithms())
        self.assertIn("mental-command", list_algorithms())
        self.assertIsInstance(get_algorithm("performance-threshold"), PerformanceMetricThresholdAlgorithm)
        self.assertIsInstance(get_algorithm("mental-command"), MentalCommandAlgorithm)

    def test_unknown_algorithm_raises(self):
        with self.assertRaises(ValueError):
            get_algorithm("missing")


if __name__ == "__main__":
    unittest.main()
