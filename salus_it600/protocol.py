"""Protocol abstractions for Salus gateway encrypted communication."""

from __future__ import annotations

import abc
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


class ProtocolDetectionError(Exception):
    """Base class for gateway protocol probing failures."""


class ProtocolHttpError(ProtocolDetectionError):
    """Gateway returned an HTTP error while probing a protocol candidate."""

    def __init__(self, status: int) -> None:
        """Create an HTTP protocol probing error."""
        self.status = status
        super().__init__(f"Gateway returned HTTP {status}")


class ProtocolFrameError(ProtocolDetectionError):
    """Gateway returned a typed protocol marker frame."""

    def __init__(self, frame: Frame33 | None, message: str) -> None:
        """Create a protocol frame error."""
        self.frame = frame
        super().__init__(message)


class ProtocolRejected(ProtocolFrameError):
    """Gateway rejected this protocol candidate."""

    def __init__(self, frame: Frame33 | None = None) -> None:
        """Create a protocol rejected error."""
        super().__init__(frame, "Gateway returned a reject frame")


class ProtocolUnsupported(ProtocolFrameError):
    """Gateway reported a protocol this client does not support."""

    def __init__(self, frame: Frame33 | None = None) -> None:
        """Create an unsupported protocol error."""
        if frame is None:
            message = "Gateway returned an unsupported protocol frame"
        else:
            message = f"Gateway returned a {frame.trailer_name} frame"
        super().__init__(frame, message)


class ProtocolDecryptFailed(ProtocolDetectionError):
    """Protocol candidate could not decrypt the gateway response."""

    def __init__(self, cause: Exception) -> None:
        """Create a decryption failure."""
        self.cause = cause
        super().__init__(f"Decryption failed ({type(cause).__name__}: {cause})")


class ProtocolInvalidResponse(ProtocolDetectionError):
    """Protocol candidate produced an invalid gateway response."""

    def __init__(self, reason: str) -> None:
        """Create an invalid response error."""
        self.reason = reason
        super().__init__(reason)


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
        timeout: float,
    ) -> dict[str, Any]:
        """Perform a readall request and return the parsed response."""
        url = f"http://{host}:{port}/deviceid/read"
        encrypted = self.wrap_request(json.dumps({"requestAttr": "readall"}))
        request_timeout = aiohttp.ClientTimeout(total=timeout)

        async with session.post(
            url,
            data=encrypted,
            headers={"content-type": "application/json"},
            timeout=request_timeout,
        ) as resp:
            raw = await resp.read()
            status = resp.status

        if status != 200:
            raise ProtocolHttpError(status)

        frame = parse_frame_33(raw)
        if frame is not None:
            if frame.is_reject:
                raise ProtocolRejected(frame)
            raise ProtocolUnsupported(frame)

        try:
            text = self.unwrap_response(raw)
        except Exception as exc:
            raise ProtocolDecryptFailed(exc) from exc

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProtocolInvalidResponse(
                f"Decrypted response is not valid JSON: {exc}"
            ) from exc

        if not isinstance(parsed, dict):
            raise ProtocolInvalidResponse(
                f"Decrypted response is not a JSON object: {type(parsed).__name__}"
            )

        result: dict[str, Any] = parsed
        if result.get("status") != "success":
            raise ProtocolInvalidResponse(f"status={result.get('status')}")
        return result

    @abc.abstractmethod
    def wrap_request(self, body_json: str) -> bytes:
        """Prepare a JSON request body for the wire."""

    @abc.abstractmethod
    def unwrap_response(self, raw: bytes) -> str:
        """Decode a raw gateway response into a JSON string."""
