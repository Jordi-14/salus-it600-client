"""Tests for device parsing and collection refresh."""

import unittest

from salus_it600.gateway import IT600Gateway


def make_gateway_with_response(response: dict) -> IT600Gateway:
    """Create a gateway with a fake encrypted request method."""
    gateway = IT600Gateway(host="192.0.2.10", euid="001E5E0D32906128", session=object())

    async def fake_request(command: str, request_body: dict) -> dict:
        return response

    gateway._make_encrypted_request = fake_request
    return gateway


class TestDeviceParsing(unittest.IsolatedAsyncioTestCase):
    async def test_switch_parser_adds_endpoint_to_unique_id(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "switch_1", "Endpoint": 2},
                        "sOnOffS": {"OnOff": 1},
                        "sZDO": {"DeviceName": '{"deviceName": "Kitchen Plug"}'},
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "SPE600"},
                    }
                ],
            }
        )

        await gateway._refresh_switch_devices(
            [{"data": {"UniID": "switch_1", "Endpoint": 2}}],
        )

        device = gateway.get_switch_device("switch_1_2")
        self.assertIsNotNone(device)
        self.assertEqual("Kitchen Plug", device.name)
        self.assertTrue(device.is_on)
        self.assertEqual("outlet", device.device_class)

    async def test_sensor_parser_adds_temperature_suffix(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "sensor_1", "Endpoint": 1},
                        "sTempS": {"MeasuredValue_x100": 2215},
                        "sZDO": {"DeviceName": '{"deviceName": "Hall Sensor"}'},
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "PS600"},
                    }
                ],
            }
        )

        await gateway._refresh_sensor_devices(
            [{"data": {"UniID": "sensor_1", "Endpoint": 1}}],
        )

        device = gateway.get_sensor_device("sensor_1_temp")
        self.assertIsNotNone(device)
        self.assertEqual("Hall Sensor", device.name)
        self.assertEqual(22.15, device.state)
        self.assertEqual("temperature", device.device_class)

    async def test_binary_sensor_parser_uses_model_device_class(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "leak_1", "Endpoint": 1},
                        "sIASZS": {"ErrorIASZSAlarmed1": 1},
                        "sZDO": {"DeviceName": '{"deviceName": "Leak Sensor"}'},
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "WLS600"},
                    }
                ],
            }
        )

        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "leak_1", "Endpoint": 1}}],
        )

        device = gateway.get_binary_sensor_device("leak_1")
        self.assertIsNotNone(device)
        self.assertEqual("Leak Sensor", device.name)
        self.assertTrue(device.is_on)
        self.assertEqual("moisture", device.device_class)


if __name__ == "__main__":
    unittest.main()
