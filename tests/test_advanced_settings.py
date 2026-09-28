"""Tests for the SQ610 advanced-settings blob decoder."""

from __future__ import annotations

import unittest
from dataclasses import replace
from typing import Any

from salus_it600.const import (
    COOLING_CONTROL_SPAN_DEGREES,
    DISPLAY_RESOLUTION_DEGREES,
    ComfortWarmFloorLevel,
    ControlAlgorithm,
    S1S2Function,
    TemperatureDisplayUnit,
    TrvCalibrationMode,
)
from salus_it600.parsers.advanced_settings import parse_advanced_settings

# Real captures from a production SQ610RFNH, taken while A/B toggling Valve
# Protection and Comfort Warm Floor in the vendor app. Between captures the
# save counter (byte 1) increments and the obfuscated PIN bytes (40-41)
# churn even though the PIN never changed; the decoder must ignore both.
BASELINE = "72000100000115004050000100010400270010000600250015004000050001000000010180010100ffff000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
VALVE_PROTECTION_OFF = "7201010000011500405000010001040027001000060025001500400005000000000001018001010001ff000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
VALVE_PROTECTION_ON_AGAIN = "7202010000011500405000010001040027001000060025001500400005000100000001018001010003ff000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
COMFORT_WARM_FLOOR_LEVEL_1 = "7203010000011500405000010001040027001000060025001500400005000100000001018001010105ff000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
COMFORT_WARM_FLOOR_LEVEL_2 = "7204010000011500405000010001040027001000060025001500400005000100000001018001010207fe000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"

# Real capture from the SQ610RF payload dump preserved in
# docs/upstream-issues.md (issue #7): a different unit whose standby cooling
# setpoint is a real temperature (35.0) rather than the Off sentinel, whose
# control algorithm is a raw On-Off span variant (3) with no named enum
# member, and whose language index is 1 (Dansk).
UPSTREAM_SQ610RF = "7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"


def _mutated(blob: str, byte_offset: int, chars: str) -> str:
    """Return a capture with one field's hex characters replaced."""
    position = 2 * byte_offset
    return blob[:position] + chars + blob[position + len(chars) :]


