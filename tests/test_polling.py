"""Integration-style tests for complete gateway polling cycles."""

import unittest

from salus_it600.exceptions import IT600ConnectionError
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
        response = pending_responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

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


def full_poll_payloads() -> tuple[dict, list[dict]]:
    """Return a readall response and one detail response per device family."""
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
    return readall, [
        gateway_detail,
        climate_detail,
        binary_detail,
        sensor_detail,
        switch_detail,
        cover_detail,
    ]


def combined_detail(*family_details: dict) -> dict:
    """Merge per-family detail responses into one combined response."""
    return {
        "status": "success",
        "id": [item for detail in family_details for item in detail["id"]],
    }


def assert_full_poll_devices(test: unittest.TestCase, gateway: IT600Gateway) -> None:
    """Assert every device family from full_poll_payloads() was refreshed."""
    test.assertEqual("AA:BB:CC:DD:EE:FF", gateway.get_gateway_device().unique_id)
    test.assertIn("thermo_1", gateway.get_climate_devices())
    test.assertIn("thermo_1_problem", gateway.get_binary_sensor_devices())
    test.assertIn("leak_1", gateway.get_binary_sensor_devices())
    test.assertIn("sensor_1_temp", gateway.get_sensor_devices())
    test.assertIn("switch_1_2", gateway.get_switch_devices())
    test.assertIn("cover_1", gateway.get_cover_devices())


def request_kinds(request_calls: list[tuple[str, dict]]) -> list[tuple[str, str]]:
    """Return (command, requestAttr) for each gateway request."""
    return [(command, body["requestAttr"]) for command, body in request_calls]


PER_FAMILY_REQUESTS = [("read", "readall")] + [("read", "deviceid")] * 6


class TestPolling(unittest.IsolatedAsyncioTestCase):
    async def test_poll_status_fetches_all_details_in_one_request(self):
        readall, details = full_poll_payloads()
        gateway, request_calls = make_gateway_with_responses(
            readall,
            combined_detail(*details),
        )

        await gateway.poll_status()

        assert_full_poll_devices(self, gateway)
        self.assertEqual(
            [("read", "readall"), ("read", "deviceid")],
            request_kinds(request_calls),
        )
        self.assertEqual(
            [
                ("gateway", None),
                ("thermo_1", None),
                ("leak_1", None),
                ("sensor_1", None),
                ("switch_1", 2),
                ("cover_1", None),
            ],
            [
                (item["data"]["UniID"], item["data"].get("Endpoint"))
                for item in request_calls[1][1]["id"]
            ],
        )
        self.assertTrue(gateway.combined_detail_requests)

    async def test_rejected_combined_request_falls_back_for_good(self):
        readall, details = full_poll_payloads()
        gateway, request_calls = make_gateway_with_responses(
            readall,
            {"status": "failed"},
            *details,
            readall,
            *details,
        )

        await gateway.poll_status()

        assert_full_poll_devices(self, gateway)
        self.assertFalse(gateway.combined_detail_requests)
        self.assertEqual(
            [("read", "readall"), ("read", "deviceid")] + PER_FAMILY_REQUESTS[1:],
            request_kinds(request_calls),
        )

        request_calls.clear()
        await gateway.poll_status()

        self.assertEqual(PER_FAMILY_REQUESTS, request_kinds(request_calls))

    async def test_incomplete_combined_answer_falls_back_for_good(self):
        readall, details = full_poll_payloads()
        gateway, request_calls = make_gateway_with_responses(
            readall,
            combined_detail(*details[:3]),
            *details,
        )

        await gateway.poll_status()

        assert_full_poll_devices(self, gateway)
        self.assertFalse(gateway.combined_detail_requests)
        self.assertEqual(8, len(request_calls))

    async def test_combined_request_survives_occasional_connection_errors(self):
        readall, details = full_poll_payloads()
        responses: list = []
        for _ in range(2):
            responses += [readall, IT600ConnectionError("dropped"), *details]
        responses += [readall, combined_detail(*details)]
        gateway, request_calls = make_gateway_with_responses(*responses)

        for _ in range(3):
            await gateway.poll_status()

        assert_full_poll_devices(self, gateway)
        self.assertTrue(gateway.combined_detail_requests)
        self.assertEqual(0, gateway._combined_detail_failures)
        self.assertEqual(2 * 8 + 2, len(request_calls))

    async def test_repeated_connection_errors_disable_combined_request(self):
        readall, details = full_poll_payloads()
        responses: list = []
        for _ in range(3):
            responses += [readall, IT600ConnectionError("dropped"), *details]
        gateway, _request_calls = make_gateway_with_responses(*responses)

        for _ in range(3):
            await gateway.poll_status()

        self.assertFalse(gateway.combined_detail_requests)

    async def test_poll_status_skips_combined_request_for_one_family(self):
        readall, details = full_poll_payloads()
        readall = {"status": "success", "id": readall["id"][:1]}
        gateway, request_calls = make_gateway_with_responses(readall, details[0])

        await gateway.poll_status()

        self.assertEqual(
            [("read", "readall"), ("read", "deviceid")],
            request_kinds(request_calls),
        )
        self.assertEqual(1, len(request_calls[1][1]["id"]))
        self.assertTrue(gateway.combined_detail_requests)

    async def test_poll_status_refreshes_wiring_centre_devices(self):
        readall = {
            "status": "success",
            "id": [
                {"data": {"UniID": "gateway"}, "sGateway": {"NetworkLANMAC": "AA"}},
                {
                    "data": {"UniID": "wc_1"},
                    "sIT600WC": {},
                    "sBasicS": {"ModelIdentifier": "it600WC"},
                },
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
        wiring_centre_detail = {
            "status": "success",
            "id": [
                {
                    **detail_base("wc_1", "it600WC"),
                    "sIT600WC": {"ErrorCodeWC_d": "0000", "Error12": 1},
                    "sIT600I": {"LastMessageRSSI_d": -27, "LastMessageLQI_d": 255},
                }
            ],
        }
        gateway, request_calls = make_gateway_with_responses(
            readall,
            combined_detail(gateway_detail, wiring_centre_detail),
        )
        await gateway.poll_status()

        self.assertIn("wc_1", gateway.get_binary_sensor_devices())
        self.assertIn("wc_1_problem", gateway.get_binary_sensor_devices())
        self.assertIn("wc_1_rssi", gateway.get_sensor_devices())
        self.assertIn("wc_1_lqi", gateway.get_sensor_devices())
        self.assertTrue(gateway.get_binary_sensor_device("wc_1_problem").is_on)
        self.assertEqual(
            [("read", "readall"), ("read", "deviceid")],
            request_kinds(request_calls),
        )


if __name__ == "__main__":
    unittest.main()
