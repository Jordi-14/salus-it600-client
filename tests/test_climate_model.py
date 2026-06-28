"""Tests for normalized climate model helpers."""

import unittest
from dataclasses import FrozenInstanceError, replace
from typing import Any

from salus_it600.const import (
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_FOLLOW_SCHEDULE,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    HoldType,
    RunningState,
    SystemMode,
)
from salus_it600.models import (
    ClimateDevice,
    active_climate_system_mode,
    active_climate_setpoint,
    active_temperature_range,
    climate_diagnostic_fields,
    normalized_hold_type,
    normalized_running_state,
    normalized_system_mode,
    normalized_temperature_range,
    normalized_temperature_value,
    running_state_is_cooling,
    running_state_is_heating,
    sq610_cooling_capability_source,
    sq610_supports_cooling,
)


def make_climate_device(**overrides: Any) -> ClimateDevice:
    """Return a minimal climate device for model tests."""
    fields: dict[str, Any] = {
        "available": True,
        "name": "Climate",
        "unique_id": "climate-1",
        "temperature_unit": "C",
        "precision": 0.1,
        "current_temperature": 20.0,
        "target_temperature": 21.0,
        "max_temp": 35.0,
        "min_temp": 5.0,
        "current_humidity": None,
        "hvac_mode": HVAC_MODE_HEAT,
        "hvac_action": CURRENT_HVAC_IDLE,
        "hvac_modes": (HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO),
        "preset_mode": PRESET_PERMANENT_HOLD,
        "preset_modes": (
            PRESET_FOLLOW_SCHEDULE,
            PRESET_PERMANENT_HOLD,
            PRESET_OFF,
        ),
        "fan_mode": None,
        "fan_modes": None,
        "locked": None,
        "supported_features": 0,
        "device_class": "temperature",
        "data": {"UniID": "climate-1"},
        "manufacturer": "SALUS",
        "model": "SQ610RF",
        "sw_version": None,
    }
    fields.update(overrides)
    return ClimateDevice(**fields)


