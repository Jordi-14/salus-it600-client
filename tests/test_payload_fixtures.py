"""Fixture-backed parser regression tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from salus_it600.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    FAN_MODE_HIGH,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    PRESET_ECO,
    PRESET_PERMANENT_HOLD,
    HoldType,
    RunningState,
    SystemMode,
)
from salus_it600.parsers import (
    parse_binary_diagnostic_devices,
    parse_binary_sensor_device,
    parse_climate_binary_sensor_devices,
    parse_climate_device,
    parse_climate_sensor_devices,
    parse_cover_device,
    parse_sensor_devices,
    parse_switch_device,
    parse_switch_sensor_devices,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> dict[str, Any]:
    """Load one gateway detail payload fixture."""
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class TestPayloadFixtures(unittest.TestCase):
    """Verify realistic payload fixtures still parse into expected models."""

    def test_cover_fixture(self) -> None:
        device = parse_cover_device(_fixture("cover_rs600.json"))

        assert device is not None
        self.assertEqual("cover_1", device.unique_id)
        self.assertEqual(25, device.current_cover_position)
        self.assertTrue(device.is_opening)
        self.assertFalse(device.is_closing)

    def test_switch_fixture(self) -> None:
        payload = _fixture("switch_spe600.json")
        device = parse_switch_device(payload)
        sensors = {
            sensor.unique_id: sensor for sensor in parse_switch_sensor_devices(payload)
        }

        assert device is not None
        self.assertEqual("switch_1_2", device.unique_id)
        self.assertTrue(device.is_on)
        self.assertEqual("outlet", device.device_class)
        self.assertEqual(42, sensors["switch_1_2_power"].state)
        self.assertEqual(12.345, sensors["switch_1_2_energy"].state)

    def test_sensor_fixture(self) -> None:
        sensors = {
            sensor.unique_id: sensor
            for sensor in parse_sensor_devices(_fixture("sensor_ts600.json"))
        }

        self.assertEqual(22.15, sensors["sensor_1_temp"].state)
        self.assertEqual(45.5, sensors["sensor_1_humidity"].state)
        self.assertEqual("sensor_1", sensors["sensor_1_humidity"].parent_unique_id)
        self.assertEqual(100, sensors["sensor_1_battery"].state)
        self.assertEqual("diagnostic", sensors["sensor_1_battery"].entity_category)

    def test_binary_sensor_fixture(self) -> None:
        payload = _fixture("binary_sensor_wls600.json")
        device = parse_binary_sensor_device(payload)
        diagnostics = {
            sensor.unique_id: sensor
            for sensor in parse_binary_diagnostic_devices(payload)
        }

        assert device is not None
        self.assertEqual("leak_1", device.unique_id)
        self.assertTrue(device.is_on)
        self.assertEqual("moisture", device.device_class)
        self.assertTrue(diagnostics["leak_1_low_battery"].is_on)
        self.assertEqual("battery", diagnostics["leak_1_low_battery"].device_class)

    def test_sq610_climate_fixture(self) -> None:
        payload = _fixture("climate_sq610.json")
        device = parse_climate_device(payload)

        assert device is not None
        sensors = {
            sensor.unique_id: sensor
            for sensor in parse_climate_sensor_devices(payload, device)
        }
        binary_sensors = {
            sensor.unique_id: sensor
            for sensor in parse_climate_binary_sensor_devices(payload, device)
        }

        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(45.5, device.current_humidity)
        self.assertEqual(21.34, sensors["sq610_1_floor_temperature"].state)
        self.assertEqual(75, sensors["sq610_1_battery"].state)
        self.assertTrue(binary_sensors["sq610_1_problem"].is_on)
        self.assertEqual(
            ["Floor sensor overheating"],
            binary_sensors["sq610_1_problem"].extra_state_attributes["errors"],
        )
        self.assertEqual(
            ["Low battery"],
            binary_sensors["sq610_1_battery_error"].extra_state_attributes["errors"],
        )

    def test_fc600_climate_fixture(self) -> None:
        device = parse_climate_device(_fixture("climate_fc600.json"))

        assert device is not None
        self.assertEqual(HVAC_MODE_COOL, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_COOL, device.hvac_action)
        self.assertEqual(PRESET_ECO, device.preset_mode)
        self.assertEqual(FAN_MODE_HIGH, device.fan_mode)
        self.assertEqual(23.0, device.target_temperature)
        self.assertTrue(device.locked)
        self.assertEqual(int(HoldType.ECO), device.hold_type)
        self.assertEqual(int(SystemMode.COOL), device.system_mode)
        self.assertEqual(int(RunningState.FAN_COIL_COOLING), device.running_state)
        self.assertEqual(21.0, device.heating_setpoint)
        self.assertEqual(23.0, device.cooling_setpoint)
        self.assertEqual(16.0, device.min_cool_temp)
        self.assertEqual(32.0, device.max_cool_temp)
        self.assertTrue(device.supports_cooling)
        self.assertTrue(device.supports_fan)
        self.assertEqual("known_model", device.cooling_capability_source)

    def test_trv3rf_climate_fixture(self) -> None:
        payload = _fixture("climate_trv3rf.json")
        device = parse_climate_device(payload)

        assert device is not None
        sensors = {
            sensor.unique_id: sensor
            for sensor in parse_climate_sensor_devices(payload, device)
        }
        binary_sensors = {
            sensor.unique_id: sensor
            for sensor in parse_climate_binary_sensor_devices(payload, device)
        }

        self.assertEqual(HVAC_MODE_HEAT, device.hvac_mode)
        self.assertEqual(CURRENT_HVAC_HEAT, device.hvac_action)
        self.assertEqual(PRESET_PERMANENT_HOLD, device.preset_mode)
        self.assertEqual({"valve_opening": 45}, device.extra_state_attributes)
        self.assertEqual(int(HoldType.PERMANENT_HOLD), device.hold_type)
        self.assertIsNone(device.system_mode)
        self.assertEqual(int(RunningState.HEATING), device.running_state)
        self.assertEqual(21.0, device.heating_setpoint)
        self.assertEqual(5.0, device.min_heat_temp)
        self.assertEqual(35.0, device.max_heat_temp)
        self.assertFalse(device.supports_cooling)
        self.assertFalse(device.supports_fan)
        self.assertEqual("none", device.cooling_capability_source)
        self.assertEqual(100, sensors["trv_1_battery"].state)
        self.assertTrue(binary_sensors["trv_1_problem"].is_on)
        self.assertTrue(binary_sensors["trv_1_open_window"].is_on)


if __name__ == "__main__":
    unittest.main()
