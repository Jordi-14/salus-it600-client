"""Compatibility encryptor for Salus iT600 local mode communication."""

from .protocol_aes_cbc import AesCbcProtocol


class IT600Encryptor:
    """Legacy AES-CBC encryptor wrapper."""

    def __init__(self, euid: str):
        self._protocol = AesCbcProtocol(euid)

    def encrypt(self, plain: str) -> bytes:
        return self._protocol.encrypt(plain)

    def decrypt(self, cypher: bytes) -> str:
        return self._protocol.decrypt(cypher)
