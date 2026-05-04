"""AES-CBC protocol for Salus iT600 local gateway communication."""

from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .protocol import GatewayProtocol

_IV = bytes(
    [
        0x88,
        0xA6,
        0xB0,
        0x79,
        0x5D,
        0x85,
        0xDB,
        0xFC,
        0xE6,
        0xE0,
        0xB3,
        0xE9,
        0xA6,
        0x29,
        0x65,
        0x4B,
    ]
)


class AesCbcProtocol(GatewayProtocol):
    """AES-CBC protocol used by legacy UGE600/UG800 firmware."""

    def __init__(self, euid: str, *, aes128: bool = False) -> None:
        """Create an AES-CBC protocol instance."""
        self._euid = euid
        self._aes128 = aes128
        md5_key = hashlib.md5(f"Salus-{euid.lower()}".encode()).digest()
        self._key = md5_key if aes128 else md5_key + bytes(16)
        self._cipher = Cipher(algorithms.AES(self._key), modes.CBC(_IV))

    @property
    def name(self) -> str:
        """Return the protocol label."""
        return "AES-128-CBC" if self._aes128 else "AES-256-CBC"

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt a UTF-8 string with AES-CBC and PKCS7 padding."""
        encryptor = self._cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()
        return encryptor.update(padded) + encryptor.finalize()

    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt AES-CBC bytes and strip PKCS7 padding."""
        decryptor = self._cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plain = unpadder.update(padded) + unpadder.finalize()
        try:
            return plain.decode()
        except UnicodeDecodeError as exc:
            raise ValueError(f"Decrypted data is not valid UTF-8: {exc}") from exc

    def wrap_request(self, body_json: str) -> bytes:
        """Encrypt a JSON request body."""
        return self.encrypt(body_json)

    def unwrap_response(self, raw: bytes) -> str:
        """Strip any non-block-aligned trailer and decrypt the response."""
        remainder = len(raw) % 16
        if remainder:
            raw = raw[: len(raw) - remainder]
        return self.decrypt(raw)
