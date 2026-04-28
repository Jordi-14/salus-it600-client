"""Tests for Salus gateway request handling."""

import asyncio
import json
import unittest

from salus_it600.const import (
    CURRENT_HVAC_IDLE,
    FAN_MODE_AUTO,
    FAN_MODE_HIGH,
    FAN_MODE_LOW,
    FAN_MODE_MEDIUM,
    FAN_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_ECO,
    PRESET_FOLLOW_SCHEDULE,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_TEMPORARY_HOLD,
)
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

    async def get(self, url: str) -> FakeResponse:
        return FakeResponse({})


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
        hvac_mode=HVAC_MODE_HEAT,
        hvac_action=CURRENT_HVAC_IDLE,
        hvac_modes=[HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO],
        preset_mode=PRESET_PERMANENT_HOLD,
        preset_modes=[
            PRESET_OFF,
            PRESET_PERMANENT_HOLD,
            PRESET_ECO,
            PRESET_TEMPORARY_HOLD,
            PRESET_FOLLOW_SCHEDULE,
        ],
        fan_mode=None,
        fan_modes=[
            FAN_MODE_AUTO,
            FAN_MODE_HIGH,
            FAN_MODE_MEDIUM,
            FAN_MODE_LOW,
            FAN_MODE_OFF,
        ],
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

    async def test_connect_returns_gateway_mac(self):
        session = FakeSession(
            {
                "status": "success",
                "id": [
                    {"sGateway": {"NetworkLANMAC": "AA:BB:CC:DD:EE:FF"}},
                ],
            }
        )
        gateway = make_gateway(session)

        mac = await gateway.connect()

        self.assertEqual("AA:BB:CC:DD:EE:FF", mac)

    async def test_connect_rejects_response_without_gateway_info(self):
        session = FakeSession({"status": "success", "id": []})
        gateway = make_gateway(session)

        with self.assertRaises(IT600CommandError) as context:
            await gateway.connect()

        self.assertIn(
            "response did not contain gateway information", str(context.exception)
        )

    async def test_set_climate_device_fan_mode_maps_medium_mode(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        await gateway.set_climate_device_fan_mode("climate-1", FAN_MODE_MEDIUM)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual("write", request["requestAttr"])
        self.assertEqual({"FanMode": 2}, request["id"][0]["sFanS"])
        self.assertEqual({"UniID": "climate-1"}, request["id"][0]["data"])

    async def test_set_it600_climate_mode_off_writes_standby_hold(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()._replace(
            model="HTRP-RF(50)",
            hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
        )

        await gateway.set_climate_device_mode("climate-1", HVAC_MODE_OFF)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetHoldType": 7}, request["id"][0]["sIT600TH"])

    async def test_set_fc600_climate_mode_cool_writes_system_mode(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        await gateway.set_climate_device_mode("climate-1", HVAC_MODE_COOL)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetSystemMode": 3}, request["id"][0]["sTherS"])

    async def test_set_fc600_eco_preset_writes_hold_type(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        await gateway.set_climate_device_preset("climate-1", PRESET_ECO)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetHoldType": 10}, request["id"][0]["sComm"])

    async def test_set_trv3rf_preset_writes_scomm_hold_type(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["trv-1"] = make_climate_device("trv-1")._replace(
            model="TRV3RF",
            hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
            preset_modes=[PRESET_FOLLOW_SCHEDULE, PRESET_PERMANENT_HOLD, PRESET_OFF],
        )

        await gateway.set_climate_device_preset("trv-1", PRESET_PERMANENT_HOLD)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetHoldType": 2}, request["id"][0]["sComm"])

    async def test_set_trv3rf_mode_writes_scomm_hold_type(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["trv-1"] = make_climate_device("trv-1")._replace(
            model="TRV3RF",
            hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
        )

        await gateway.set_climate_device_mode("trv-1", HVAC_MODE_HEAT)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetHoldType": 2}, request["id"][0]["sComm"])

    async def test_set_fc600_temperature_in_cool_mode_writes_cooling_setpoint(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()._replace(
            hvac_mode=HVAC_MODE_COOL,
        )

        await gateway.set_climate_device_temperature("climate-1", 22.3)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual(
            {"SetCoolingSetpoint_x100": 2250},
            request["id"][0]["sTherS"],
        )

    async def test_set_climate_device_locked_writes_lock_key(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        await gateway.set_climate_device_locked("climate-1", True)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual({"SetLockKey": 1}, request["id"][0]["sTherUIS"])

    async def test_set_trv3rf_temperature_writes_sthers_payload(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["trv-1"] = make_climate_device("trv-1")._replace(
            model="TRV3RF",
            hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
            min_temp=5.0,
            max_temp=35.0,
        )

        await gateway.set_climate_device_temperature("trv-1", 21.2)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual(
            {"SetHeatingSetpoint_x100": 2100},
            request["id"][0]["sTherS"],
        )

    async def test_fetch_sq610_properties_returns_flattened_raw_payload(self):
        session = FakeSession(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "sq610-1"},
                        "sIT600TH": {
                            "SystemMode": 3,
                            "CoolingSetpoint_x100": 2200,
                        },
                    }
                ],
            }
        )
        gateway = make_gateway(session)
        gateway._climate_devices["sq610-1"] = make_climate_device("sq610-1")._replace(
            model="SQ610RF"
        )

        raw_props = await gateway.fetch_sq610_properties(["sq610-1"])

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual("deviceid", request["requestAttr"])
        self.assertEqual({"UniID": "sq610-1"}, request["id"][0]["data"])
        self.assertEqual(
            {
                "UniID": "sq610-1",
                "SystemMode": 3,
                "CoolingSetpoint_x100": 2200,
            },
            raw_props["sq610-1"],
        )

    async def test_write_sq610_property_writes_sit600th_payload(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["sq610-1"] = make_climate_device("sq610-1")._replace(
            model="SQ610RF"
        )

        await gateway.write_sq610_property("sq610-1", "SetSystemMode", 3)

        request = json.loads(session.post_calls[0][1]["data"])
        self.assertEqual("write", request["requestAttr"])
        self.assertEqual({"UniID": "sq610-1"}, request["id"][0]["data"])
        self.assertEqual({"SetSystemMode": 3}, request["id"][0]["sIT600TH"])

    async def test_public_commands_reject_blank_device_id(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)

        with self.assertRaises(ValueError):
            await gateway.turn_on_switch_device(" ")

    async def test_public_commands_reject_missing_devices(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)

        with self.assertRaises(KeyError):
            await gateway.turn_on_switch_device("missing-switch")

    async def test_set_cover_position_rejects_invalid_range(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)

        with self.assertRaises(ValueError):
            await gateway.set_cover_position("cover-1", 101)

    async def test_set_climate_device_fan_mode_rejects_unsupported_mode(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        with self.assertRaises(ValueError):
            await gateway.set_climate_device_fan_mode("climate-1", "Turbo")

    async def test_set_climate_device_fan_mode_rejects_devices_without_fan_modes(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()._replace(
            fan_modes=None
        )

        with self.assertRaises(ValueError):
            await gateway.set_climate_device_fan_mode("climate-1", FAN_MODE_MEDIUM)

    async def test_set_climate_device_temperature_rejects_out_of_range(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)
        gateway._climate_devices["climate-1"] = make_climate_device()

        with self.assertRaises(ValueError):
            await gateway.set_climate_device_temperature("climate-1", 50.0)

    async def test_callback_registration_rejects_non_callable(self):
        session = FakeSession({"status": "success", "id": [{"status": "success"}]})
        gateway = make_gateway(session)

        with self.assertRaises(TypeError):
            await gateway.add_switch_update_callback("not-callable")


if __name__ == "__main__":
    unittest.main()
