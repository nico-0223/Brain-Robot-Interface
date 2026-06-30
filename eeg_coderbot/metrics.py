"""Utilities for Emotiv metric-stream messages."""

from __future__ import annotations

from typing import Any, Sequence


def values_to_dict(columns: Sequence[str], values: Sequence[Any]) -> dict[str, Any]:
    """Map Cortex stream columns to received values."""

    return {column: values[index] for index, column in enumerate(columns) if index < len(values)}


def should_move_from_met_values(values: Sequence[Any]) -> bool:
    """Return whether performance metrics should trigger CoderBot movement.

    This preserves the previous behavior: move when engagement (`met[1]`) is not
    missing and engagement and excitement (`met[3]`) are both greater than zero.
    """

    if len(values) <= 3:
        return False
    engagement = values[1]
    excitement = values[3]
    if engagement is None or excitement is None:
        return False
    return engagement > 0 and excitement > 0
