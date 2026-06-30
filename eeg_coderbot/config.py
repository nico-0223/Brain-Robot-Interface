"""Centralized configuration for the Emotiv/CoderBot scripts."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class CortexConfig:
    """Connection and credential settings for Emotiv Cortex."""

    websocket_url: str = "wss://localhost:6868"
    client_id: str = ""
    client_secret: str = ""


@dataclass(frozen=True)
class CoderBotConfig:
    """HTTP API settings for CoderBot."""

    base_url: str = ""
    dry_run: bool = False


@dataclass(frozen=True)
class MovementConfig:
    """Parameters used when sending CoderBot movement commands."""

    speed: int = 100
    elapse: int = 1
    experiment_seconds: float = 120.0


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""

    cortex: CortexConfig
    coderbot: CoderBotConfig
    movement: MovementConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build configuration from environment variables."""

        return cls(
            cortex=CortexConfig(
                websocket_url=os.getenv("EMOTIV_CORTEX_URL", CortexConfig.websocket_url),
                client_id=os.getenv("EMOTIV_CLIENT_ID", ""),
                client_secret=os.getenv("EMOTIV_CLIENT_SECRET", ""),
            ),
            coderbot=CoderBotConfig(
                base_url=os.getenv("CODERBOT_BASE_URL", ""),
                dry_run=_env_bool("DRY_RUN", False),
            ),
            movement=MovementConfig(
                speed=_env_int("CODERBOT_MOVE_SPEED", 100),
                elapse=_env_int("CODERBOT_MOVE_ELAPSE", 1),
                experiment_seconds=_env_float("EXPERIMENT_SECONDS", 120.0),
            ),
        )
