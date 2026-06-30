"""CoderBot HTTP API client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import CoderBotConfig


@dataclass(frozen=True)
class CoderBotResult:
    """Result returned by CoderBot client operations."""

    status_code: int | None
    dry_run: bool
    message: str


class CoderBotClient:
    """Client for CoderBot commands with first-class dry-run support."""

    def __init__(self, config: CoderBotConfig, http_client: Any | None = None) -> None:
        self.config = config
        if http_client is None:
            import requests

            http_client = requests
        self.http_client = http_client

    def move(self, speed: int = 100, elapse: int = 1) -> CoderBotResult:
        """Move CoderBot or report what would be sent in dry-run mode."""

        payload = {"speed": speed, "elapse": elapse}
        url = f"{self.config.base_url.rstrip('/')}/control/move"
        if self.config.dry_run:
            message = f"DRY RUN: would POST {url} with {payload}"
            print(message)
            return CoderBotResult(status_code=None, dry_run=True, message=message)
        if not self.config.base_url:
            raise ValueError("CODERBOT_BASE_URL is required unless DRY_RUN=true")
        response = self.http_client.post(url, json=payload)
        message = f"Move response: {response.status_code}"
        print(message)
        return CoderBotResult(status_code=response.status_code, dry_run=False, message=message)

    def run_program(self, program_name: str) -> CoderBotResult:
        """Run a saved CoderBot program by name."""

        base_url = self.config.base_url.rstrip("/")
        get_url = f"{base_url}/programs/{program_name}"
        run_url = f"{base_url}/programs/{program_name}/run"
        if self.config.dry_run:
            message = f"DRY RUN: would fetch {get_url} and POST {run_url}"
            print(message)
            return CoderBotResult(status_code=None, dry_run=True, message=message)
        if not self.config.base_url:
            raise ValueError("CODERBOT_BASE_URL is required unless DRY_RUN=true")
        program_response = self.http_client.get(get_url)
        program_code = program_response.json().get("code")
        response = self.http_client.post(run_url, json={"name": program_name, "code": program_code})
        message = f"Run program response: {response.status_code}"
        print(message)
        return CoderBotResult(status_code=response.status_code, dry_run=False, message=message)
