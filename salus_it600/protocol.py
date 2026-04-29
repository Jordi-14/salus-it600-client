"""Protocol abstractions for Salus gateway encrypted communication."""

from __future__ import annotations

import abc
import dataclasses
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

    @abc.abstractmethod
    async def connect(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        timeout: int | float,
    ) -> dict[str, Any]:
        """Perform a readall request and return the parsed response."""

    @abc.abstractmethod
    def wrap_request(self, body_json: str) -> bytes:
        """Prepare a JSON request body for the wire."""

    @abc.abstractmethod
    def unwrap_response(self, raw: bytes) -> str:
        """Decode a raw gateway response into a JSON string."""
