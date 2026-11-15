"""Tests for it600MINITRV report decoding and child entities."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

from salus_it600.const import MiniTrvMode
from salus_it600.exceptions import IT600ConnectionError, IT600ValidationError
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

# B37: asks the TRV to send a status report.
STATUS_REQUEST = "42 33 37 00 00 00 00 00 00 00 00 78"
# `mini_trv_request_report_after` used by the polling tests, in seconds.
REQUEST_AFTER = 1800.0


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

    def test_out_of_range_thermostat_temperature_is_none(self) -> None:
        for label, text in {
            "zero": SAMPLE_HEATING.replace("182020251850", "000020251850"),
            "too high": SAMPLE_HEATING.replace("182020251850", "999920251850"),
        }.items():
            with self.subTest(label):
                self.assertEqual(
                    MiniTrvReport(
                        thermostat_temperature=None,
                        trv_temperature=20.25,
                        setpoint=18.5,
                    ),
                    decode_mini_trv_report(_hex(text)),
                )

    def test_out_of_range_setpoint_is_none(self) -> None:
        for label, text in {
            "zero": SAMPLE_HEATING.replace("182020251850", "182020250000"),
            "too high": SAMPLE_HEATING.replace("182020251850", "182020259999"),
        }.items():
            with self.subTest(label):
                self.assertEqual(
                    MiniTrvReport(
                        thermostat_temperature=18.2,
                        trv_temperature=20.25,
                        setpoint=None,
                    ),
                    decode_mini_trv_report(_hex(text)),
                )

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


class _FakeTrvGateway:
    """A real `IT600Gateway` whose gateway requests and clock are faked.

    Report requests depend on time, so each test is a sequence of polls at
    chosen times, checking what each poll wrote.

    Between polls, a test can change what the next poll sees:

    - `set_response()` changes or removes a TRV's `CommandResponse_d`;
    - `payloads` holds each TRV's full payload: edit one (for example, to take it
      offline), add one, or remove one to leave that TRV out of polls;
    - `write_error` makes writes fail.

    The first poll sets the baseline: the report already there then has an
    unknown age. To simulate the TRV sending a new report, call `set_response()`
    after a poll, not before the first one.

    Times are arbitrary seconds; only the gaps between polls matter. Code that
    reads the clock outside `poll()`, such as `set_mini_trv_mode()`, sees `now`,
    so set it first. `commands` holds every write so far, for checks that span
    more than one poll.
    """

    def __init__(self, **gateway_kwargs: Any) -> None:
        gateway_kwargs.setdefault("mini_trv_request_report_after", REQUEST_AFTER)
        # The real client under test; only its gateway I/O and clock are faked.
        self.gateway = IT600Gateway(
            host="192.0.2.10",
            euid="001E5E0D32906128",
            session=object(),
            **gateway_kwargs,
        )
        # Detail payload per TRV unique ID, served by every poll. Edit one to
        # change what the next poll sees; remove one to leave that TRV out.
        self.payloads: dict[str, dict[str, Any]] = {"trv_mini_1": _mini_trv_payload()}
        # Every SetCommand_d write, in order, as (TRV unique ID, command).
        self.commands: list[tuple[str, str]] = []
        # When set, each write is still recorded but then raises this.
        self.write_error: Exception | None = None
        # The loop time the gateway sees, in seconds; `poll(at)` sets it.
        self.now = 1000.0
        self.gateway._make_encrypted_request = self._request  # type: ignore[method-assign]
        # The gateway reads the time only through this method. Replacing it on
        # the instance with a lambda that reads `self.now` on every call makes
        # the gateway see whatever `now` is at the time.
        self.gateway._mini_trv_report_time = lambda: self.now  # type: ignore[method-assign]

    async def _request(self, command: str, request_body: dict) -> dict:
        """Answer gateway requests: record writes, serve `payloads` to reads."""
        if command == "write":
            item = request_body["id"][0]
            self.commands.append(
                (item["data"]["UniID"], item["sIT600I"]["SetCommand_d"])
            )
            if self.write_error is not None:
                raise self.write_error
            return {"status": "success", "id": [{"status": "success"}]}
        if request_body["requestAttr"] == "readall":
            return {
                "status": "success",
                "id": [
                    {
                        "data": copy.deepcopy(payload["data"]),
                        "sBasicS": {"ModelIdentifier": "it600MINITRV"},
                    }
                    for payload in self.payloads.values()
                ],
            }
        return {
            "status": "success",
            "id": [copy.deepcopy(payload) for payload in self.payloads.values()],
        }

    def set_response(self, value: str | None, device_id: str = "trv_mini_1") -> None:
        """Set a TRV's `CommandResponse_d`, or leave it out of polls with None."""
        sit600i = self.payloads[device_id]["sIT600I"]
        if value is None:
            sit600i.pop("CommandResponse_d", None)
        else:
            sit600i["CommandResponse_d"] = value

    async def poll(self, at: float) -> list[tuple[str, str]]:
        """Run `poll_status()` at time `at` and return the writes it made.

        Returns the device commands the client sent through the gateway during
        this poll, each as (target TRV UniID, `SetCommand_d`); writes to any
        TRV are included. Reads are not recorded.
        """
        self.now = at
        sent = len(self.commands)
        await self.gateway.poll_status()
        return self.commands[sent:]


