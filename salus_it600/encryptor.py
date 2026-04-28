"""Encryptor for Salus iT600 local mode communication."""

import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class IT600Encryptor:
    iv = bytes(
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

    def __init__(self, euid: str):
        key: bytes = hashlib.md5(
            f"Salus-{euid.lower()}".encode("utf-8")
        ).digest() + bytes([0] * 16)
        self.cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), default_backend())

    def encrypt(self, plain: str) -> bytes:
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data: bytes = padder.update(plain.encode("utf-8")) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt(self, cypher: bytes) -> str:
        decryptor = self.cipher.decryptor()
        padded_data: bytes = decryptor.update(cypher) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plain: bytes = unpadder.update(padded_data) + unpadder.finalize()
        return plain.decode("utf-8")
