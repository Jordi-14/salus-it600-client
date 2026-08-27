"""SQ610-family "Advanced Settings" blob decoder (read-only).

The vendor app's per-thermostat Advanced Settings screen (~28 fields: valve
protection, comfort warm floor, optimum start/stop, control algorithm, S1/S2
input, floor-temperature limits, relay configuration, minimum off times,
display/language/PIN options) has no named JSON fields in the local gateway
API. Every field is packed into a single 77-byte blob exposed twice on the
`sIT600TH` section, under two aliased keys that always carry identical
values: `Status_2_d` and `Schedule`. `Schedule` is a misleading legacy name;
the blob is not primarily schedule or timer data. The client reads
`Status_2_d` and falls back to `Schedule` for payloads that only carry the
legacy key.

Encoding: `byte = position / 2` into the 154-hex-char string. Each field's
hex characters are read as a decimal digit string, NOT as hexadecimal
(`"15"` is decimal 15, not 0x15 = 21). Multi-byte fields concatenate their
digit strings big-endian (`"1500"` -> 1500 -> 15.00 degC after /100).
Byte 0 is a constant `72` header.

The byte offsets were derived by live A/B toggling of individual settings in
the cloud app while diffing gateway captures of this blob, then confirmed
field-by-field against the settings-parsing table in the Salus cloud web
app's own compiled Flutter JS (`main.dart.js` keeps JSON string-literal keys
readable even when minified). The two methods cross-validated exactly on the
fields checked by hand.

Deliberately not decoded:

- Byte 1 is a save-sequence counter that increments on every settings write
  regardless of what changed; it is not thermostat state.
- Bytes 40-41 hold the thermostat PIN code, obfuscated against the save
  counter at byte 1 with an algorithm that was not fully reverse-engineered.
  Security-sensitive and unverified, so intentionally not decoded or
  exposed.
- Bytes 44 and 48-76 are outside the confirmed settings table (a gap byte,
  then the schedule/holiday-hold payload region and `ff` padding).

This module is read-only by design. No write/encode path is implemented:
the save-counter and PIN-obfuscation interactions with writes are not fully
understood, and a subtly wrong write could corrupt a live thermostat's
settings.
"""

from __future__ import annotations

from typing import Any

from ..const import TEMPERATURE_SCALE
from ..models import ThermostatAdvancedSettings

# The blob is a fixed 77-byte (154-hex-char) vendor firmware layout starting
# with a constant `72` header byte; anything else is not a known layout.
ADVANCED_SETTINGS_HEX_LENGTH = 154
ADVANCED_SETTINGS_HEADER = "72"

# Standby-cooling wire values meaning "Off" rather than a real temperature.
STANDBY_COOLING_OFF_VALUES = frozenset({"4050", "0450"})

_DECIMAL_DIGITS = frozenset("0123456789")

# Hex characters of blob bytes 3-4 (sign-magnitude temperature calibration).
_TEMPERATURE_CALIBRATION_SLICE = slice(6, 10)
_STANDBY_COOLING_BYTE = 8


def _field_chars(blob: str, byte_offset: int, byte_count: int = 1) -> str:
    """Return the raw hex characters of one blob field."""
    return blob[2 * byte_offset : 2 * (byte_offset + byte_count)]


def _int_field(blob: str, byte_offset: int, byte_count: int = 1) -> int | None:
    """Return one field read as a decimal digit string, or None."""
    chars = _field_chars(blob, byte_offset, byte_count)
    if not _DECIMAL_DIGITS.issuperset(chars):
        return None
    return int(chars)


def _flag_field(blob: str, byte_offset: int) -> bool | None:
    """Return one 0/1 field as a bool, or None for other values."""
    value = _int_field(blob, byte_offset)
    if value == 0:
        return False
    if value == 1:
        return True
    return None