class TestAdvancedSettingsDecoding(unittest.TestCase):
    """Decode the real captures and assert the UI-confirmed field values."""

    def test_real_captures_decode_confirmed_fields(self) -> None:
        captures: tuple[tuple[str, str, bool, int], ...] = (
            ("baseline", BASELINE, True, int(ComfortWarmFloorLevel.DISABLED)),
            ("valve_off", VALVE_PROTECTION_OFF, False, 0),
            ("valve_on_again", VALVE_PROTECTION_ON_AGAIN, True, 0),
            ("comfort_level_1", COMFORT_WARM_FLOOR_LEVEL_1, True, 1),
            ("comfort_level_2", COMFORT_WARM_FLOOR_LEVEL_2, True, 2),
        )

        for name, blob, valve_protection, comfort_warm_floor in captures:
            with self.subTest(capture=name):
                settings = parse_advanced_settings({"Status_2_d": blob})

                assert settings is not None
                self.assertEqual(valve_protection, settings.valve_protection)
                self.assertEqual(comfort_warm_floor, settings.comfort_warm_floor)
                # Fields confirmed in the live UI at capture time, identical
                # across all five captures.
                self.assertEqual(15.0, settings.standby_heating_setpoint)
                self.assertIsNone(settings.standby_cooling_setpoint)
                self.assertEqual(15.0, settings.min_heating_setpoint)
                self.assertEqual(25.0, settings.max_heating_setpoint)
                self.assertEqual(5.0, settings.min_cooling_setpoint)
                self.assertEqual(40.0, settings.max_cooling_setpoint)
                self.assertEqual(180, settings.min_off_time_cooling)
                self.assertEqual(
                    int(TemperatureDisplayUnit.CELSIUS),
                    settings.temperature_display_unit,
                )
                self.assertEqual(
                    0.1,
                    DISPLAY_RESOLUTION_DEGREES[settings.display_resolution],
                )
                self.assertEqual(
                    int(ControlAlgorithm.ITLC_UNDERFLOOR),
                    settings.control_algorithm,
                )
                self.assertEqual(
                    0.25,
                    COOLING_CONTROL_SPAN_DEGREES[settings.cooling_control_span],
                )
                self.assertEqual(
                    int(S1S2Function.DISABLED),
                    settings.s1_s2_function,
                )
                self.assertEqual(
                    int(TrvCalibrationMode.AUTO_SELECTION),
                    settings.trv_calibration_mode,
                )
                self.assertEqual(0.0, settings.temperature_calibration)
                self.assertFalse(settings.unlock_from_thermostat_enabled)
                self.assertFalse(settings.adjust_setpoint_when_locked_allowed)

    def test_decoder_ignores_save_counter_and_pin_bytes(self) -> None:
        # BASELINE and VALVE_PROTECTION_ON_AGAIN describe identical settings;
        # only the save counter (byte 1) and the obfuscated PIN bytes (40-41)
        # differ on the wire. Whole-object equality proves the decoder does
        # not key off any of them.
        self.assertEqual(
            parse_advanced_settings({"Status_2_d": BASELINE}),
            parse_advanced_settings({"Status_2_d": VALVE_PROTECTION_ON_AGAIN}),
        )

        # The two comfort-level captures differ only in that one setting
        # besides the counter/PIN churn.
        level_1 = parse_advanced_settings({"Status_2_d": COMFORT_WARM_FLOOR_LEVEL_1})
        level_2 = parse_advanced_settings({"Status_2_d": COMFORT_WARM_FLOOR_LEVEL_2})
        assert level_1 is not None
        self.assertEqual(
            replace(level_1, comfort_warm_floor=int(ComfortWarmFloorLevel.LEVEL_2)),
            level_2,
        )

    def test_upstream_capture_with_real_standby_cooling_setpoint(self) -> None:
        settings = parse_advanced_settings({"Status_2_d": UPSTREAM_SQ610RF})

        assert settings is not None
        self.assertEqual(5.0, settings.standby_heating_setpoint)
        self.assertEqual(35.0, settings.standby_cooling_setpoint)
        # Raw On-Off algorithm variant without a named enum member.
        self.assertEqual(3, settings.control_algorithm)
        self.assertNotIn(
            settings.control_algorithm,
            [int(member) for member in ControlAlgorithm],
        )
        self.assertEqual(
            0.5,
            DISPLAY_RESOLUTION_DEGREES[settings.display_resolution],
        )
        self.assertEqual(1, settings.language)
        self.assertTrue(settings.unlock_from_thermostat_enabled)

    def test_standby_cooling_off_sentinels(self) -> None:
        for sentinel in ("4050", "0450"):
            with self.subTest(sentinel=sentinel):
                settings = parse_advanced_settings(
                    {"Status_2_d": _mutated(BASELINE, 8, sentinel)},
                )

                assert settings is not None
                self.assertIsNone(settings.standby_cooling_setpoint)
                # Neighbouring fields still decode.
                self.assertEqual(15.0, settings.standby_heating_setpoint)

    def test_temperature_calibration_sign_magnitude(self) -> None:
        # All real captures carry 0.0 calibration, so the signed encodings
        # are exercised on targeted mutations of the baseline capture.
        for chars, expected in (("8350", -3.5), ("0050", 0.5), ("0000", 0.0)):
            with self.subTest(chars=chars):
                settings = parse_advanced_settings(
                    {"Status_2_d": _mutated(BASELINE, 3, chars)},
                )

                assert settings is not None
                self.assertEqual(expected, settings.temperature_calibration)

    def test_schedule_key_is_an_aliased_fallback(self) -> None:
        from_alias = parse_advanced_settings({"Schedule": BASELINE})
        from_preferred = parse_advanced_settings(
            {"Status_2_d": BASELINE, "Schedule": "garbage"},
        )

        self.assertEqual(
            parse_advanced_settings({"Status_2_d": BASELINE}),
            from_alias,
        )
        assert from_preferred is not None
        self.assertTrue(from_preferred.valve_protection)

    def test_malformed_blobs_are_rejected(self) -> None:
        malformed: tuple[tuple[str, dict[str, Any]], ...] = (
            ("missing", {}),
            ("non_string", {"Status_2_d": 42}),
            ("truncated", {"Status_2_d": BASELINE[:96]}),
            ("overlong", {"Status_2_d": BASELINE + "00"}),
            ("wrong_header", {"Status_2_d": _mutated(BASELINE, 0, "71")}),
        )

        for name, payload in malformed:
            with self.subTest(payload=name):
                self.assertIsNone(parse_advanced_settings(payload))

    def test_undecodable_field_bytes_decode_as_none(self) -> None:
        settings = parse_advanced_settings(
            {"Status_2_d": _mutated(BASELINE, 30, "ab")},
        )

        assert settings is not None
        self.assertIsNone(settings.valve_protection)
        # The rest of the blob still decodes.
        self.assertEqual(0, settings.comfort_warm_floor)
        self.assertEqual(25.0, settings.max_heating_setpoint)


if __name__ == "__main__":
    unittest.main()
