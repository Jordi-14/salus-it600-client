"""Protocol abstractions for Salus gateway encrypted communication."""

from __future__ import annotations

import abc
import asyncio
import dataclasses
import json
from typing import Any

import aiohttp

REJECT_FRAME_LENGTH = 33
REJECT_TRAILER = 0xAE
NEW_PROTOCOL_TRAILER = 0xAF
_KNOWN_TRAILERS = frozenset({REJECT_TRAILER, NEW_PROTOCOL_TRAILER})


@dataclasses.dataclass(frozen=True)
class Frame33:
    """Parsed 33-byte gateway response frame."""

    payload: bytes
    counter: int
    tag: bytes
    trailer: int

    @property
    def is_reject(self) -> bool:
        """Return whether this is a protocol reject frame."""
        return self.trailer == REJECT_TRAILER

    @property
    def is_new_protocol(self) -> bool:
        """Return whether this is a new-protocol marker frame."""
        return self.trailer == NEW_PROTOCOL_TRAILER

    @property
    def trailer_name(self) -> str:
        """Return a readable trailer label."""
        if self.trailer == REJECT_TRAILER:
            return "reject"
        if self.trailer == NEW_PROTOCOL_TRAILER:
            return "new-protocol"
        return f"unknown(0x{self.trailer:02X})"


def parse_frame_33(raw: bytes) -> Frame33 | None:
    """Parse a known 33-byte gateway frame, or return None."""
    if len(raw) != REJECT_FRAME_LENGTH or raw[-1] not in _KNOWN_TRAILERS:
        return None
    return Frame33(
        payload=raw[:28],
        counter=raw[28],
        tag=raw[29:32],
        trailer=raw[32],
    )


def is_reject_frame(raw: bytes) -> bool:
    """Return True if raw bytes are a protocol reject frame."""
    return len(raw) == REJECT_FRAME_LENGTH and raw[-1] == REJECT_TRAILER


def is_new_protocol_frame(raw: bytes) -> bool:
    """Return True if raw bytes are a new-protocol marker frame."""
    return len(raw) == REJECT_FRAME_LENGTH and raw[-1] == NEW_PROTOCOL_TRAILER


class GatewayProtocol(abc.ABC):
    """Contract implemented by Salus gateway encryption protocols."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return a human-readable protocol label."""

    @abc.abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt a JSON string into wire bytes."""

    @abc.abstractmethod
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt wire bytes into a JSON string."""

    async def connect(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        timeout: int | float,
    ) -> dict[str, Any]:
        """Perform a readall request and return the parsed response."""
        url = f"http://{host}:{port}/deviceid/read"
        encrypted = self.wrap_request(json.dumps({"requestAttr": "readall"}))

        async with asyncio.timeout(timeout):
            resp = await session.post(
                url,
                data=encrypted,
                headers={"content-type": "application/json"},
            )
            raw = await resp.read()

        if resp.status != 200:
            raise ValueError(f"HTTP {resp.status}")

        frame = parse_frame_33(raw)
        if frame is not None:
            if frame.is_reject:
                raise ValueError("Gateway returned a reject frame")
            raise ValueError("Gateway returned a new-protocol frame")

        try:
            text = self.unwrap_response(raw)
        except Exception as exc:
            raise ValueError(
                f"Decryption failed ({type(exc).__name__}: {exc})"
            ) from exc

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Decrypted response is not valid JSON: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                f"Decrypted response is not a JSON object: {type(parsed).__name__}"
            )

        result: dict[str, Any] = parsed
        if result.get("status") != "success":
            raise ValueError(f"status={result.get('status')}")
        return result

    @abc.abstractmethod
    def wrap_request(self, body_json: str) -> bytes:
        """Prepare a JSON request body for the wire."""

    @abc.abstractmethod
    def unwrap_response(self, raw: bytes) -> str:
        """Decode a raw gateway response into a JSON string."""
