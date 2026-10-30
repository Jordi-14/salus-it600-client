"""it600MINITRV report decoding.

The it600MINITRV is a slave actuator: it has no `sIT600TH`/`sTherS` block, so
the gateway reports no temperature or setpoint for it in named fields. The
TRV's own temperature reading, which the vendor app shows, is only available
packed into `sIT600I.CommandResponse_d`.

`CommandResponse_d` is an ASCII string encoded as hex. Once decoded, the last
three 4-digit decimal groups before the first `@` are temperatures x100, in
this order: the paired thermostat's temperature, the TRV's own temperature,
and the setpoint. For example::

    B37A1B2 4000000010020 0328 4068 1820 2025 1850 @ 320236FF...

(spaces added) decodes to thermostat 18.20, TRV 20.25 and setpoint 18.50,
which was checked against the vendor app (which rounds to 0.5 degrees). The
whole section before the first `@` must have this shape (`B37`, a 4-character hex
short address, 13 status digits, the valve position,
an undecoded 4-digit group and the three temperatures), and at least 16 hex
characters must follow the `@`.

The valve position, at characters 20-23, runs from about 0 (closed) to about
2240 (open). Each character is `'0' + n`, so when the motor goes slightly past
closed, the last one drops below `0` in ASCII: `*` is -6 and `.` is -2. It is
checked for shape here but not decoded.

`B37` identifies the report as the reply to the status request written to
`sIT600I.SetCommand_d`; the vendor app checks for the same prefix. The field also
carries other responses, such as `B20` from a thermostat.

An unpaired TRV (characters 3-6 are `FFFF`, the unpaired short address) uses a
different layout with no `@`. Its own temperature is the 4-digit group at
character 28, written twice in a row, with no thermostat temperature or
setpoint::

    B37FFFF 0000000000000 0002 4074 2418 2418 1500022032600000000

(spaces added) decodes to TRV 24.18, which matched the vendor app across a
falling series of samples. The position matters: at 24.94 the string holds
`...4 2494 2494 1...`, which also contains the repeat `4249 4249` one
character earlier. The characters around the reading are not decoded, but must
be present in full.

Anything else, including a string that merely contains a plausible-looking
group of digits, is rejected rather than searched for a reading.
"""

from __future__ import annotations

import string
from typing import Any, NamedTuple

from ..const import TEMPERATURE_SCALE

# Fields shared by both layouts, as positions in the decoded string.
_RESPONSE_ID = "B37"
_SHORT_ID = slice(3, 7)
_STATUS = slice(7, 20)
_VALVE_POSITION_LEADING = slice(20, 23)
_VALVE_POSITION_LAST = 23  # Not always a digit; see the module docstring.
_UNDECODED = slice(24, 28)

# Paired layout.
_THERMOSTAT_TEMPERATURE = slice(28, 32)
_TRV_TEMPERATURE = slice(32, 36)
_SETPOINT = slice(36, 40)
_SEPARATOR = "@"
_SEPARATOR_INDEX = 40
_PAIRED_TAIL = slice(41, None)
_MIN_PAIRED_TAIL_LENGTH = 16

# Unpaired layout.
_UNPAIRED_SHORT_ID = "FFFF"
_READING = slice(28, 32)
_READING_REPEAT = slice(32, 36)
_UNPAIRED_TAIL = slice(36, None)
_MIN_UNPAIRED_TAIL_LENGTH = 19

# A TRV temperature outside this range is treated as a decoding error rather
# than a reading. The upper bound is far above any room temperature but still
# rejects the larger values a misaligned 4-digit group would produce.
_MIN_TRV_TEMPERATURE = 0.0
_MAX_TRV_TEMPERATURE = 60.0


class MiniTrvReport(NamedTuple):
    """Temperatures decoded from an it600MINITRV `CommandResponse_d`."""

    thermostat_temperature: float | None
    trv_temperature: float
    setpoint: float | None


def _plausible(temperature: float) -> bool:
    return _MIN_TRV_TEMPERATURE < temperature <= _MAX_TRV_TEMPERATURE


def _is_hex(text: str) -> bool:
    return all(character in string.hexdigits for character in text)


def _temperature(text: str) -> float:
    return int(text) / TEMPERATURE_SCALE


def _has_common_fields(text: str) -> bool:
    """Return whether the fields shared by both layouts are well formed."""
    return (
        len(text) >= _UNDECODED.stop
        and text.startswith(_RESPONSE_ID)
        and _is_hex(text[_SHORT_ID])
        and text[_STATUS].isdigit()
        and text[_VALVE_POSITION_LEADING].isdigit()
        and text[_VALVE_POSITION_LAST].isprintable()
        and text[_UNDECODED].isdigit()
    )


def _decode_paired(text: str) -> MiniTrvReport | None:
    """Return the temperatures from a paired TRV's report."""
    thermostat = text[_THERMOSTAT_TEMPERATURE]
    trv = text[_TRV_TEMPERATURE]
    setpoint = text[_SETPOINT]
    tail = text[_PAIRED_TAIL]
    if (
        not _has_common_fields(text)
        or not thermostat.isdigit()
        or not trv.isdigit()
        or not setpoint.isdigit()
        or len(tail) < _MIN_PAIRED_TAIL_LENGTH
        or not _is_hex(tail)
        or not _plausible(_temperature(trv))
    ):
        return None
    return MiniTrvReport(
        thermostat_temperature=_temperature(thermostat),
        trv_temperature=_temperature(trv),
        setpoint=_temperature(setpoint),
    )


def _decode_unpaired(text: str) -> MiniTrvReport | None:
    """Return the TRV temperature from an unpaired TRV's report."""
    reading = text[_READING]
    tail = text[_UNPAIRED_TAIL]
    if (
        not _has_common_fields(text)
        or text[_SHORT_ID].upper() != _UNPAIRED_SHORT_ID
        or not reading.isdigit()
        or text[_READING_REPEAT] != reading
        or len(tail) < _MIN_UNPAIRED_TAIL_LENGTH
        or not _is_hex(tail)
        or not _plausible(_temperature(reading))
    ):
        return None
    return MiniTrvReport(
        thermostat_temperature=None,
        trv_temperature=_temperature(reading),
        setpoint=None,
    )


def decode_mini_trv_report(value: Any) -> MiniTrvReport | None:
    """Decode the temperatures packed into `sIT600I.CommandResponse_d`.

    Returns None when the value is missing, is not hex-encoded ASCII, does not
    have the full paired (first `@` at index 40) or unpaired (no `@`) layout, or
    holds an implausible TRV temperature.
    """
    if not isinstance(value, str) or not value:
        return None

    try:
        text = bytes.fromhex(value).decode("ascii")
    except ValueError:
        # Covers both invalid hex and UnicodeDecodeError.
        return None

    separator_index = text.find(_SEPARATOR)
    if separator_index == _SEPARATOR_INDEX:
        return _decode_paired(text)
    if separator_index == -1:
        return _decode_unpaired(text)
    return None
