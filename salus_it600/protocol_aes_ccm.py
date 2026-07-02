"""AES-256-CCM protocol for newer Salus UG800 gateway firmware.

The key derivation (EUID bytes + fixed suffix) and 8-byte nonce layout
(3 random + 2 counter + 3 timestamp bytes) below are dictated by the UG800
firmware and are reproduced here for interoperability only. They are NOT design
choices and MUST NOT be "hardened": the gateway expects exactly this scheme, so
any change silently breaks all local communication. The nonce is transmitted
alongside the ciphertext and AESCCM verifies the authentication tag on decrypt.
"""

from __future__ import annotations

import os
import struct
import time

from cryptography.hazmat.primitives.ciphers.aead import AESCCM

from .protocol import GatewayProtocol

_HARDCODED_SUFFIX = b"9a4ba190ac2b5139b32c3528"
_MAC_SIZE = 8
_NONCE_SIZE = 8


def _derive_key(euid: str) -> bytes:
    """Derive the AES-256-CCM key from the gateway EUID."""
    euid_bytes = bytearray(bytes.fromhex(euid.strip()))
    if len(euid_bytes) == 12:
        euid_bytes[3:3] = b"\x09\x02"
    return bytes(euid_bytes) + _HARDCODED_SUFFIX


def _build_nonce(counter: int) -> bytes:
    """Build an 8-byte nonce: 3 random bytes, 2-byte counter, 3-byte time."""
    rand_bytes = os.urandom(3)
    counter_bytes = struct.pack(">H", counter & 0xFFFF)
    timestamp = int(time.time()) & 0xFFFFFF
    timestamp_bytes = struct.pack(">I", timestamp)[1:]
    return rand_bytes + counter_bytes + timestamp_bytes


class AesCcmProtocol(GatewayProtocol):
    """AES-256-CCM protocol used by newer UG800 firmware."""

    def __init__(self, euid: str) -> None:
        """Create an AES-CCM protocol instance."""
        self._euid = euid
        self._key = _derive_key(euid)
        self._aesccm = AESCCM(self._key, tag_length=_MAC_SIZE)
        self._counter = 0

    @property
    def name(self) -> str:
        """Return the protocol label."""
        return "AES-256-CCM (UG800)"

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt plaintext into wire bytes: ciphertext+tag followed by nonce."""
        nonce = _build_nonce(self._counter)
        self._counter = (self._counter + 1) & 0xFFFF
        ct_and_tag = self._aesccm.encrypt(nonce, plaintext.encode(), None)
        return ct_and_tag + nonce

    def decrypt(self, data: bytes) -> str:
        """Decrypt wire bytes into a JSON string."""
        if len(data) <= _NONCE_SIZE + _MAC_SIZE:
            raise ValueError(
                f"Data too short for CCM ({len(data)} bytes, "
                f"need > {_NONCE_SIZE + _MAC_SIZE})"
            )
        ct_and_tag = data[:-_NONCE_SIZE]
        nonce = data[-_NONCE_SIZE:]
        return self._aesccm.decrypt(nonce, ct_and_tag, None).decode()

    def wrap_request(self, body_json: str) -> bytes:
        """Encrypt a JSON request body."""
        return self.encrypt(body_json)

    def unwrap_response(self, raw: bytes) -> str:
        """Decrypt a raw gateway response."""
        return self.decrypt(raw)
