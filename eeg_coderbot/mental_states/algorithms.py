"""Algorithms that interpret Emotiv-classified mental states.

The algorithms in this module intentionally consume Cortex stream values that are
already classified by Emotiv, such as performance metrics (``met``) and mental
commands (``com``). They do not infer mental states directly from raw EEG.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class MentalStateEvent:
    """A normalized mental-state classification from an Emotiv stream."""

    state: str
    confidence: float | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class MovementPlan:
    """CoderBot movement parameters associated with a mental state."""

    speed: int
    elapse: int
    reason: str


@dataclass(frozen=True)
class MentalStateAction:
    """The movement decision produced by a mental-state algorithm."""

    event: MentalStateEvent
    movement: MovementPlan | None


class MentalStateAlgorithm(Protocol):
    """Interface for mental-state readers backed by Emotiv stream values."""

    name: str
    stream_name: str

    def evaluate(self, columns: Sequence[str], values: Sequence[Any]) -> MentalStateAction:
        """Classify one stream message and return the CoderBot action to take."""


class PerformanceMetricThresholdAlgorithm:
    """Map Emotiv performance metrics to simple CoderBot movement plans.

    Cortex ``met`` streams include Emotiv-classified performance metrics. The
    original script used engagement and excitement indices from this stream; this
    algorithm keeps that behavior and adds readable state names for other metrics
    where they are available.
    """

    name = "performance-threshold"
    stream_name = "met"

    # Indices match the metric positions used in the original script.
    ENGAGEMENT_INDEX = 1
    EXCITEMENT_INDEX = 3
    STRESS_INDEX = 6
    RELAXATION_INDEX = 8
    INTEREST_INDEX = 10
    FOCUS_INDEX = 12

    def __init__(self, active_threshold: float = 0.0, strong_threshold: float = 0.5) -> None:
        self.active_threshold = active_threshold
        self.strong_threshold = strong_threshold

    def evaluate(self, columns: Sequence[str], values: Sequence[Any]) -> MentalStateAction:
        metrics = _values_to_metric_dict(columns, values)
        engagement = _value_at(values, self.ENGAGEMENT_INDEX)
        excitement = _value_at(values, self.EXCITEMENT_INDEX)
        stress = _value_at(values, self.STRESS_INDEX)
        relaxation = _value_at(values, self.RELAXATION_INDEX)
        interest = _value_at(values, self.INTEREST_INDEX)
        focus = _value_at(values, self.FOCUS_INDEX)

        if engagement is None:
            return _action("no_signal", None, metrics, None)
        if _above(focus, self.strong_threshold):
            return _action("focused", focus, metrics, MovementPlan(80, 1, "focused metric above threshold"))
        if _above(relaxation, self.strong_threshold):
            return _action("relaxed", relaxation, metrics, MovementPlan(35, 1, "relaxation metric above threshold"))
        if _above(stress, self.strong_threshold):
            return _action("stressed", stress, metrics, None)
        if _above(engagement, self.active_threshold) and _above(excitement, self.active_threshold):
            confidence = min(float(engagement), float(excitement))
            return _action("engaged_excited", confidence, metrics, MovementPlan(100, 1, "engagement and excitement are positive"))
        if _above(interest, self.strong_threshold):
            return _action("interested", interest, metrics, MovementPlan(60, 1, "interest metric above threshold"))
        return _action("neutral", engagement, metrics, None)


class MentalCommandAlgorithm:
    """Map Emotiv mental-command classifications to CoderBot movement plans.

    Cortex ``com`` streams report an Emotiv-classified action and power. The
    movement plans below intentionally use the existing CoderBot ``move`` command
    with different speeds/durations instead of assuming undocumented turn/stop
    endpoints exist.
    """

    name = "mental-command"
    stream_name = "com"

    ACTION_INDEX = 0
    POWER_INDEX = 1

    def __init__(self, power_threshold: float = 0.1) -> None:
        self.power_threshold = power_threshold

    def evaluate(self, columns: Sequence[str], values: Sequence[Any]) -> MentalStateAction:
        metrics = _values_to_metric_dict(columns, values)
        action = _value_at(values, self.ACTION_INDEX)
        power = _value_at(values, self.POWER_INDEX)
        state = str(action or "neutral")
        confidence = float(power) if isinstance(power, (int, float)) else None
        if confidence is None or confidence < self.power_threshold:
            return _action("neutral", confidence, metrics, None)

        movement = {
            "push": MovementPlan(100, 1, "mental command push"),
            "pull": MovementPlan(40, 2, "mental command pull"),
            "lift": MovementPlan(70, 1, "mental command lift"),
            "drop": MovementPlan(25, 1, "mental command drop"),
            "left": MovementPlan(50, 1, "mental command left"),
            "right": MovementPlan(50, 1, "mental command right"),
        }.get(state)
        return _action(state, confidence, metrics, movement)


def list_algorithms() -> tuple[str, ...]:
    """Return supported mental-state algorithm names."""

    return (PerformanceMetricThresholdAlgorithm.name, MentalCommandAlgorithm.name)


def get_algorithm(name: str) -> MentalStateAlgorithm:
    """Create a mental-state algorithm by CLI/configuration name."""

    if name == PerformanceMetricThresholdAlgorithm.name:
        return PerformanceMetricThresholdAlgorithm()
    if name == MentalCommandAlgorithm.name:
        return MentalCommandAlgorithm()
    raise ValueError(f"Unknown mental-state algorithm: {name}")


def _action(
    state: str,
    confidence: float | None,
    raw: dict[str, Any],
    movement: MovementPlan | None,
) -> MentalStateAction:
    return MentalStateAction(MentalStateEvent(state=state, confidence=confidence, raw=raw), movement)


def _value_at(values: Sequence[Any], index: int) -> Any:
    return values[index] if index < len(values) else None


def _above(value: Any, threshold: float) -> bool:
    return isinstance(value, (int, float)) and value > threshold


def _values_to_metric_dict(columns: Sequence[str], values: Sequence[Any]) -> dict[str, Any]:
    return {column: values[index] for index, column in enumerate(columns) if index < len(values)}
