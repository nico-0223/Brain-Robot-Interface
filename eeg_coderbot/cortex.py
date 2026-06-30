"""Client wrapper for the Emotiv Cortex JSON-RPC WebSocket API."""

from __future__ import annotations

import json
from typing import Any, Iterable

from websockets.sync.client import connect

from .config import CortexConfig


class CortexClient:
    """Small JSON-RPC client for the Cortex WebSocket API.

    The WebSocket object is injectable to keep business logic unit-testable without
    opening a real connection to Emotiv Launcher/Cortex.
    """

    def __init__(self, config: CortexConfig, websocket: Any | None = None) -> None:
        self.config = config
        self.websocket = websocket

    def connect(self) -> None:
        """Open the WebSocket connection if one was not injected."""

        if self.websocket is None:
            self.websocket = connect(self.config.websocket_url)

    def close(self) -> None:
        """Close the WebSocket if supported by the underlying object."""

        if self.websocket is not None and hasattr(self.websocket, "close"):
            self.websocket.close()

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send one JSON-RPC request and return the decoded response."""

        if self.websocket is None:
            raise RuntimeError("Cortex WebSocket is not connected")
        payload: dict[str, Any] = {"id": 1, "jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self.websocket.send(json.dumps(payload))
        return json.loads(self.websocket.recv())

    def recv_json(self) -> dict[str, Any]:
        """Receive and decode one subscription message."""

        if self.websocket is None:
            raise RuntimeError("Cortex WebSocket is not connected")
        return json.loads(self.websocket.recv())

    def get_user_login(self) -> dict[str, Any]:
        return self.call("getUserLogin")

    def request_access(self) -> dict[str, Any]:
        return self.call(
            "requestAccess",
            {"clientId": self.config.client_id, "clientSecret": self.config.client_secret},
        )

    def authorize(self) -> dict[str, Any]:
        return self.call(
            "authorize",
            {"clientId": self.config.client_id, "clientSecret": self.config.client_secret},
        )

    def get_token(self) -> str:
        message = self.authorize()
        return message["result"]["cortexToken"]

    def get_license_info(self, cortex_token: str) -> dict[str, Any]:
        return self.call("getLicenseInfo", {"cortexToken": cortex_token})

    def query_headsets(self) -> list[dict[str, Any]]:
        message = self.call("queryHeadsets")
        return message.get("result", [])

    def get_first_headset_id(self) -> str:
        headsets = self.query_headsets()
        if not headsets:
            raise RuntimeError("No Emotiv headset found")
        return headsets[0]["id"]

    def create_session(self, cortex_token: str, headset_id: str) -> str:
        message = self.call(
            "createSession",
            {"cortexToken": cortex_token, "headset": headset_id, "status": "open"},
        )
        return message["result"]["id"]

    def create_record(self, cortex_token: str, session_id: str, title: str = "Cortex Record") -> dict[str, Any]:
        return self.call(
            "createRecord",
            {"cortexToken": cortex_token, "session": session_id, "title": title},
        ).get("result", {})

    def subscribe(self, cortex_token: str, session_id: str, streams: Iterable[str]) -> dict[str, Any]:
        return self.call(
            "subscribe",
            {"cortexToken": cortex_token, "session": session_id, "streams": list(streams)},
        )
