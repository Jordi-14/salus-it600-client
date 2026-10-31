"""Tests for it600MINITRV report decoding and child entities."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from salus_it600.gateway import IT600Gateway
from salus_it600.parsers import (
    MiniTrvReport,
    decode_mini_trv_report,
    device_short_id,
    parse_binary_diagnostic_devices,
    parse_binary_relay_sensor_devices,
    parse_binary_sensor_device,
    parse_climate_device,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"

# Decoded CommandResponse_d samples from a real it600MINITRV, with the leading
# short address and trailing bytes replaced by placeholders. The `.` at index 23
# is real gateway data: a fully closed valve position of -2.
SAMPLE_IDLE = "B37A1B20000000000000000.4068236022762100@320243FF00000000"
SAMPLE_HEATING = "B37A1B2400000001002003284068182020251850@320236FF00000000"
# Unpaired TRV (short address FFFF): no `@`, TRV temperature written twice.
SAMPLE_UNPAIRED = "B37FFFF000000000000000024074241824181500022032600000000"
# Unpaired report stored in the vendor app, complete and unedited.
SAMPLE_VENDOR = (
    "B37FFFF0000000000000000/28342672267205002220292FFE40000114800001000600078"
)
# At 24.94 the digits also hold the repeat "4249 4249", one character early.
SAMPLE_UNPAIRED_SHIFTED_REPEAT = (
    "B37FFFF000000000000000024074249424941500022032600000000"
)


def _hex(text: str) -> str:
    """Encode an ASCII report the way the gateway does."""
    return text.encode("ascii").hex().upper()


def _mini_trv_payload(**sit600i: Any) -> dict[str, Any]:
    """Return the MiniTRV fixture with selected `sIT600I` fields replaced."""
    payload = json.loads(
        (FIXTURE_DIR / "binary_sensor_mini_trv.json").read_text(encoding="utf-8")
    )
    for key, value in sit600i.items():
        if value is None:
            payload["sIT600I"].pop(key, None)
        else:
            payload["sIT600I"][key] = value
    return payload


def _thermostat_payload(unique_id: str, name: str, short_id: int) -> dict[str, Any]:
    """Return a minimal SQ610 payload carrying a ZigBee short address."""
    return {
        "data": {"UniID": unique_id, "Endpoint": 1},
        "sZDO": {
            "ShortID_d": short_id,
            "DeviceName": json.dumps({"deviceName": name, "ShortID_d": short_id}),
        },
        "sZDOInfo": {"OnlineStatus_i": 1},
        "sBasicS": {"ManufactureName": "SALUS"},
        "DeviceL": {"ModelIdentifier_i": "SQ610RF"},
        "sIT600TH": {
            "LocalTemperature_x100": 1820,
            "HeatingSetpoint_x100": 1850,
            "HoldType": 2,
            "RunningState": 1,
        },
    }


class TestDecodeMiniTrvReport(unittest.TestCase):
    """CommandResponse_d decoding."""

    def test_decodes_issue_samples(self) -> None:
        self.assertEqual(
            MiniTrvReport(
                thermostat_temperature=23.6,
                trv_temperature=22.76,
                setpoint=21.0,
            ),
            decode_mini_trv_report(_hex(SAMPLE_IDLE)),
        )
        self.assertEqual(
            MiniTrvReport(
                thermostat_temperature=18.2,
                trv_temperature=20.25,
                setpoint=18.5,
            ),
            decode_mini_trv_report(_hex(SAMPLE_HEATING)),
        )

    def test_decodes_unpaired_sample(self) -> None:
        self.assertEqual(
            MiniTrvReport(
                thermostat_temperature=None,
                trv_temperature=24.18,
                setpoint=None,
            ),
            decode_mini_trv_report(_hex(SAMPLE_UNPAIRED)),
        )

    def test_unpaired_ignores_misaligned_repeat(self) -> None:
        report = decode_mini_trv_report(_hex(SAMPLE_UNPAIRED_SHIFTED_REPEAT))

        assert report is not None
        self.assertEqual(24.94, report.trv_temperature)

    def test_unpaired_layout_needs_unpaired_short_id(self) -> None:
        paired = SAMPLE_UNPAIRED.replace("B37FFFF", "B375D6D")

        self.assertIsNone(decode_mini_trv_report(_hex(paired)))

    def test_lowercase_hex_is_accepted(self) -> None:
        report = decode_mini_trv_report(_hex(SAMPLE_HEATING).lower())

        assert report is not None
        self.assertEqual(20.25, report.trv_temperature)

    def test_rejects_unusable_values(self) -> None:
        cases = {
            "missing": None,
            "empty": "",
            "not a string": 1234,
            "not hex": "zz" + _hex(SAMPLE_HEATING),
            "odd-length hex": _hex(SAMPLE_HEATING)[:-1],
            "non-ascii bytes": "FF" + _hex(SAMPLE_HEATING),
            "no separator": _hex(SAMPLE_HEATING.replace("@", "#")),
            "non-digit thermostat temperature": _hex(
                SAMPLE_HEATING.replace("182020251850", "18x020251850")
            ),
            "non-digit trv temperature": _hex(
                SAMPLE_HEATING.replace("182020251850", "182020x51850")
            ),
            "non-digit setpoint": _hex(
                SAMPLE_HEATING.replace("182020251850", "1820202518x0")
            ),
            "zero trv temperature": _hex(
                SAMPLE_HEATING.replace("182020251850", "182000001850")
            ),
            "implausible trv temperature": _hex(
                SAMPLE_HEATING.replace("182020251850", "182075001850")
            ),
            "unpaired non-digit reading": _hex(
                SAMPLE_UNPAIRED.replace("24182418", "24x824x8")
            ),
            "unpaired without repeat": _hex(
                SAMPLE_UNPAIRED.replace("24182418", "24182419")
            ),
            "unpaired only zeros repeat": _hex(
                SAMPLE_UNPAIRED.replace("24182418", "00000000")
            ),
            "unpaired implausible reading": _hex(
                SAMPLE_UNPAIRED.replace("24182418", "75007500")
            ),
        }
        for label, value in cases.items():
            with self.subTest(label):
                self.assertIsNone(decode_mini_trv_report(value))

    def test_accepts_observed_valve_positions(self) -> None:
        # Characters 20-23: closed readings fall below `0` in the last character.
        for position in (
            "000*",
            "000+",
            "000,",
            "000.",
            "000/",
            "0005",
            "1433",
            "2241",
        ):
            with self.subTest(position):
                paired = decode_mini_trv_report(
                    _hex(SAMPLE_IDLE[:20] + position + SAMPLE_IDLE[24:])
                )
                unpaired = decode_mini_trv_report(
                    _hex(SAMPLE_UNPAIRED[:20] + position + SAMPLE_UNPAIRED[24:])
                )

                assert paired is not None and unpaired is not None
                self.assertEqual(22.76, paired.trv_temperature)
                self.assertEqual(24.18, unpaired.trv_temperature)

    def test_decodes_vendor_sample(self) -> None:
        # Its tail holds hex letters and its valve position ends in `/`.
        report = decode_mini_trv_report(_hex(SAMPLE_VENDOR))

        assert report is not None
        self.assertEqual(26.72, report.trv_temperature)

    def test_rejects_other_response_ids(self) -> None:
        cases = {
            "wiring centre, paired layout": "B70" + SAMPLE_HEATING[3:],
            "receiver, unpaired layout": "B71" + SAMPLE_UNPAIRED[3:],
            "placeholder identifier": "A1B" + SAMPLE_HEATING[3:],
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertIsNone(decode_mini_trv_report(_hex(text)))

    def test_undecodable_report_warns_once(self) -> None:
        for label, value in {
            "not hex": "zz" + _hex(SAMPLE_HEATING),
            "non-ascii bytes": "FF" + _hex(SAMPLE_HEATING),
        }.items():
            with (
                self.subTest(label),
                patch("salus_it600.parsers.mini_trv._REPORT_FAILURES_WARNED", set()),
            ):
                with self.assertLogs("salus_it600", level="DEBUG") as first:
                    self.assertIsNone(decode_mini_trv_report(value))
                with self.assertLogs("salus_it600", level="DEBUG") as second:
                    self.assertIsNone(decode_mini_trv_report(value))

                self.assertEqual(["WARNING"], [r.levelname for r in first.records])
                self.assertIn(value, first.output[0])
                self.assertEqual(["DEBUG"], [r.levelname for r in second.records])

    def test_invalid_status_report_warns_once_per_layout(self) -> None:
        with patch("salus_it600.parsers.mini_trv._REPORT_FAILURES_WARNED", set()):
            for label, text in {
                "invalid paired": SAMPLE_HEATING.replace(
                    "182020251850", "182075001850"
                ),
                "invalid unpaired": SAMPLE_UNPAIRED.replace("24182418", "24182419"),
            }.items():
                with self.subTest(label):
                    with self.assertLogs("salus_it600", level="DEBUG") as first:
                        self.assertIsNone(decode_mini_trv_report(_hex(text)))
                    with self.assertLogs("salus_it600", level="DEBUG") as second:
                        self.assertIsNone(decode_mini_trv_report(_hex(text)))

                    self.assertEqual(["WARNING"], [r.levelname for r in first.records])
                    self.assertIn(label, first.output[0])
                    self.assertEqual(["DEBUG"], [r.levelname for r in second.records])

    def test_misplaced_separator_logs_its_own_kind(self) -> None:
        with (
            patch("salus_it600.parsers.mini_trv._REPORT_FAILURES_WARNED", set()),
            self.assertLogs("salus_it600", level="WARNING") as logs,
        ):
            self.assertIsNone(decode_mini_trv_report(_hex("B37BAD@182020251850@")))

        self.assertIn("misplaced separator", logs.output[0])

    def test_valid_reports_do_not_log(self) -> None:
        for text in (SAMPLE_IDLE, SAMPLE_HEATING, SAMPLE_UNPAIRED, SAMPLE_VENDOR):
            with self.subTest(text), self.assertNoLogs("salus_it600", level="DEBUG"):
                self.assertIsNotNone(decode_mini_trv_report(_hex(text)))

    def test_other_responses_log_only_at_debug(self) -> None:
        for text in ("B381", "B70" + SAMPLE_HEATING[3:]):
            with (
                self.subTest(text),
                self.assertLogs("salus_it600", level="DEBUG") as logs,
            ):
                self.assertIsNone(decode_mini_trv_report(_hex(text)))

            self.assertEqual(["DEBUG"], [r.levelname for r in logs.records])
            self.assertIn(_hex(text), logs.output[0])

    def test_non_string_value_logs_as_undecodable(self) -> None:
        for value in (1234, 0, False, ["B37"]):
            with (
                self.subTest(value),
                patch("salus_it600.parsers.mini_trv._REPORT_FAILURES_WARNED", set()),
                self.assertLogs("salus_it600", level="WARNING") as logs,
            ):
                self.assertIsNone(decode_mini_trv_report(value))

            self.assertIn("undecodable", logs.output[0])
            self.assertIn(str(value), logs.output[0])

    def test_missing_or_empty_value_does_not_log(self) -> None:
        for value in (None, ""):
            with self.subTest(value), self.assertNoLogs("salus_it600", level="DEBUG"):
                self.assertIsNone(decode_mini_trv_report(value))

    def test_rejects_unrelated_responses_with_plausible_digits(self) -> None:
        cases = {
            "paired digits after garbage": "garbage182020251850@320236FF00000000",
            "paired digits only": "182020251850@320236FF00000000",
            "paired digits inside text": "OK 182020251850@ OK",
            "unpaired digits after garbage": "garbage" + SAMPLE_UNPAIRED,
            "unpaired digits without prefix": SAMPLE_UNPAIRED[7:],
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertIsNone(decode_mini_trv_report(_hex(text)))

    def test_paired_reads_only_before_first_separator(self) -> None:
        cases = {
            "short first section": "B37BAD@182020251850@",
            "short first section, full report after": "B37BAD@" + SAMPLE_HEATING,
            "garbage first section, full report after": "garbage@" + SAMPLE_IDLE,
            "second separator in tail": SAMPLE_HEATING.replace("FF00", "FF@0"),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertIsNone(decode_mini_trv_report(_hex(text)))

    def test_rejects_truncated_reports(self) -> None:
        separator = SAMPLE_HEATING.index("@")
        cases = {
            "paired, nothing after separator": SAMPLE_HEATING[: separator + 1],
            "paired, short tail": SAMPLE_HEATING[: separator + 9],
            "paired, identifier cut": SAMPLE_HEATING[4:],
            "paired, status digits cut": SAMPLE_HEATING[:12] + SAMPLE_HEATING[16:],
            "unpaired, cut after reading": SAMPLE_UNPAIRED[:36],
            "unpaired, short tail": SAMPLE_UNPAIRED[:-1],
            "unpaired, cut in reading": SAMPLE_UNPAIRED[:32],
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertIsNone(decode_mini_trv_report(_hex(text)))

    def test_accepts_longer_tails(self) -> None:
        # The fixture holds the full report, with a longer tail than the samples.
        fixture = _mini_trv_payload()["sIT600I"]["CommandResponse_d"]

        self.assertEqual(
            MiniTrvReport(
                thermostat_temperature=18.2,
                trv_temperature=20.25,
                setpoint=18.5,
            ),
            decode_mini_trv_report(fixture),
        )
        report = decode_mini_trv_report(_hex(SAMPLE_UNPAIRED + "00000000"))
        assert report is not None
        self.assertEqual(24.18, report.trv_temperature)


class TestDeviceShortId(unittest.TestCase):
    """ZigBee short address lookup."""

    def test_reads_szdo_short_id(self) -> None:
        self.assertEqual(23917, device_short_id({"sZDO": {"ShortID_d": 23917}}))

    def test_falls_back_to_device_name_json(self) -> None:
        payload = {"sZDO": {"DeviceName": '{"deviceName": "Hall", "ShortID_d": 17481}'}}

        self.assertEqual(17481, device_short_id(payload))

    def test_missing_or_malformed_short_id(self) -> None:
        cases = {
            "no sZDO": {},
            "sZDO not a dict": {"sZDO": "x"},
            "no short id": {"sZDO": {"DeviceName": '{"deviceName": "Hall"}'}},
            "bad device name": {"sZDO": {"DeviceName": "not json"}},
            "device name not an object": {"sZDO": {"DeviceName": "[1]"}},
            "bool short id": {"sZDO": {"ShortID_d": True}},
            "string short id": {"sZDO": {"ShortID_d": "23917"}},
        }
        for label, payload in cases.items():
            with self.subTest(label):
                self.assertIsNone(device_short_id(payload))


class TestMiniTrvParsers(unittest.TestCase):
    """Entities parsed from one it600MINITRV payload."""

    def test_relay_sensors_from_fixture(self) -> None:
        sensors = {
            sensor.unique_id: sensor
            for sensor in parse_binary_relay_sensor_devices(_mini_trv_payload())
        }

        self.assertEqual(
            {"trv_mini_1_temperature", "trv_mini_1_rssi", "trv_mini_1_lqi"},
            set(sensors),
        )
        temperature = sensors["trv_mini_1_temperature"]
        self.assertEqual(20.25, temperature.state)
        self.assertEqual("temperature", temperature.device_class)
        self.assertEqual("trv_mini_1", temperature.parent_unique_id)
        self.assertEqual("Bedroom TRV Temperature", temperature.name)
        self.assertIsNone(temperature.entity_category)
        self.assertEqual(-58, sensors["trv_mini_1_rssi"].state)
        self.assertEqual("diagnostic", sensors["trv_mini_1_rssi"].entity_category)
        self.assertEqual(255, sensors["trv_mini_1_lqi"].state)

    def test_temperature_is_carried_forward(self) -> None:
        first = {
            sensor.unique_id: sensor
            for sensor in parse_binary_relay_sensor_devices(_mini_trv_payload())
        }
        offline = _mini_trv_payload(CommandResponse_d=None)
        offline["sZDOInfo"]["OnlineStatus_i"] = 0

        second = {
            sensor.unique_id: sensor
            for sensor in parse_binary_relay_sensor_devices(offline, first)
        }

        self.assertEqual(20.25, second["trv_mini_1_temperature"].state)
        self.assertFalse(second["trv_mini_1_temperature"].available)

    def test_temperature_is_carried_forward_over_mode_command_replies(self) -> None:
        # The reply format is unknown, so these cover plausible shapes: the bare
        # command, and a report layout with digits a search could misread.
        first = {
            sensor.unique_id: sensor
            for sensor in parse_binary_relay_sensor_devices(_mini_trv_payload())
        }

        for command in ("B381", "B387", "B388"):
            for reply in (command, command + SAMPLE_HEATING[4:]):
                with self.subTest(reply):
                    second = {
                        sensor.unique_id: sensor
                        for sensor in parse_binary_relay_sensor_devices(
                            _mini_trv_payload(CommandResponse_d=_hex(reply)), first
                        )
                    }

                    self.assertEqual(20.25, second["trv_mini_1_temperature"].state)

    def test_no_temperature_until_a_report_decodes(self) -> None:
        sensors = parse_binary_relay_sensor_devices(
            _mini_trv_payload(CommandResponse_d="not hex")
        )

        self.assertNotIn(
            "trv_mini_1_temperature",
            {sensor.unique_id for sensor in sensors},
        )

    def test_receiver_gets_signal_sensors_only(self) -> None:
        payload = _mini_trv_payload()
        payload["DeviceL"]["ModelIdentifier_i"] = "it600Receiver"
        payload["sBasicS"]["ModelIdentifier"] = "it600Receiver"

        sensors = {
            sensor.unique_id for sensor in parse_binary_relay_sensor_devices(payload)
        }

        self.assertEqual({"trv_mini_1_rssi", "trv_mini_1_lqi"}, sensors)

    def test_non_relay_models_get_no_relay_sensors(self) -> None:
        payload = _mini_trv_payload()
        payload["DeviceL"]["ModelIdentifier_i"] = "WLS600"
        payload["sBasicS"]["ModelIdentifier"] = "WLS600"

        self.assertEqual([], parse_binary_relay_sensor_devices(payload))
        self.assertEqual([], parse_binary_relay_sensor_devices({"sIT600I": {}}))

    def test_problem_sensor_off_when_no_fault_flags_are_set(self) -> None:
        diagnostics = {
            sensor.unique_id: sensor
            for sensor in parse_binary_diagnostic_devices(_mini_trv_payload())
        }

        self.assertFalse(diagnostics["trv_mini_1_low_battery"].is_on)
        problem = diagnostics["trv_mini_1_problem"]
        self.assertFalse(problem.is_on)
        self.assertEqual("problem", problem.device_class)
        self.assertEqual("diagnostic", problem.entity_category)
        self.assertEqual({"errors": []}, problem.extra_state_attributes)

    def test_problem_sensor_lists_active_faults(self) -> None:
        payload = _mini_trv_payload(TRVError22=1, TRVError30=1, TRVError31=1)

        diagnostics = {
            sensor.unique_id: sensor
            for sensor in parse_binary_diagnostic_devices(payload)
        }

        # Low battery stays on its own sensor, not in the problem list.
        self.assertTrue(diagnostics["trv_mini_1_low_battery"].is_on)
        problem = diagnostics["trv_mini_1_problem"]
        self.assertTrue(problem.is_on)
        self.assertEqual(
            {"errors": ["Gear issue", "Adaptation issue"]},
            problem.extra_state_attributes,
        )

    def test_no_problem_sensor_without_fault_flags(self) -> None:
        payload = _mini_trv_payload(
            TRVError01=None,
            TRVError23=None,
            TRVError30=None,
            TRVError31=None,
        )

        unique_ids = {
            sensor.unique_id for sensor in parse_binary_diagnostic_devices(payload)
        }

        self.assertEqual({"trv_mini_1_low_battery"}, unique_ids)

    def test_heat_sensor_names_paired_thermostat(self) -> None:
        thermostat = parse_climate_device(
            _thermostat_payload("sq610_1", "Bedroom Thermostat", 23917)
        )
        assert thermostat is not None

        device = parse_binary_sensor_device(_mini_trv_payload(), {23917: thermostat})

        assert device is not None
        self.assertTrue(device.is_on)
        self.assertEqual("heat", device.device_class)
        self.assertEqual(
            {
                "paired_thermostat_short_id": 23917,
                "paired_thermostat_id": "sq610_1",
                "paired_thermostat_name": "Bedroom Thermostat",
            },
            device.extra_state_attributes,
        )

    def test_heat_sensor_reports_mode(self) -> None:
        for mode in (0, 1, 2, 4):
            with self.subTest(mode):
                device = parse_binary_sensor_device(_mini_trv_payload(Mode=mode))

                assert device is not None
                self.assertEqual(mode, device.mini_trv_mode)

    def test_heat_sensor_ignores_missing_or_malformed_mode(self) -> None:
        for label, mode in {"missing": None, "bool": True, "string": "1"}.items():
            with self.subTest(label):
                device = parse_binary_sensor_device(_mini_trv_payload(Mode=mode))

                assert device is not None
                self.assertIsNone(device.mini_trv_mode)

    def test_receiver_reports_no_mode(self) -> None:
        payload = _mini_trv_payload(Mode=1)
        payload["DeviceL"]["ModelIdentifier_i"] = "it600Receiver"
        payload["sBasicS"]["ModelIdentifier"] = "it600Receiver"

        device = parse_binary_sensor_device(payload)

        assert device is not None
        self.assertIsNone(device.mini_trv_mode)

    def test_heat_sensor_keeps_unresolved_short_id(self) -> None:
        device = parse_binary_sensor_device(_mini_trv_payload())

        assert device is not None
        self.assertEqual(
            {"paired_thermostat_short_id": 23917},
            device.extra_state_attributes,
        )

    def test_heat_sensor_ignores_unpaired_or_malformed_short_id(self) -> None:
        for value in (0, 0xFFFF, True, "23917", None):
            with self.subTest(value=value):
                device = parse_binary_sensor_device(
                    _mini_trv_payload(PairedThermostatShortID=value)
                )

                assert device is not None
                self.assertIsNone(device.extra_state_attributes)


class TestMiniTrvGatewayRefresh(unittest.IsolatedAsyncioTestCase):
    """MiniTRV entities through the gateway caches."""

    async def test_refresh_exposes_mini_trv_entities(self) -> None:
        mini_trv = _mini_trv_payload()
        responses = [
            {
                "status": "success",
                "id": [_thermostat_payload("sq610_1", "Bedroom Thermostat", 23917)],
            },
            {"status": "success", "id": [mini_trv]},
            {
                "status": "success",
                "id": [
                    _mini_trv_payload(
                        CommandResponse_d=None,
                        LastMessageRSSI_d=None,
                        LastMessageLQI_d=None,
                    )
                ],
            },
        ]
        gateway = IT600Gateway(
            host="192.0.2.10", euid="001E5E0D32906128", session=object()
        )

        async def fake_request(command: str, request_body: dict) -> dict:
            return copy.deepcopy(responses.pop(0))

        gateway._make_encrypted_request = fake_request  # type: ignore[method-assign]

        await gateway._refresh_climate_devices([{"data": {"UniID": "sq610_1"}}])
        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "trv_mini_1"}}]
        )

        heat = gateway.get_binary_sensor_device("trv_mini_1")
        assert heat is not None
        assert heat.extra_state_attributes is not None
        self.assertEqual("sq610_1", heat.extra_state_attributes["paired_thermostat_id"])
        problem = gateway.get_binary_sensor_device("trv_mini_1_problem")
        assert problem is not None
        self.assertFalse(problem.is_on)
        temperature = gateway.get_sensor_device("trv_mini_1_temperature")
        assert temperature is not None
        self.assertEqual(20.25, temperature.state)
        self.assertIn("trv_mini_1_rssi", gateway.get_sensor_devices())

        # A poll without the report or signal fields keeps the last readings.
        await gateway._refresh_binary_sensor_devices(
            [{"data": {"UniID": "trv_mini_1"}}]
        )

        sensors = gateway.get_sensor_devices()
        self.assertEqual(20.25, sensors["trv_mini_1_temperature"].state)
        self.assertEqual(-58, sensors["trv_mini_1_rssi"].state)
        self.assertEqual(255, sensors["trv_mini_1_lqi"].state)


if __name__ == "__main__":
    unittest.main()
