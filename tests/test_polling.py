"""Integration-style tests for complete gateway polling cycles."""

import unittest

from salus_it600.gateway import IT600Gateway


def make_gateway_with_responses(
    *responses: dict,
) -> tuple[IT600Gateway, list[tuple[str, dict]]]:
    """Create a gateway whose request method returns queued responses."""
    gateway = IT600Gateway(host="192.0.2.10", euid="001E5E0D32906128", session=object())
    pending_responses = list(responses)
    request_calls = []

    async def fake_request(command: str, request_body: dict) -> dict:
        request_calls.append((command, request_body))
        if not pending_responses:
            raise AssertionError("No fake gateway response queued")
        return pending_responses.pop(0)

    gateway._make_encrypted_request = fake_request
    return gateway, request_calls


def detail_base(unique_id: str, model: str, endpoint: int = 1) -> dict:
    """Return common fields for a detailed fake device payload."""
    return {
        "data": {"UniID": unique_id, "Endpoint": endpoint},
        "sZDO": {
            "DeviceName": f'{{"deviceName": "{unique_id}"}}',
            "FirmwareVersion": "1.2.3",
        },
        "sZDOInfo": {"OnlineStatus_i": 1},
        "sBasicS": {"ManufactureName": "SALUS"},
        "DeviceL": {"ModelIdentifier_i": model},
    }


class TestPolling(unittest.IsolatedAsyncioTestCase):
    async def test_poll_status_refreshes_all_supported_device_collections(self):
        readall = {
            "status": "success",
            "id": [
                {"data": {"UniID": "gateway"}, "sGateway": {"NetworkLANMAC": "AA"}},
                {"data": {"UniID": "thermo_1"}, "sIT600TH": {}},
                {
                    "data": {"UniID": "leak_1"},
                    "sIASZS": {},
                    "sBasicS": {"ModelIdentifier": "WLS600"},
                },
                {"data": {"UniID": "sensor_1"}, "sTempS": {}},
                {"data": {"UniID": "switch_1", "Endpoint": 2}, "sOnOffS": {}},
                {"data": {"UniID": "cover_1"}, "sLevelS": {}},
            ],
        }
        gateway_detail = {
            "status": "success",
            "id": [
                {
                    "data": {"UniID": "gateway"},
                    "sGateway": {
                        "NetworkLANMAC": "AA:BB:CC:DD:EE:FF",
                        "ModelIdentifier": "UG600",
                    },
                    "sBasicS": {"ManufactureName": "SALUS"},
                    "sOTA": {"OTAFirmwareVersion_d": "1.0.0"},
                }
            ],
        }
        climate_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("thermo_1", "HTRP-RF(50)"),
                    "sIT600TH": {
                        "LocalTemperature_x100": 2050,
                        "HeatingSetpoint_x100": 2150,
                        "HoldType": 2,
                        "RunningState": 1,
                    },
                }
            ],
        }
        binary_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("leak_1", "WLS600"),
                    "sIASZS": {"ErrorIASZSAlarmed1": 1},
                }
            ],
        }
        sensor_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("sensor_1", "PS600"),
                    "sTempS": {"MeasuredValue_x100": 1875},
                }
            ],
        }
        switch_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("switch_1", "SPE600", endpoint=2),
                    "sOnOffS": {"OnOff": 1},
                }
            ],
        }
        cover_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("cover_1", "RS600"),
                    "sLevelS": {"CurrentLevel": 100, "MoveToLevel_f": "64FFFF"},
                    "sButtonS": {"Mode": 1},
                }
            ],
        }
        gateway, request_calls = make_gateway_with_responses(
            readall,
            gateway_detail,
            climate_detail,
            binary_detail,
            sensor_detail,
            switch_detail,
            cover_detail,
        )
        callback_events = []

        async def callback(device_id: str) -> None:
            callback_events.append(device_id)

        await gateway.add_climate_update_callback(callback)
        await gateway.add_binary_sensor_update_callback(callback)
        await gateway.add_sensor_update_callback(callback)
        await gateway.add_switch_update_callback(callback)
        await gateway.add_cover_update_callback(callback)

        await gateway.poll_status(send_callback=True)

        self.assertEqual("AA:BB:CC:DD:EE:FF", gateway.get_gateway_device().unique_id)
        self.assertIn("thermo_1", gateway.get_climate_devices())
        self.assertIn("thermo_1_problem", gateway.get_binary_sensor_devices())
        self.assertIn("leak_1", gateway.get_binary_sensor_devices())
        self.assertIn("sensor_1_temp", gateway.get_sensor_devices())
        self.assertIn("switch_1_2", gateway.get_switch_devices())
        self.assertIn("cover_1", gateway.get_cover_devices())
        self.assertEqual(
            [
                "thermo_1",
                "thermo_1_problem",
                "leak_1",
                "sensor_1_temp",
                "switch_1_2",
                "cover_1",
            ],
            callback_events,
        )
        self.assertEqual(
            [
                ("read", "readall"),
                ("read", "deviceid"),
                ("read", "deviceid"),
                ("read", "deviceid"),
                ("read", "deviceid"),
                ("read", "deviceid"),
                ("read", "deviceid"),
            ],
            [(command, body["requestAttr"]) for command, body in request_calls],
        )


if __name__ == "__main__":
    unittest.main()