class TestMiniTrvPollStatusRequests(unittest.IsolatedAsyncioTestCase):
    """When poll_status() writes the B37 status request (`STATUS_REQUEST`).

    It does so for a MiniTRV that has gone `mini_trv_request_report_after`
    seconds without a new report or a status request.
    """

    async def test_first_poll_requests_a_report_then_waits(self) -> None:
        fake = _FakeTrvGateway()

        # A valid report is already present, but its age is unknown, so ensure the
        # first poll still asks for one.
        self.assertEqual([("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000))
        self.assertEqual([], await fake.poll(1000 + REQUEST_AFTER - 1))
        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000 + REQUEST_AFTER)
        )

    async def test_requests_when_no_report_was_ever_seen(self) -> None:
        fake = _FakeTrvGateway()
        # Before the first poll, so the gateway never sees a report at all.
        fake.set_response(None)

        self.assertEqual([("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000))

    async def test_new_report_restarts_the_wait(self) -> None:
        fake = _FakeTrvGateway()
        # The first poll records the existing report as the baseline. A
        # report already there on the first poll has an unknown age, so only a
        # change seen on a later poll counts as new.
        await fake.poll(1000)

        fake.set_response(_hex(SAMPLE_IDLE))  # The TRV sends a new report.
        await fake.poll(1500)

        # Counted from the report at 1500, not the request at 1000.
        self.assertEqual([], await fake.poll(1000 + REQUEST_AFTER))
        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1500 + REQUEST_AFTER)
        )
        temperature = fake.gateway.get_sensor_device("trv_mini_1_temperature")
        assert temperature is not None
        self.assertEqual(22.76, temperature.state)

    async def test_omitted_then_repeated_report_is_not_new(self) -> None:
        fake = _FakeTrvGateway()
        original = fake.payloads["trv_mini_1"]["sIT600I"]["CommandResponse_d"]
        await fake.poll(1000)  # Baseline: the gateway has now seen `original`.

        # The field drops out of one poll, then returns unchanged. Neither is
        # a new report, so the wait still runs from the request at 1000.
        fake.set_response(None)
        await fake.poll(1100)
        fake.set_response(original)
        await fake.poll(1200)

        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000 + REQUEST_AFTER)
        )

    async def test_other_responses_are_not_reports(self) -> None:
        fake = _FakeTrvGateway()
        await fake.poll(1000)  # Baseline, so the changes below are seen as changes.

        # Changed values that are not status reports: a thermostat-style B20
        # response, then a B37 that does not decode. Neither restarts the wait.
        fake.set_response("42323000")
        await fake.poll(1100)
        fake.set_response(_hex("B37" + "9" * 40))
        await fake.poll(1200)

        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000 + REQUEST_AFTER)
        )

    async def test_skips_offline_trv(self) -> None:
        fake = _FakeTrvGateway()
        fake.payloads["trv_mini_1"]["sZDOInfo"]["OnlineStatus_i"] = 0

        self.assertEqual([], await fake.poll(1000))

    async def test_disabled_with_none(self) -> None:
        fake = _FakeTrvGateway(mini_trv_request_report_after=None)

        self.assertEqual([], await fake.poll(1000))
        self.assertEqual([], await fake.poll(1000 + 10 * REQUEST_AFTER))

    async def test_disabled_by_default(self) -> None:
        fake = _FakeTrvGateway()
        fake.gateway = IT600Gateway(
            host="192.0.2.10", euid="001E5E0D32906128", session=object()
        )
        fake.gateway._make_encrypted_request = fake._request  # type: ignore[method-assign]

        await fake.gateway.poll_status()

        self.assertEqual([], fake.commands)

    async def test_custom_request_report_after(self) -> None:
        fake = _FakeTrvGateway(mini_trv_request_report_after=60)
        await fake.poll(1000)

        self.assertEqual([], await fake.poll(1059))
        self.assertEqual([("trv_mini_1", STATUS_REQUEST)], await fake.poll(1060))

    async def test_requests_each_trv_independently(self) -> None:
        fake = _FakeTrvGateway()
        second = _mini_trv_payload()
        second["data"]["UniID"] = "trv_mini_2"
        fake.payloads["trv_mini_2"] = second
        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST), ("trv_mini_2", STATUS_REQUEST)],
            await fake.poll(1000),
        )

        # After the baseline poll, so only trv_mini_2 gets a new report.
        fake.set_response(_hex(SAMPLE_IDLE), "trv_mini_2")
        await fake.poll(1500)

        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000 + REQUEST_AFTER)
        )

    async def test_failed_request_does_not_fail_the_poll(self) -> None:
        fake = _FakeTrvGateway()
        fake.write_error = IT600ConnectionError("dropped")

        with self.assertLogs("salus_it600", level="DEBUG") as logs:
            self.assertEqual([("trv_mini_1", STATUS_REQUEST)], await fake.poll(1000))
            # Not retried on every poll, and repeats are logged at debug.
            self.assertEqual([], await fake.poll(1020))
            await fake.poll(1000 + REQUEST_AFTER)

        failures = [line for line in logs.output if "Could not ask" in line]
        self.assertEqual(2, len(failures))
        self.assertTrue(failures[0].startswith("WARNING"))
        self.assertTrue(failures[1].startswith("DEBUG"))
        self.assertIsNotNone(fake.gateway.get_binary_sensor_device("trv_mini_1"))

    async def test_skips_trv_while_a_command_sequence_holds_its_lock(self) -> None:
        fake = _FakeTrvGateway()
        await fake.poll(1000)

        async with fake.gateway._mini_trv_command_lock("trv_mini_1"):
            self.assertEqual([], await fake.poll(1000 + REQUEST_AFTER))

    async def test_mode_change_counts_as_a_request(self) -> None:
        fake = _FakeTrvGateway()
        await fake.poll(1000)
        fake.now = 1500

        with patch("salus_it600.gateway.asyncio.sleep", new=AsyncMock()):
            # Padded on purpose: the lock and state are keyed on the unique ID.
            await fake.gateway.set_mini_trv_mode(" trv_mini_1 ", MiniTrvMode.MANUAL_ON)

        self.assertEqual(("trv_mini_1", STATUS_REQUEST), fake.commands[-1])
        self.assertEqual([], await fake.poll(1000 + REQUEST_AFTER))
        self.assertEqual(
            [("trv_mini_1", STATUS_REQUEST)], await fake.poll(1500 + REQUEST_AFTER)
        )

    async def test_forgets_a_trv_that_disappears(self) -> None:
        fake = _FakeTrvGateway()
        payload = fake.payloads["trv_mini_1"]
        await fake.poll(1000)

        del fake.payloads["trv_mini_1"]
        await fake.poll(1100)
        fake.payloads["trv_mini_1"] = payload

        # Back with an unknown report age.
        self.assertEqual([("trv_mini_1", STATUS_REQUEST)], await fake.poll(1200))

    def test_rejects_invalid_request_report_after(self) -> None:
        for value, error in (
            (0, IT600ValidationError),
            (-1, IT600ValidationError),
            (float("nan"), IT600ValidationError),
            (True, TypeError),
            ("1800", TypeError),
        ):
            with self.subTest(value=value), self.assertRaises(error):
                IT600Gateway(
                    host="192.0.2.10",
                    euid="001E5E0D32906128",
                    session=object(),
                    mini_trv_request_report_after=value,  # type: ignore[arg-type]
                )


if __name__ == "__main__":
    unittest.main()
