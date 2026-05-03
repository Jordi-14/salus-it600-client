"""Tests for device parsing and collection refresh."""

import unittest

from salus_it600.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_OFF,
    FAN_MODE_HIGH,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_ECO,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
)
from salus_it600.exceptions import IT600CommandError
from salus_it600.gateway import IT600Gateway
from salus_it600.parsers.cover import parse_cover_device
from salus_it600.parsers.switch import parse_switch_device


def make_gateway_with_response(response: dict) -> IT600Gateway:
    """Create a gateway with a fake encrypted request method."""
    gateway = IT600Gateway(host="192.0.2.10", euid="001E5E0D32906128", session=object())

    async def fake_request(command: str, request_body: dict) -> dict:
        return response

    gateway._make_encrypted_request = fake_request
    return gateway


def common_detail(unique_id: str, model: str) -> dict:
    """Return common fields for detailed device payloads."""
    return {
        "data": {"UniID": unique_id, "Endpoint": 1},
        "sZDO": {"DeviceName": f'{{"deviceName": "{unique_id}"}}'},
        "sZDOInfo": {"OnlineStatus_i": 1},
        "sBasicS": {"ManufactureName": "SALUS"},
        "DeviceL": {"ModelIdentifier_i": model},
    }


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

    async def test_switch_parser_adds_power_and_energy_sensors(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "switch_1", "Endpoint": 2},
                        "sOnOffS": {"OnOff": 1},
                        "sMeteringS": {
                            "InstantaneousDemand": 42,
                            "CurrentSummationDelivered": 12345,
                        },
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

        power = gateway.get_sensor_device("switch_1_2_power")
        energy = gateway.get_sensor_device("switch_1_2_energy")
        self.assertIsNotNone(power)
        self.assertEqual(42, power.state)
        self.assertEqual("W", power.unit_of_measurement)
        self.assertEqual("switch_1_2", power.parent_unique_id)
        self.assertIsNotNone(energy)
        self.assertEqual(12.345, energy.state)
        self.assertEqual("kWh", energy.unit_of_measurement)

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

    async def test_sensor_parser_adds_humidity_and_battery_children(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("sensor_1", "TS600"),
                        "sTempS": {"MeasuredValue_x100": 2215},
                        "sRelativeHumidity": {"MeasuredValue_x100": 4550},
                        "sPowerS": {"BatteryVoltage_x10": 29},
                    }
                ],
            }
        )

        await gateway._refresh_sensor_devices(
            [{"data": {"UniID": "sensor_1", "Endpoint": 1}}],
        )

        humidity = gateway.get_sensor_device("sensor_1_humidity")
        battery = gateway.get_sensor_device("sensor_1_battery")
        self.assertIsNotNone(humidity)
        self.assertEqual(45.5, humidity.state)
        self.assertEqual("sensor_1", humidity.parent_unique_id)
        self.assertIsNotNone(battery)
        self.assertEqual(100, battery.state)
        self.assertEqual("diagnostic", battery.entity_category)

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

    async def test_cover_parser_sets_position_and_motion_state(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("cover_1", "RS600"),
                        "sLevelS": {"CurrentLevel": 25, "MoveToLevel_f": "50FFFF"},
                        "sButtonS": {"Mode": 1},
                    }
                ],
            }
        )

        await gateway._refresh_cover_devices([{"data": {"UniID": "cover_1"}}])

        device = gateway.get_cover_device("cover_1")
        self.assertIsNotNone(device)
        self.assertEqual(25, device.current_cover_position)
        self.assertTrue(device.is_opening)
        self.assertFalse(device.is_closing)
        self.assertFalse(device.is_closed)
        self.assertEqual("shutter", device.device_class)

    async def test_cover_parser_skips_disabled_endpoint(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("cover_1", "RS600"),
                        "sLevelS": {"CurrentLevel": 25, "MoveToLevel_f": "50FFFF"},
                        "sButtonS": {"Mode": 0},
                    }
                ],
            }
        )

        await gateway._refresh_cover_devices([{"data": {"UniID": "cover_1"}}])

        self.assertEqual({}, gateway.get_cover_devices())

    def test_sr600_payload_with_level_is_switch_not_cover(self):
        payload = {
            **common_detail("relay_1", "SR600"),
            "sOnOffS": {"OnOff": 1},
            "sLevelS": {"CurrentLevel": 100, "MoveToLevel_f": "64FFFF"},
        }

        switch = parse_switch_device(payload)

        self.assertIsNotNone(switch)
        self.assertEqual("relay_1_1", switch.unique_id)
        self.assertEqual("switch", switch.device_class)
        self.assertIsNone(parse_cover_device(payload))

    def test_rs600_payload_with_level_remains_cover_only(self):
        payload = {
            **common_detail("cover_1", "RS600"),
            "sOnOffS": {"OnOff": 1},
            "sLevelS": {"CurrentLevel": 25, "MoveToLevel_f": "50FFFF"},
        }

        self.assertIsNone(parse_switch_device(payload))
        self.assertIsNotNone(parse_cover_device(payload))

    async def test_binary_relay_model_uses_relay_status(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("trv_1", "it600MINITRV"),
                        "sIT600I": {"RelayStatus": 1},
                    }
                ],
            }
        )

        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "trv_1"}}],
        )

        device = gateway.get_binary_sensor_device("trv_1")
        self.assertIsNotNone(device)
        self.assertTrue(device.is_on)
        self.assertEqual("heat", device.device_class)

    async def test_binary_sensor_adds_low_battery_diagnostic(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("window_1", "SW600"),
                        "sIASZS": {
                            "ErrorIASZSAlarmed1": 0,
                            "ErrorIASZSLowBattery": 1,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "window_1"}}],
        )

        low_battery = gateway.get_binary_sensor_device("window_1_low_battery")
        self.assertIsNotNone(low_battery)
        self.assertTrue(low_battery.is_on)
        self.assertEqual("battery", low_battery.device_class)
        self.assertEqual("diagnostic", low_battery.entity_category)
        self.assertEqual("window_1", low_battery.parent_unique_id)

    async def test_button_model_is_not_exposed_as_binary_sensor(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("button_1", "SB600"),
                        "sIASZS": {"ErrorIASZSAlarmed1": 1},
                    }
                ],
            }
        )

        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "button_1"}}],
        )

        self.assertEqual({}, gateway.get_binary_sensor_devices())

    async def test_it600th_standby_maps_to_off_state(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("thermo_1", "HTRP-RF(50)"),
                        "sIT600TH": {
                            "LocalTemperature_x100": 2015,
                            "HeatingSetpoint_x100": 2100,
                            "HoldType": 7,
                            "RunningState": 0,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "thermo_1"}}])

        device = gateway.get_climate_device("thermo_1")
        self.assertIsNotNone(device)
        self.assertEqual(HVAC_MODE_OFF, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_OFF, device.hvac_action)
        self.assertEqual(PRESET_OFF, device.preset_mode)
        self.assertIsNone(device.current_humidity)

    async def test_sq610_humidity_accepts_raw_percent_field(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("sq610_1", "SQ610RF"),
                        "sIT600TH": {
                            "LocalTemperature_x100": 2015,
                            "HeatingSetpoint_x100": 2100,
                            "SunnySetpoint_x100": 63,
                            "HoldType": 2,
                            "RunningState": 0,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "sq610_1"}}])

        device = gateway.get_climate_device("sq610_1")
        self.assertIsNotNone(device)
        self.assertEqual(63.0, device.current_humidity)

    async def test_sq610_humidity_accepts_x100_field(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("sq610_1", "SQ610RF"),
                        "sIT600TH": {
                            "LocalTemperature_x100": 2015,
                            "HeatingSetpoint_x100": 2100,
                            "SunnySetpoint_x100": 4550,
                            "HoldType": 2,
                            "RunningState": 0,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "sq610_1"}}])

        device = gateway.get_climate_device("sq610_1")
        self.assertIsNotNone(device)
        self.assertEqual(45.5, device.current_humidity)

    async def test_sq610_adds_floor_battery_and_problem_children(self):
        status_d = "0" * 12 + "2134" + "0" * 83 + "4" + "0" * 10
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("sq610_1", "SQ610RF"),
                        "sIT600TH": {
                            "LocalTemperature_x100": 2015,
                            "HeatingSetpoint_x100": 2100,
                            "SunnySetpoint_x100": 4550,
                            "Status_d": status_d,
                            "OUTSensorProbe": 1,
                            "HoldType": 2,
                            "RunningState": 0,
                            "Error02": 1,
                            "Error32": 1,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "sq610_1"}}])

        humidity = gateway.get_sensor_device("sq610_1_humidity")
        floor = gateway.get_sensor_device("sq610_1_floor_temperature")
        battery = gateway.get_sensor_device("sq610_1_battery")
        problem = gateway.get_binary_sensor_device("sq610_1_problem")
        battery_problem = gateway.get_binary_sensor_device("sq610_1_battery_error")
        self.assertIsNotNone(humidity)
        self.assertEqual(45.5, humidity.state)
        self.assertIsNotNone(floor)
        self.assertEqual(21.34, floor.state)
        self.assertIsNotNone(battery)
        self.assertEqual(75, battery.state)
        self.assertEqual("diagnostic", battery.entity_category)
        self.assertIsNotNone(problem)
        self.assertTrue(problem.is_on)
        self.assertEqual(["Floor sensor overheating"], problem.extra_state_attributes["errors"])
        self.assertIsNotNone(battery_problem)
        self.assertTrue(battery_problem.is_on)
        self.assertEqual(["Low battery"], battery_problem.extra_state_attributes["errors"])

    async def test_it600th_current_temperature_falls_back_to_temp_measurement(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("sq610_1", "SQ610RF"),
                        "sIT600TH": {
                            "HeatingSetpoint_x100": 2100,
                            "HoldType": 2,
                            "RunningState": 0,
                        },
                        "sTempS": {"MeasuredValue_x100": 2235},
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "sq610_1"}}])

        device = gateway.get_climate_device("sq610_1")
        self.assertIsNotNone(device)
        self.assertEqual(22.35, device.current_temperature)

    async def test_fc600_cooling_payload_maps_extended_state(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("fan_1", "FC600"),
                        "sTherS": {
                            "SystemMode": 3,
                            "LocalTemperature_x100": 2420,
                            "HeatingSetpoint_x100": 2100,
                            "CoolingSetpoint_x100": 2300,
                            "MinCoolSetpoint_x100": 1600,
                            "MaxCoolSetpoint_x100": 3200,
                            "RunningState": 66,
                        },
                        "sComm": {"HoldType": 10},
                        "sFanS": {"FanMode": 3},
                        "sTherUIS": {"LockKey": 1},
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "fan_1"}}])

        device = gateway.get_climate_device("fan_1")
        self.assertIsNotNone(device)
        self.assertEqual(HVAC_MODE_COOL, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_COOL, device.hvac_action)
        self.assertEqual(PRESET_ECO, device.preset_mode)
        self.assertEqual(FAN_MODE_HIGH, device.fan_mode)
        self.assertEqual(23.0, device.target_temperature)
        self.assertEqual(16.0, device.min_temp)
        self.assertEqual(32.0, device.max_temp)
        self.assertTrue(device.locked)

    async def test_fc600nh_variant_parsed_as_fan_coil(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("fan_nh", "FC600NH"),
                        "sTherS": {
                            "SystemMode": 4,
                            "LocalTemperature_x100": 2250,
                            "HeatingSetpoint_x100": 2100,
                            "CoolingSetpoint_x100": 2400,
                            "RunningState": 33,
                        },
                        "sComm": {"HoldType": 2},
                        "sFanS": {"FanMode": 5},
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "fan_nh"}}])

        device = gateway.get_climate_device("fan_nh")
        self.assertIsNotNone(device)
        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_HEAT, device.hvac_action)
        self.assertEqual(PRESET_PERMANENT_HOLD, device.preset_mode)
        self.assertEqual("FC600NH", device.model)

    async def test_trv3rf_climate_and_diagnostics(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("trv_1", "TRV3RF"),
                        "sTherS": {
                            "LocalTemperature_x100": 2015,
                            "HeatingSetpoint_x100": 2100,
                            "MinHeatSetpoint_x100": 500,
                            "MaxHeatSetpoint_x100": 3500,
                            "RunningState": 1,
                        },
                        "sComm": {
                            "HoldType": 2,
                            "DeviceErrorCode": "0000000000000001",
                            "OpenWindowStatus": 1,
                        },
                        "sIT6ZB": {"TRVOutputPercentage": 45},
                        "sPowerS": {"BatteryVoltage_x10": 27},
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices([{"data": {"UniID": "trv_1"}}])

        device = gateway.get_climate_device("trv_1")
        self.assertIsNotNone(device)
        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_HEAT, device.hvac_action)
        self.assertEqual(PRESET_PERMANENT_HOLD, device.preset_mode)
        self.assertEqual(["off", "heat", "auto"], device.hvac_modes)
        self.assertEqual({"valve_opening": 45}, device.extra_state_attributes)
        battery = gateway.get_sensor_device("trv_1_battery")
        problem = gateway.get_binary_sensor_device("trv_1_problem")
        open_window = gateway.get_binary_sensor_device("trv_1_open_window")
        self.assertIsNotNone(battery)
        self.assertEqual(100, battery.state)
        self.assertIsNotNone(problem)
        self.assertTrue(problem.is_on)
        self.assertEqual(
            {"error_code": "0000000000000001"},
            problem.extra_state_attributes,
        )
        self.assertIsNotNone(open_window)
        self.assertTrue(open_window.is_on)

    async def test_ecm600_meter_sensors_parsed(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "ecm_1", "Endpoint": 1},
                        "sZDO": {
                            "DeviceName": '{"deviceName": "Clamp Meter"}',
                        },
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "ECM600"},
                        "sMeterS": {
                            "Multiplier": 1,
                            "Divisor": 10000,
                            "InstantaneousDemand": 3500,
                            "CurrentSummationDelivered": 1234567,
                        },
                        "sPowerS": {"BatteryVoltage_x10": 51},
                    }
                ],
            }
        )

        await gateway._refresh_meter_devices(
            [{"data": {"UniID": "ecm_1"}}]
        )

        power = gateway.get_sensor_device("ecm_1_1_power")
        self.assertIsNotNone(power)
        self.assertEqual(0.35, power.state)
        self.assertEqual("W", power.unit_of_measurement)
        self.assertEqual("power", power.device_class)

        energy = gateway.get_sensor_device("ecm_1_1_energy")
        self.assertIsNotNone(energy)
        self.assertEqual(123.46, energy.state)
        self.assertEqual("kWh", energy.unit_of_measurement)
        self.assertEqual("energy", energy.device_class)

        battery = gateway.get_sensor_device("ecm_1_1_battery")
        self.assertIsNotNone(battery)
        self.assertEqual(50, battery.state)
        self.assertEqual("battery", battery.device_class)

    async def test_ecm600_meter_without_readings_returns_battery_only(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        "data": {"UniID": "ecm_2", "Endpoint": 2},
                        "sZDO": {
                            "DeviceName": '{"deviceName": "Clamp 2"}',
                        },
                        "sZDOInfo": {"OnlineStatus_i": 1},
                        "sBasicS": {"ManufactureName": "SALUS"},
                        "DeviceL": {"ModelIdentifier_i": "ECM600"},
                        "sMeterS": {"Multiplier": 1, "Divisor": 10000},
                        "sPowerS": {"BatteryVoltage_x10": 51},
                    }
                ],
            }
        )

        await gateway._refresh_meter_devices(
            [{"data": {"UniID": "ecm_2"}}]
        )

        self.assertIsNone(gateway.get_sensor_device("ecm_2_2_power"))
        self.assertIsNone(gateway.get_sensor_device("ecm_2_2_energy"))
        battery = gateway.get_sensor_device("ecm_2_2_battery")
        self.assertIsNotNone(battery)

    async def test_parser_errors_are_logged_and_skipped(self):
        gateway = make_gateway_with_response(
            {
                "status": "success",
                "id": [
                    {
                        **common_detail("broken_1", "HTRP-RF(50)"),
                        "sIT600TH": {
                            "HeatingSetpoint_x100": 2100,
                            "HoldType": 2,
                        },
                    }
                ],
            }
        )

        await gateway._refresh_climate_devices(
            [{"data": {"UniID": "broken_1"}}],
        )

        # Device should load successfully without inventing a fake current temperature.
        device = gateway.get_climate_device("broken_1")
        self.assertIsNotNone(device)
        self.assertIsNone(device.current_temperature)
        self.assertEqual(21.0, device.target_temperature)

    async def test_refresh_invokes_registered_callbacks(self):
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
        callback_device_ids = []

        async def callback(device_id: str) -> None:
            callback_device_ids.append(device_id)

        await gateway.add_switch_update_callback(callback)
        await gateway._refresh_switch_devices(
            [{"data": {"UniID": "switch_1", "Endpoint": 2}}],
            send_callback=True,
        )

        self.assertEqual(["switch_1_2"], callback_device_ids)
        self.assertIn("switch_1_2", gateway.get_switch_devices())

    async def test_device_detail_response_validation_propagates(self):
        gateway = make_gateway_with_response({"status": "success"})

        with self.assertRaisesRegex(IT600CommandError, "missing list field 'id'"):
            await gateway._refresh_switch_devices(
                [{"data": {"UniID": "switch_1", "Endpoint": 2}}],
            )


if __name__ == "__main__":
    unittest.main()
