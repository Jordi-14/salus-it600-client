"""Tests for climate payload compatibility."""

import unittest

from salus_it600.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_HEAT,
    PRESET_PERMANENT_HOLD,
)
from salus_it600.gateway import IT600Gateway


def make_gateway_with_response(response: dict) -> IT600Gateway:
    """Create a gateway with a fake encrypted request method."""
    gateway = IT600Gateway(host="192.0.2.10", euid="001E5E0D32906128", session=object())

    async def fake_request(command: str, request_body: dict) -> dict:
        return response

    gateway._make_encrypted_request = fake_request
    return gateway


class TestClimateCompat(unittest.IsolatedAsyncioTestCase):
    async def test_it600th_climate_loads_when_hold_type_missing(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"DeviceType": 100, "Endpoint": 1, "UniID": "thermo_1"},
                        "sIT600TH": {
                            "LocalTemperature_x100": 2010,
                            "HeatingSetpoint_x100": 2100,
                            "RunningState": 1,
                        },
                        "sZDO": {"DeviceName": '{"deviceName": "Living Room"}'},
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "SQ610RF"},
                    }
                ],
            }
        )

        with self.assertLogs("salus_it600", level="WARNING") as logs:
            await gateway._refresh_climate_devices(
                [{"data": {"DeviceType": 100, "Endpoint": 1, "UniID": "thermo_1"}}],
            )

        self.assertIn("missing HoldType", "\n".join(logs.output))
        device = gateway.get_climate_device("thermo_1")
        self.assertEqual("Living Room", device.name)
        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_HEAT, device.hvac_action)
        self.assertEqual(PRESET_PERMANENT_HOLD, device.preset_mode)

    async def test_fan_climate_loads_when_scomm_hold_type_missing(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"DeviceType": 100, "Endpoint": 9, "UniID": "fan_1"},
                        "sTherS": {
                            "SystemMode": 4,
                            "LocalTemperature_x100": 1980,
                            "HeatingSetpoint_x100": 2000,
                            "CoolingSetpoint_x100": 2400,
                            "RunningState": 0,
                        },
                        "sComm": {},
                        "sFanS": {"FanMode": 5},
                        "sZDO": {"DeviceName": '{"deviceName": "Fan Coil"}'},
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "FC600"},
                    }
                ],
            }
        )

        with self.assertLogs("salus_it600", level="WARNING") as logs:
            await gateway._refresh_climate_devices(
                [{"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "fan_1"}}],
            )

        self.assertIn("missing HoldType", "\n".join(logs.output))
        device = gateway.get_climate_device("fan_1")
        self.assertEqual("Fan Coil", device.name)
        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_IDLE, device.hvac_action)
        self.assertEqual(PRESET_PERMANENT_HOLD, device.preset_mode)


if __name__ == "__main__":
    unittest.main()
