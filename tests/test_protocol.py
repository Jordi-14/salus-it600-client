"""Tests for Salus gateway protocol helpers."""

from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from salus_it600.exceptions import IT600UnsupportedFirmwareError
from salus_it600.gateway import IT600Gateway
from salus_it600.protocol import is_new_protocol_frame, is_reject_frame, parse_frame_33
from salus_it600.protocol_aes_cbc import AesCbcProtocol
from salus_it600.protocol_aes_ccm import AesCcmProtocol, _derive_key


class FakeResponse:
    """Minimal response object for protocol tests."""

    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, *exc_info) -> None:
        self.exited = True

    async def read(self) -> bytes:
        return self._body


class FakeSession:
    """Minimal aiohttp session stand-in."""

    def __init__(self, body: bytes = b"", status: int = 200) -> None:
        self.body = body
        self.status = status
        self.post_calls = []
        self.get_calls = []
        self.responses = []

    def post(self, url: str, **kwargs):
        self.post_calls.append((url, kwargs))
        response = FakeResponse(self.body, self.status)
        self.responses.append(response)
        return response

    def get(self, url: str, **kwargs):
        self.get_calls.append((url, kwargs))
        response = FakeResponse(b"ok")
        self.responses.append(response)
        return response


class FakeProtocol:
    """Protocol fake for gateway auto-detection tests."""

    def __init__(self, name: str, result=None, error: Exception | None = None) -> None:
        self.name = name
        self.result = result
        self.error = error

    async def connect(self, *_args, **_kwargs):
        if self.error is not None:
            raise self.error
        return self.result

    def wrap_request(self, body_json: str) -> bytes:
        return f"wrapped:{body_json}".encode()

    def unwrap_response(self, raw: bytes) -> str:
        return raw.decode().removeprefix("wrapped-response:")


class TestFrameHelpers(unittest.TestCase):
    """Test 33-byte gateway frame helpers."""

    def test_reject_frame(self) -> None:
        raw = bytes(32) + b"\xae"
        frame = parse_frame_33(raw)

        self.assertTrue(is_reject_frame(raw))
        self.assertFalse(is_new_protocol_frame(raw))
        self.assertIsNotNone(frame)
        self.assertTrue(frame.is_reject)
        self.assertEqual("reject", frame.trailer_name)

    def test_new_protocol_frame(self) -> None:
        raw = bytes(32) + b"\xaf"
        frame = parse_frame_33(raw)

        self.assertFalse(is_reject_frame(raw))
        self.assertTrue(is_new_protocol_frame(raw))
        self.assertIsNotNone(frame)
        self.assertTrue(frame.is_new_protocol)
        self.assertEqual("new-protocol", frame.trailer_name)


class TestProtocols(unittest.IsolatedAsyncioTestCase):
    """Test AES protocol implementations."""

    EUID = "001E5E0D32906128"

    def test_aes_cbc_roundtrip(self) -> None:
        protocol = AesCbcProtocol(self.EUID)
        payload = '{"requestAttr":"readall"}'

        self.assertEqual(payload, protocol.decrypt(protocol.encrypt(payload)))

    def test_aes_ccm_roundtrip(self) -> None:
        protocol = AesCcmProtocol(self.EUID)
        payload = '{"requestAttr":"readall"}'

        self.assertEqual(payload, protocol.decrypt(protocol.encrypt(payload)))

    def test_aes_ccm_key_derivation(self) -> None:
        key = _derive_key(self.EUID)

        self.assertEqual(32, len(key))
        self.assertEqual(bytes.fromhex(self.EUID), key[:8])
        self.assertEqual(b"9a4ba190ac2b5139b32c3528", key[8:])

    async def test_aes_cbc_connect_success(self) -> None:
        protocol = AesCbcProtocol(self.EUID)
        response = {"status": "success", "id": [{"sGateway": {"NetworkLANMAC": "AA"}}]}
        session = FakeSession(protocol.encrypt(json.dumps(response)))

        result = await protocol.connect(session, "192.0.2.10", 80, 5)

        self.assertEqual("success", result["status"])
        self.assertEqual(5, session.post_calls[0][1]["timeout"].total)
        self.assertTrue(session.responses[0].entered)
        self.assertTrue(session.responses[0].exited)

    async def test_aes_ccm_connect_success(self) -> None:
        protocol = AesCcmProtocol(self.EUID)
        response = {"status": "success", "id": [{"sGateway": {"NetworkLANMAC": "AA"}}]}
        session = FakeSession(protocol.encrypt(json.dumps(response)))

        result = await protocol.connect(session, "192.0.2.10", 80, 5)

        self.assertEqual("success", result["status"])


class TestGatewayProtocolDetection(unittest.IsolatedAsyncioTestCase):
    """Test gateway protocol auto-detection."""

    async def test_connect_uses_first_successful_protocol(self) -> None:
        success = FakeProtocol(
            "second",
            {"status": "success", "id": [{"sGateway": {"NetworkLANMAC": "AA"}}]},
        )
        gateway = IT600Gateway(
            host="192.0.2.10",
            euid="001E5E0D32906128",
            session=SimpleNamespace(),
        )
        gateway._protocol_candidates = lambda: [
            FakeProtocol("first", error=ValueError("bad padding")),
            success,
        ]

        mac = await gateway.connect()

        self.assertEqual("AA", mac)
        self.assertIs(gateway._protocol, success)

    async def test_reject_frames_raise_unsupported_firmware(self) -> None:
        session = FakeSession()
        gateway = IT600Gateway(
            host="192.0.2.10",
            euid="001E5E0D32906128",
            session=session,
        )
        gateway._protocol_candidates = lambda: [
            FakeProtocol("first", error=ValueError("Gateway returned a reject frame")),
            FakeProtocol("second", error=ValueError("Gateway returned a reject frame")),
        ]

        with self.assertRaises(IT600UnsupportedFirmwareError):
            await gateway.connect()

    async def test_detected_protocol_is_used_for_requests(self) -> None:
        protocol = FakeProtocol("fake")
        session = FakeSession(b'wrapped-response:{"status": "success", "id": []}')
        gateway = IT600Gateway(
            host="192.0.2.10",
            euid="001E5E0D32906128",
            session=session,
        )
        gateway._protocol = protocol

        response = await gateway._make_encrypted_request(
            "read",
            {"requestAttr": "readall"},
        )

        self.assertEqual({"status": "success", "id": []}, response)
        self.assertEqual(
            b'wrapped:{"requestAttr": "readall"}',
            session.post_calls[0][1]["data"],
        )


if __name__ == "__main__":
    unittest.main()
