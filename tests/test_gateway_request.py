"""Tests for Salus gateway request handling."""

import asyncio
import json
import unittest

from salus_it600.const import FAN_MODE_MEDIUM
from salus_it600.exceptions import IT600CommandError, IT600ConnectionError
from salus_it600.gateway import IT600Gateway
from salus_it600.models import ClimateDevice


class PassthroughEncryptor:
    """Minimal encryptor for request tests."""

    def encrypt(self, plain: str) -> bytes:
        return plain.encode("utf-8")

    def decrypt(self, cypher: bytes) -> str:
        return cypher.decode("utf-8")


class FakeResponse:
    """Minimal aiohttp response stand-in."""

    def __init__(self, payload):
        self._payload = payload

    async def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class FakeSession:
    """Minimal aiohttp session stand-in."""

    def __init__(self, payload: dict | None = None, error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.post_calls = []

    async def post(self, url: str, **kwargs) -> FakeResponse:
        self.post_calls.append((url, kwargs))
        if self.error is not None:
            raise self.error
        return FakeResponse(self.payload)


def make_gateway(session: FakeSession) -> IT600Gateway:
    """Create a gateway using fake network and encryption layers."""
    gateway = IT600Gateway(host="192.0.2.10", euid="001E5E0D32906128", session=session)
    gateway._encryptor = PassthroughEncryptor()
    return gateway


def make_climate_device(device_id: str = "climate-1") -> ClimateDevice:
    """Create a minimal climate device for command tests."""
    return ClimateDevice(
        available=True,
        name="Climate",
        unique_id=device_id,
        temperature_unit="C",
        precision=0.1,
        current_temperature=20.0,
        target_temperature=21.0,
        max_temp=35.0,
        min_temp=5.0,
        current_humidity=None,
        hvac_mode="Heat",
        hvac_action="Idle",
        hvac_modes=[],
        preset_mode="Permanent Hold",
        preset_modes=[],
        fan_mode=None,
        fan_modes=[],
        locked=None,
        supported_features=0,
        device_class="temperature",
        data={"UniID": device_id},
        manufacturer="SALUS",
        model="FC600",
        sw_version=None,
    )


class TestGatewayRequest(unittest.IsolatedAsyncioTestCase):
    async def test_make_encrypted_request_returns_success_response(self):
        session = FakeSession({"status": "success", "id": []})
        gateway = make_gateway(session)

        response = await gateway._make_encrypted_request(
            "read",
            {"requestAttr": "readall"},
        )

        self.assertEqual({"status": "success", "id": []}, response)
        self.assertEqual("http://192.0.2.10:80/deviceid/read", session.post_calls[0][0])
        self.assertEqual(
            b'{"requestAttr": "readall"}',
            session.post_calls[0][1]["data"],
        )

    async def test_make_encrypted_request_preserves_gateway_rejection_error(self):
        session = FakeSession({"status": "fail", "id": [{"status": "fail"}]})
        gateway = make_gateway(session)

        with self.assertLogs("salus_it600", level="ERROR"):
            with self.assertRaises(IT600CommandError) as context:
                await gateway._make_encrypted_request(
                    "write",
                    {"requestAttr": "write", "id": []},
                )

        message = str(context.exception)
        self.assertIn("gateway rejected 'write' command", message)
        self.assertIn("response", message)
        self.assertNotIn("Unknown error", message)

    async def test_make_encrypted_request_maps_timeout_to_connection_error(self):
        session = FakeSession(error=asyncio.TimeoutError())
        gateway = make_gateway(session)

        with self.assertLogs("salus_it600", level="ERROR"):
            with self.assertRaises(IT600ConnectionError) as context:
                await gateway._make_encrypted_request(
                    "read",
                    {"requestAttr": "readall"},
                )

        self.assertIn("timeout", str(context.exception))

    async def test_make_encrypted_request_rejects_non_object_response(self):
        session = FakeSession(["not", "an", "object"])
        gateway = make_gateway(session)

        with self.assertRaises(IT600CommandError) as context:
            await gateway._make_encrypted_request(
                "read",
                {"requestAttr": "readall"},
            )

        self.assertIn("must be an object", str(context.exception))

    async def test_make_encrypted_request_rejects_missing_status(self):
        session = FakeSession({"id": []})
        gateway = make_gateway(session)

        with self.assertRaises(IT600CommandError) as context:
            await gateway._make_encrypted_request(
                "read",
                {"requestAttr": "readall"},
            )

        self.assertIn("missing 'status'", str(context.exception))

    async def test_poll_status_rejects_readall_without_device_list(self):
        session = FakeSession({"status": "success"})
        gateway = make_gateway(session)

        with self.assertRaises(IT600CommandError) as context:
            await gateway.poll_status()

        self.assertIn("missing list field 'id'", str(context.exception))

    async def test_poll_status_rejects_non_object_device_entries(self):
        session = FakeSession({"status": "success", "id": ["bad-device"]})
        gateway = make_gateway(session)

        with self.assertRaises(IT600CommandError) as context:
            await gateway.poll_status()

        self.assertIn("non-object device entries", str(context.exception))

    async def test_set_climate_device_fan_mode_maps_medium_mode(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        await gateway.set_climate_device_fan_mode("climate-1", FAN_MODE_MEDIUM)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual("write", request["requestAttr"])
        self.assertEqual({"FanMode": 2}, request["id"][0]["sFanS"])
        self.assertEqual({"UniID": "climate-1"}, request["id"][0]["data"])


if __name__ == "__main__":
    unittest.main()