class TestClimateModel(unittest.TestCase):
    def test_climate_device_is_keyword_only_and_frozen(self):
        with self.assertRaises(TypeError):
            ClimateDevice(True)

        device = make_climate_device()

        with self.assertRaises(FrozenInstanceError):
            device.name = "Changed"

        self.assertFalse(hasattr(device, "_replace"))
        self.assertEqual("Changed", replace(device, name="Changed").name)

    def test_climate_device_stores_immutable_mode_snapshots(self):
        hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT]
        preset_modes = [PRESET_PERMANENT_HOLD]
        fan_modes = ["Auto"]
        data = {"UniID": "climate-1"}
        extra_state_attributes = {"floor_temperature": 22.0}
        diagnostic_fields = {"SystemMode": int(SystemMode.HEAT)}

        device = make_climate_device(
            hvac_modes=hvac_modes,
            preset_modes=preset_modes,
            fan_modes=fan_modes,
            data=data,
            extra_state_attributes=extra_state_attributes,
            diagnostic_fields=diagnostic_fields,
        )

        hvac_modes.append(HVAC_MODE_COOL)
        preset_modes.append(PRESET_OFF)
        fan_modes.append("High")
        data["UniID"] = "mutated"
        extra_state_attributes["floor_temperature"] = 0.0
        diagnostic_fields["SystemMode"] = int(SystemMode.COOL)

        self.assertEqual((HVAC_MODE_OFF, HVAC_MODE_HEAT), device.hvac_modes)
        self.assertEqual((PRESET_PERMANENT_HOLD,), device.preset_modes)
        self.assertEqual(("Auto",), device.fan_modes)
        self.assertEqual({"UniID": "climate-1"}, device.data)
        self.assertEqual(
            {"floor_temperature": 22.0},
            device.extra_state_attributes,
        )
        self.assertEqual({"SystemMode": int(SystemMode.HEAT)}, device.diagnostic_fields)

    def test_active_climate_setpoint_uses_system_mode_with_fallbacks(self):
        self.assertEqual(
            23.0,
            active_climate_setpoint(
                system_mode=SystemMode.COOL,
                heating_setpoint=20.0,
                cooling_setpoint=23.0,
            ),
        )
        self.assertEqual(
            20.0,
            active_climate_setpoint(
                system_mode=SystemMode.COOL,
                heating_setpoint=20.0,
                cooling_setpoint=None,
            ),
        )
        self.assertEqual(
            20.5,
            active_climate_setpoint(
                system_mode=SystemMode.HEAT,
                heating_setpoint=20.5,
                cooling_setpoint=24.0,
            ),
        )
        self.assertEqual(
            24.0,
            active_climate_setpoint(
                system_mode=None,
                heating_setpoint=None,
                cooling_setpoint=24.0,
            ),
        )

    def test_active_climate_system_mode_uses_shared_state_signals(self):
        self.assertEqual(
            int(SystemMode.COOL),
            active_climate_system_mode(
                system_mode=None,
                hvac_mode=HVAC_MODE_COOL,
                running_state=RunningState.IDLE,
            ),
        )
        self.assertEqual(
            int(SystemMode.COOL),
            active_climate_system_mode(
                system_mode=SystemMode.HEAT,
                running_state=RunningState.FAN_COIL_COOLING,
            ),
        )
        self.assertEqual(
            int(SystemMode.HEAT),
            active_climate_system_mode(
                system_mode=None,
                running_state=RunningState.FAN_COIL_HEATING,
            ),
        )

    def test_running_state_helpers_treat_fan_stage_values_as_bitmasks(self):
        for running_state in (2, 6, 34, 66):
            with self.subTest(running_state=running_state):
                self.assertTrue(running_state_is_cooling(running_state))
                self.assertFalse(running_state_is_heating(running_state))

        for running_state in (1, 5, 33, 65):
            with self.subTest(running_state=running_state):
                self.assertTrue(running_state_is_heating(running_state))
                self.assertFalse(running_state_is_cooling(running_state))

        self.assertFalse(running_state_is_heating(RunningState.IDLE))
        self.assertFalse(running_state_is_cooling(RunningState.IDLE))
        self.assertFalse(running_state_is_heating(None))
        self.assertFalse(running_state_is_cooling(None))

    def test_active_temperature_range_uses_system_mode_with_fallbacks(self):
        self.assertEqual(
            (10.0, 30.0),
            active_temperature_range(
                system_mode=SystemMode.COOL,
                min_heat_temp=5.0,
                max_heat_temp=35.0,
                min_cool_temp=10.0,
                max_cool_temp=30.0,
            ),
        )
        self.assertEqual(
            (5.0, 35.0),
            active_temperature_range(
                system_mode=SystemMode.COOL,
                min_heat_temp=5.0,
                max_heat_temp=35.0,
                min_cool_temp=None,
                max_cool_temp=None,
            ),
        )
        self.assertEqual(
            (5.0, 35.0),
            active_temperature_range(
                system_mode=SystemMode.HEAT,
                min_heat_temp=5.0,
                max_heat_temp=35.0,
                min_cool_temp=10.0,
                max_cool_temp=30.0,
            ),
        )
        self.assertEqual(
            (10.0, 30.0),
            active_temperature_range(
                system_mode=None,
                min_heat_temp=None,
                max_heat_temp=None,
                min_cool_temp=10.0,
                max_cool_temp=30.0,
            ),
        )

    def test_normalized_missing_values_have_explicit_semantics(self):
        self.assertEqual(int(HoldType.PERMANENT_HOLD), normalized_hold_type(None))
        self.assertEqual(int(HoldType.STANDBY), normalized_hold_type(HoldType.STANDBY))
        self.assertIsNone(normalized_hold_type("2", default=None))
        self.assertIsNone(normalized_hold_type(True, default=None))

        self.assertEqual(int(SystemMode.HEAT), normalized_system_mode(SystemMode.HEAT))
        self.assertIsNone(normalized_system_mode(None))
        self.assertIsNone(normalized_system_mode(True))

        self.assertEqual(int(RunningState.IDLE), normalized_running_state(None))
        self.assertEqual(
            int(RunningState.COOLING),
            normalized_running_state(RunningState.COOLING),
        )
        self.assertIsNone(normalized_running_state("0", default=None))

        self.assertEqual(21.5, normalized_temperature_value(21.5))
        self.assertEqual(20.0, normalized_temperature_value(None, default=20.0))
        self.assertIsNone(normalized_temperature_value(True))
        self.assertEqual(
            (5.0, 35.0),
            normalized_temperature_range(5, 35),
        )
        self.assertEqual(
            (5.0, None),
            normalized_temperature_range(True, "35", default_min=5.0),
        )

    def test_sq610_cooling_capability_uses_reliable_sources(self):
        cases = [
            ({"cooling_control": 1}, "cooling_control"),
            ({"cooling_control": 0}, "cooling_control"),
            (
                {
                    "system_mode": SystemMode.COOL,
                    "running_state": RunningState.IDLE,
                },
                "active_system_mode",
            ),
            (
                {
                    "system_mode": SystemMode.HEAT,
                    "running_state": 34,
                },
                "active_running_state",
            ),
            ({"known_model_supports_cooling": True}, "known_model"),
            (
                {
                    "system_mode": SystemMode.HEAT,
                    "running_state": RunningState.HEATING,
                },
                "none",
            ),
        ]

        for kwargs, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, sq610_cooling_capability_source(**kwargs))

        self.assertTrue(sq610_supports_cooling(cooling_control=1))
        self.assertTrue(sq610_supports_cooling(cooling_control=0))
        self.assertFalse(
            sq610_supports_cooling(
                system_mode=SystemMode.HEAT,
                running_state=RunningState.HEATING,
            )
        )

    def test_climate_diagnostic_fields_are_whitelisted(self):
        self.assertEqual(
            {
                "SystemMode": int(SystemMode.HEAT),
                "RunningState": int(RunningState.IDLE),
                "CoolingControl": 1,
                "OnlineStatus_i": 1,
                "CoolingSetpoint_x100": 2300,
                "LocalTemperature_x100": 2100,
                "UniID": "climate-1",
            },
            climate_diagnostic_fields(
                {
                    "SystemMode": int(SystemMode.HEAT),
                    "RunningState": int(RunningState.IDLE),
                    "CoolingControl": 1,
                    "OnlineStatus_i": 1,
                    "CoolingSetpoint_x100": 2300,
                    "LocalTemperature_x100": 2100,
                    "UniID": "climate-1",
                }
            ),
        )


if __name__ == "__main__":
    unittest.main()