def _temperature_field(blob: str, byte_offset: int) -> float | None:
    """Return one two-byte x100 temperature field in Celsius."""
    value = _int_field(blob, byte_offset, 2)
    return None if value is None else value / TEMPERATURE_SCALE


def _temperature_calibration(blob: str) -> float | None:
    """Return the sign-magnitude calibration at bytes 3-4 in Celsius.

    The first hex digit is a sign flag (`8` negative, `0` positive); the
    remaining three digits are the magnitude x100 (`8350` -> -3.5,
    `0050` -> +0.5).
    """
    chars = blob[_TEMPERATURE_CALIBRATION_SLICE]
    sign_digit, magnitude_chars = chars[0], chars[1:]
    if sign_digit not in "08" or not _DECIMAL_DIGITS.issuperset(magnitude_chars):
        return None
    magnitude = int(magnitude_chars) / TEMPERATURE_SCALE
    return -magnitude if sign_digit == "8" else magnitude


def _standby_cooling_setpoint(blob: str) -> float | None:
    """Return the standby cooling setpoint, or None when reported as Off."""
    if _field_chars(blob, _STANDBY_COOLING_BYTE, 2) in STANDBY_COOLING_OFF_VALUES:
        return None
    return _temperature_field(blob, _STANDBY_COOLING_BYTE)


def parse_advanced_settings(th: dict[str, Any]) -> ThermostatAdvancedSettings | None:
    """Parse the advanced-settings blob from an `sIT600TH` payload section.

    `Status_2_d` and `Schedule` are aliased duplicates of the same value on
    the wire; `Status_2_d` is preferred because the legacy `Schedule` name
    misdescribes the contents.
    """
    blob = th.get("Status_2_d")
    if not isinstance(blob, str):
        blob = th.get("Schedule")
    if not isinstance(blob, str) or len(blob) != ADVANCED_SETTINGS_HEX_LENGTH:
        return None
    if not blob.startswith(ADVANCED_SETTINGS_HEADER):
        return None

    # Byte offsets follow the table in the module docstring and
    # docs/device-protocol.md; fields are listed in wire byte order.
    return ThermostatAdvancedSettings(
        display_time_on_lcd=_flag_field(blob, 2),
        temperature_calibration=_temperature_calibration(blob),
        display_humidity_on_lcd=_flag_field(blob, 5),
        standby_heating_setpoint=_temperature_field(blob, 6),
        standby_cooling_setpoint=_standby_cooling_setpoint(blob),
        temperature_display_unit=_int_field(blob, 10),
        display_resolution=_int_field(blob, 11),
        control_algorithm=_int_field(blob, 12),
        cooling_control_span=_int_field(blob, 13),
        trv_calibration_mode=_int_field(blob, 14),
        s1_s2_function=_int_field(blob, 15),
        max_floor_temp_heating=_temperature_field(blob, 16),
        min_floor_temp_heating=_temperature_field(blob, 18),
        min_floor_temp_cooling=_temperature_field(blob, 20),
        max_heating_setpoint=_temperature_field(blob, 22),
        min_heating_setpoint=_temperature_field(blob, 24),
        max_cooling_setpoint=_temperature_field(blob, 26),
        min_cooling_setpoint=_temperature_field(blob, 28),
        valve_protection=_flag_field(blob, 30),
        internal_relay_function=_int_field(blob, 31),
        relay_contact_type=_int_field(blob, 32),
        min_off_time_heating=_int_field(blob, 33, 2),
        min_off_time_cooling=_int_field(blob, 35, 2),
        optimum_start=_flag_field(blob, 37),
        optimum_stop=_flag_field(blob, 38),
        comfort_warm_floor=_int_field(blob, 39),
        language=_int_field(blob, 42),
        pin_required_to_unlock=_flag_field(blob, 43),
        display_floor_temperature_on_lcd=_flag_field(blob, 45),
        unlock_from_thermostat_enabled=_flag_field(blob, 46),
        adjust_setpoint_when_locked_allowed=_flag_field(blob, 47),
    )
